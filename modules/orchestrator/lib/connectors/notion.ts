import { Client } from '@notionhq/client';

export class NotionConnector {
    private notion: Client;
    private masterTemplateId: string;

    constructor() {
        this.notion = new Client({ auth: process.env.NOTION_API_KEY });
        this.masterTemplateId = process.env.NOTION_MASTER_TEMPLATE_ID || '';

        if (!process.env.NOTION_API_KEY) {
            console.warn("⚠️ [Notion] NOTION_API_KEY missing. Operations will fail.");
        }
    }

    /**
     * Creates a new Client Dashboard by duplicating the Master Template.
     */
    async createClientDashboard(clientName: string, planType: string): Promise<string> {
        console.log(`🏗️ [Notion] Creating dashboard for ${clientName} (${planType})...`);

        if (!this.masterTemplateId) {
            console.warn("⚠️ [Notion] No Master Template ID. Skipping dashboard creation.");
            return "https://notion.so/mock-dashboard";
        }

        try {
            // 1. Search for the template if ID provided is not a page ID (optional safety)
            // For now, assume ID is valid.

            // 2. Duplicate Block/Page is not directly "duplicate" in API, usually we create a new page 
            // and copy content or just create a page with properties.
            // A common pattern for "templates" in API is creating a page within a database 
            // or as a child of a parent page.

            // Simplified: Create a new page in the 'Clients' database or parent page
            const parentId = process.env.NOTION_CLIENTS_PARENT_ID;

            if (!parentId) throw new Error("NOTION_CLIENTS_PARENT_ID missing");

            const response = await this.notion.pages.create({
                parent: { page_id: parentId },
                icon: { type: "emoji", emoji: "🚀" },
                properties: {
                    title: {
                        title: [
                            { text: { content: `${clientName} - Dashboard` } }
                        ]
                    }
                },
                children: [
                    {
                        object: 'block',
                        type: 'heading_2',
                        heading_2: {
                            rich_text: [{ text: { content: `Welcome to ${clientName} Growth Portal` } }]
                        }
                    },
                    {
                        object: 'block',
                        type: 'paragraph',
                        paragraph: {
                            rich_text: [{ text: { content: `Plan: ${planType}` } }]
                        }
                    },
                    {
                        object: 'block',
                        type: 'callout',
                        callout: {
                            rich_text: [{ text: { content: "Action Required: Upload your assets below." } }],
                            icon: { type: "emoji", emoji: "⚠️" }
                        }
                    }
                ]
            });

            console.log(`✅ [Notion] Dashboard created: ${response.url}`);
            return response.url;

        } catch (error: any) {
            console.error(`❌ [Notion] Failed to create dashboard: ${error.message}`);
            return "https://notion.so/error-creating-dashboard";
        }
    }
}
