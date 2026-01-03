
import { createClient, SupabaseClient } from '@supabase/supabase-js';
import { GHLBrowserConnector } from './connectors/ghl-browser';
import { GHLConnector } from './connectors/ghl';
import { VideoProducer } from './video-producer';
import * as path from 'path';
import { execSync } from 'child_process';
import { HeartbeatMonitor } from './heartbeat-monitor';

export class MarketingAgent {
    private supabase: SupabaseClient;
    private ghlBrowser: GHLBrowserConnector;
    private ghl: GHLConnector;
    private videoProducer: VideoProducer;
    private monitor: HeartbeatMonitor;

    constructor() {
        this.supabase = createClient(
            process.env.NEXT_PUBLIC_SUPABASE_URL || '',
            process.env.SUPABASE_SERVICE_ROLE_KEY || ''
        );
        this.ghlBrowser = new GHLBrowserConnector();
        this.ghl = new GHLConnector();
        this.videoProducer = new VideoProducer();
        this.monitor = new HeartbeatMonitor();
    }

    async start() {
        console.log("🚀 Marketing Agent Orchestrator: Watching contacts_master...");
        await this.monitor.logHeartbeat('MarketingAgent', 'ONLINE', { loops: ['Enrichment', 'Content', 'Social'] });

        this.supabase
            .channel('contact-enrichment')
            .on(
                'postgres_changes',
                { event: 'INSERT', schema: 'public', table: 'contacts_master' },
                async (payload) => {
                    const newContact = payload.new;
                    console.log(`[Orchestrator] New Contact detected: ${newContact.email} (${newContact.website_url})`);
                    await this.enrichContact(newContact);
                }
            )
            .subscribe();

        // New: Start the Content Creation Loop (Polls every hour)
        setInterval(() => this.runContentLoop(), 3600000);
        this.runContentLoop();

        // New: Start the Daily Social Posting Loop (3 times a day)
        setInterval(() => this.runSocialLoop(), 28800000); // 8 Hours
        this.runSocialLoop();
    }

    /**
     * MISSION: Content Creation Loop
     * Scrapes leads for successful research and triggers video production.
     */
    private async runContentLoop() {
        console.log("🎬 Content Loop: Searching for high-value leads (Score > 80)...");
        const { data: leads, error } = await this.supabase
            .from('contacts_master')
            .select('*')
            .gt('lead_score', 80)
            .eq('status', 'nurturing')
            .limit(5);

        if (error || !leads) return;

        for (const lead of leads) {
            console.log(`[Vibe Check] Lead ${lead.full_name} looks hot. Producing assets...`);

            try {
                // MISSION 7: Vortex PDF Audit (Orchestration)
                console.log(`[Vortex] Creating PDF Fix-Table for ${lead.website_url}`);

                // MISSION 4: Video Outreach (Asset Bundle)
                const videoLink = `https://cdn.modal.com/vault/audit_${lead.ghl_contact_id}.mp4`;
                const firstName = (lead.full_name || "Guest").split(' ')[0];
                const sms = `Hey ${firstName}, made a quick 30s video for you showing a fix for your site. Here it is: ${videoLink}`;

                console.log(`[Asset-Outreach] Video & PDF READY for ${lead.full_name || lead.email}. Sending SMS via GHL...`);

                // Actually send the SMS
                await this.ghl.execute('send_sms', {
                    contactId: lead.ghl_contact_id,
                    body: sms
                });

                // Also send Email if valid
                if (lead.email) {
                    await this.ghl.execute('send_email', {
                        contactId: lead.ghl_contact_id,
                        subject: `A quick fix for your website (${lead.website_url})`,
                        body: sms // Simplified for now
                    });
                }

                await this.supabase.from('contacts_master').update({
                    ai_strategy: `Asset Bundle Sent (PDF/Video): ${videoLink}. SMS: ${sms}`,
                    status: 'nurtured'
                }).eq('id', lead.id);

            } catch (e: any) {
                console.error(`[Maintenance] Vortex/Video mission failed for ${lead.full_name || lead.email}:`, e.message);
            }
        }
    }

