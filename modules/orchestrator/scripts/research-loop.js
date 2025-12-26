const { createClient } = require('@supabase/supabase-js');
const dotenv = require('dotenv');
const path = require('path');
const puppeteer = require('puppeteer');
const { GoogleGenerativeAI } = require("@google/generative-ai");

dotenv.config({ path: path.resolve(process.cwd(), '.env.local') });

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY;
const googleKey = process.env.GOOGLE_API_KEY;

const supabase = createClient(supabaseUrl, supabaseKey);

async function runResearchLoop() {
    console.log('--- STARTING RESEARCH LOOP (JS) ---');

    try {
        // 1. Fetch leads
        const { data: leads, error } = await supabase
            .from('leads')
            .select('*')
            .or('status.eq.new,personalized_copy.is.null');

        if (error) throw error;
        if (!leads || leads.length === 0) {
            console.log('No new leads found.');
            return;
        }

        console.log(`Found ${leads.length} leads.`);

        const genAI = new GoogleGenerativeAI(googleKey);
        const model = genAI.getGenerativeModel({ model: "gemma-3-27b-it" });

        for (const lead of leads) {
            console.log(`\nProcessing: ${lead.email}`);
            const url = lead.website_url;

            if (!url) continue;

            // 2. Scrape
            let text = "";
            try {
                const browser = await puppeteer.launch({ headless: "new" });
                const page = await browser.newPage();
                await page.goto(url, { waitUntil: 'networkidle2', timeout: 30000 });
                text = await page.evaluate(() => document.body.innerText);
                await browser.close();
            } catch (e) {
                console.error(`Scrape failed for ${url}:`, e.message);
            }

            if (!text) {
                console.log("No text extracted.");
                continue;
            }

            // 3. AI Personalization
            const prompt = `Write a short, professional 1-sentence sales opener for ${lead.email} based on their website content: ${text.substring(0, 2000)}`;
            const result = await model.generateContent(prompt);
            const proposal = result.response.text();

            // 4. Update
            const { error: updateError } = await supabase
                .from('leads')
                .update({
                    personalized_copy: proposal,
                    status: 'ready_to_send'
                })
                .eq('id', lead.id);

            if (updateError) console.error("Update Error:", updateError.message);
            else console.log(`[SUCCESS] Updated ${lead.email}`);
        }
    } catch (err) {
        console.error("Critical Error:", err.message);
    }
}

runResearchLoop();
