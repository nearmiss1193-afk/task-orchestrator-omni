import puppeteer from 'puppeteer';
import { GoogleGenerativeAI } from '@google/generative-ai';

export class ResearchAgent {
    private genAI: GoogleGenerativeAI;
    private model: any;

    constructor() {
        const apiKey = process.env.GOOGLE_API_KEY || '';
        if (!apiKey) {
            console.warn('GOOGLE_API_KEY missing. AI generation will fail.');
        }
        this.genAI = new GoogleGenerativeAI(apiKey);
        // Using gemini-1.5-pro for high quality research and reasoning
        this.model = this.genAI.getGenerativeModel({ model: 'gemma-3-27b-it' });
    }

    /**
     * Scrapes a website and returns the main text content.
     */
    async scrapeWebsite(url: string): Promise<string> {
        console.log(`Scraping website: ${url}`);
        let browser;
        try {
            browser = await puppeteer.launch({
                headless: true,
                args: ['--no-sandbox', '--disable-setuid-sandbox']
            });
            const page = await browser.newPage();
            // Setting a reasonable timeout and waiting for network idle
            await page.goto(url, { waitUntil: 'networkidle2', timeout: 30000 });

            // Extract main text content
            const text = await page.evaluate(() => {
                // Remove scripts, styles, and other non-content elements
                const selectors = ['script', 'style', 'nav', 'footer', 'header', 'iframe', 'noscript'];
                selectors.forEach(selector => {
                    document.querySelectorAll(selector).forEach(el => el.remove());
                });
                return document.body.innerText.trim();
            });

            return text.substring(0, 5000); // Limit to 5000 chars for prompt safety
        } catch (error: any) {
            console.error(`Scraping failed for ${url}:`, error.message);
            return '';
        } finally {
            if (browser) await browser.close();
        }
    }

    /**
     * Generates a personalized proposal based on website content.
     */
    async generateProposal(websiteText: string): Promise<string> {
        if (!websiteText) return 'No website content found to analyze.';

        const prompt = `
        You are an expert AI Solution Consultant at "AI Service Co".
        
        PROJECT DIRECTIVES:
        - Tech Stack: Next.js, Tailwind, Supabase, GHL Webhooks.
        - Goal: Help businesses automate workflows and boost profit using AI.

        TASK:
        Based on the following scraped website content from a potential lead, write a brief, professional, and personalized 1-paragraph proposal.
        Point out a specific area where AI automation (like lead nurturing, AI chatbots, or automated follow-ups) could help their business specifically.
        
        STYLE:
        - Professional yet conversational.
        - Avoid empty buzzwords.
        - Focus on "Profit" and "Efficiency".
        - Mention "AI Service Co" as the provider.

        WEBSITE CONTENT:
        """
        ${websiteText}
        """

        PROPOSAL:
        `;

        try {
            const result = await this.model.generateContent(prompt);
            const response = await result.response;
            return response.text().trim();
        } catch (error: any) {
            console.error('AI Generation failed:', error.message);
            return 'AI Generation failed. Please review manually.';
        }
    }
}
