import puppeteer from 'puppeteer';
import { GoogleGenerativeAI } from '@google/generative-ai';

export class NeuralLink {
    private genAI: GoogleGenerativeAI;
    private model: any;

    constructor() {
        const apiKey = process.env.GOOGLE_API_KEY || '';
        this.genAI = new GoogleGenerativeAI(apiKey);
        this.model = this.genAI.getGenerativeModel({ model: 'gemini-1.5-flash' });
    }

    /**
     * Extracts activity from a LinkedIn profile and generates a hook.
     */
    async extractActivity(profileUrl: string): Promise<string> {
        console.log(`🧠 [NeuralLink] Analyzing LinkedIn: ${profileUrl}`);
        let browser;
        try {
            // Attempt to use a persistent profile to reuse login session
            // Note: This path might need adjustment based on where the app runs or if we want a dedicated profile
            const userDataDir = './.neural_link_profile';

            browser = await puppeteer.launch({
                headless: false, // Non-headless so we can see if login is needed
                args: ['--no-sandbox', '--disable-setuid-sandbox'],
                userDataDir: userDataDir
            });

            const page = await browser.newPage();
            // standard headers to look less bot-like
            await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36');

            // Normalize URL to activity tab
            const activityUrl = profileUrl.endsWith('/')
                ? `${profileUrl}recent-activity/all/`
                : `${profileUrl}/recent-activity/all/`;

            console.log(`Navigating to ${activityUrl}`);
            await page.goto(activityUrl, { waitUntil: 'domcontentloaded', timeout: 30000 });

            // Check if login is required
            if (page.url().includes('login') || page.url().includes('auth')) {
                console.warn('⚠️ LinkedIn Login Checkpoint detected. Interactive login might be required.');
                // Wait a bit to see if automation can proceed or if manual intervention handles it (if user is watching)
                // For a background agent, this is a failure point we'd flag.
                // We'll try to wait for a specific element that indicates logged in state, or just proceed best effort.
            }

            // Scroll to load some content
            await page.evaluate(async () => {
                window.scrollBy(0, 1000);
                await new Promise(r => setTimeout(r, 1000));
                window.scrollBy(0, 1000);
            });

            // Scrape feed content
            const feedText = await page.evaluate(() => {
                // Select feed items (adjust selectors as LinkedIn updates frequently)
                // This is a broad selector strategy to catch text content
                const items = Array.from(document.querySelectorAll('.feed-shared-update-v2__description, .feed-shared-text, .update-components-text'));
                return items.map(el => el.innerText).join('\n---\n');
            });

            if (!feedText || feedText.length < 50) {
                console.log('No recent activity found or selectors skipped.');
                return "noticed you're hiring for [job title] on indeed, congrats on the growth"; // Default fallback
            }

            // Analyze with AI
            return await this.generateHook(feedText);

        } catch (error: any) {
            console.error('Neural Link extraction failed:', error.message);
            return "noticed you're hiring for [job title] on indeed, congrats on the growth";
        } finally {
            if (browser) await browser.close();
        }
    }

    private async generateHook(activityText: string): Promise<string> {
        const prompt = `
        MISSION: Extract Neural Link.
        Activity Log: ${JSON.stringify(activityText.substring(0, 5000), null, 2)}
        
        Find ONE specific project, sports team, or alma mater they commented on in the last 14 days.
        Draft a 1-sentence opening hook: 'saw your comment on [topic], [short thought].'
        If no recent activity is found, default to: "noticed you're hiring for [job title] on indeed, congrats on the growth."
        `;

        try {
            const result = await this.model.generateContent(prompt);
            const text = result.response.text().trim();
            if (text.includes("DEFAULT")) {
                return "noticed you're hiring for [job title] on indeed, congrats on the growth";
            }
            return text;
        } catch (e) {
            return "noticed you're hiring for [job title] on indeed, congrats on the growth";
        }
    }
}
