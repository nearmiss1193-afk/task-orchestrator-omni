import { GHLConnector } from './connectors/ghl';
import { GoogleGenerativeAI } from '@google/generative-ai';
import puppeteer from 'puppeteer';

/**
 * FunnelOptimizer analyzes GHL funnel pages and proposes/implements UI code changes.
 */
export class FunnelOptimizer {
    private ghl = new GHLConnector();
    private genAI: any;
    private model: any;

    constructor() {
        const apiKey = process.env.GOOGLE_API_KEY;
        if (apiKey) {
            this.genAI = new GoogleGenerativeAI(apiKey);
            this.model = this.genAI.getGenerativeModel({ model: 'gemma-3-27b-it' });
        }
    }

    /**
     * Scrapes a funnel page, analyzes UI/UX, and generates optimized HTML/CSS.
     */
    async optimizePage(url: string) {
        console.log(`[Optimizer] Analyzing funnel page: ${url}...`);

        const browser = await puppeteer.launch({ headless: "new" });
        const page = await browser.newPage();

        try {
            await page.goto(url, { waitUntil: 'networkidle2' });

            // 1. Capture Page Structure & Visual Elements
            const pageData = await page.evaluate(() => {
                return {
                    title: document.title,
                    h1: document.querySelector('h1')?.innerText,
                    buttons: Array.from(document.querySelectorAll('button')).map(b => b.innerText),
                    forms: document.querySelectorAll('form').length
                };
            });

            // 2. AI Analysis & Improvement Proposal
            const prompt = `
                You are a world-class CRO (Conversion Rate Optimization) expert for GHL funnels.
                Page Data: ${JSON.stringify(pageData)}
                Goal: Improve conversion for 'AI Service Co' landing page.
                
                Analyze the current elements. Propose 3 major UI/UX improvements.
                Then, provide a block of Custom CSS/JS that can be injected into GHL 
                to make the 'Call to Action' buttons more vibrant and add a smooth scroll effect.
            `;

            const result = await this.model.generateContent(prompt);
            const optimization = result.response.text();

            console.log('[Optimizer] Optimization proposal generated.');
            return { success: true, optimization };

        } catch (error: any) {
            console.error('[Optimizer] Error:', error.message);
            throw error;
        } finally {
            await browser.close();
        }
    }
}