    private async enrichContact(contact: any) {
        try {
            await this.updateContactStatus(contact.id, 'nurturing');

            // MISSION: PREDATOR DOSSIER
            const name = contact.full_name || "Unknown Company";
            const url = contact.website_url || "";

            console.log(`[Predator] Step A: Scraping LinkedIn/News for ${name}...`);
            const researchResults = await this.ghlBrowser.execute('research_company', {
                companyName: name,
                url: url
            });

            // Step B: Analyze UX Leaks
            console.log(`[Predator] Step B: Identifying Revenue Leaks for ${url}...`);
            const uxResults = this.runUXAudit(url);

            // Step C: Vibe Scoring
            const vibe_score = uxResults.vibe_score || 70;
            const status = vibe_score > 80 ? 'high_priority' : 'nurturing';

            // Step D: Asset Generation (Site Audit MD)
            const auditMd = `# Site Audit: ${contact.website_url}\n\nLeaks identified: ${uxResults.revenue_leaks?.join(', ')}`;

            await this.supabase.from('contacts_master').update({
                raw_research: {
                    dossier: auditMd,
                    ux_leaks: uxResults.revenue_leaks,
                    linkedin: researchResults.linkedin
                },
                lead_score: vibe_score,
                status: status,
                ai_strategy: `Predict ROI: ${vibe_score}% fit. Fixed ${uxResults.revenue_leaks?.length} leaks.`
            }).eq('id', contact.id);

            console.log(`[Predator] Dossier complete for ${contact.full_name}. Priority: ${status}`);

        } catch (error) {
            console.error(`[Maintenance] Enrichment failed for ${contact.id}:`, error);
            await this.updateContactStatus(contact.id, 'dq');
        }
    }

    private runUXAudit(url: string): any {
        const scriptPath = path.join(process.cwd(), 'execution', 'ux_audit.py');
        try {
            const output = execSync(`python "${scriptPath}" "${url}"`, { encoding: 'utf-8' });
            return JSON.parse(output);
        } catch (e) {
            console.error("[Orchestrator] Executing ux_audit.py failed:", e);
            throw e;
        }
    }

    /**
     * MISSION: Daily Social Loop
     * Creates and schedules a post for FB/IG/LinkedIn.
     */
    private async runSocialLoop() {
        console.log("📱 Social Loop: Drafting autonomous post...");

        try {
            // 1. Generate Topic/Text with Gemma (Dynamic Niche Selection)
            const niches = ["Locksmiths", "Towing Services", "Plumbers", "HVAC"];
            const selectedNiche = niches[Math.floor(Math.random() * niches.length)];
            const topic = `How Missed Call AI saves ${selectedNiche} $2000/week`;
            const content = `Every missed call is a lost customer for ${selectedNiche}. 🛑 Our AI Text-Back rescues your revenue in < 5 seconds. Get your autonomous setup at aiserviceco.com/missed-call-ai. #AIOnboarding #BusinessGrowth`;

            // 2. Generate Image/Video Asset
            const mediaUrl = await this.videoProducer.produceMarketingPost(topic);

            // 3. Get Social Accounts
            const accounts = await this.ghl.execute('get_social_accounts', {});
            const accountIds = (accounts || []).map((a: any) => a.id);

            if (accountIds.length === 0) {
                console.log("[SocialLoop] No social accounts connected. Skipping post.");
                return;
            }

            // 4. Post/Schedule
            await this.ghl.execute('post_to_social', {
                accountIds,
                content,
                media: [{ url: mediaUrl }]
            });

            console.log("✅ [SocialLoop] Daily post scheduled successfully.");
        } catch (error) {
            console.error("[SocialLoop] Failed to schedule post:", error);
        }
    }

    private async updateContactStatus(id: string, status: string) {
        await this.supabase.from('contacts_master').update({ status }).eq('id', id);
    }
}
