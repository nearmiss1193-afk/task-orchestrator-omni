
import { GHLBrowserConnector } from './connectors/ghl-browser';
import { createClient, SupabaseClient } from '@supabase/supabase-js';

export class SetupOnboardingAgent {
    private ghlBrowser: GHLBrowserConnector;
    private supabase: SupabaseClient;

    constructor() {
        this.ghlBrowser = new GHLBrowserConnector();
        this.supabase = createClient(
            process.env.NEXT_PUBLIC_SUPABASE_URL || '',
            process.env.SUPABASE_SERVICE_ROLE_KEY || ''
        );
    }

    /**
     * Triggered after payment verification.
     * Performs 100% autonomous setup in GHL.
     */
    async setupMissedCallEmpire(contactId: string, locationId: string) {
        console.log(`🚀 [SetupAgent] Initiating Autonomous Onboarding for Location: ${locationId}`);

        try {
            // 1. Configure GHL Settings
            const configResult = await this.ghlBrowser.execute('configure_missed_call', {
                message: "Hi! This is the AI assistant. Sorry we missed your call—we're out on a job right now. How can we help you? ☎️"
            });

            if (!configResult.success) throw new Error("GHL Configuration Failed");

            // 2. Log Success in Supabase
            await this.supabase.from('contacts_master').update({
                ai_strategy: "Onboarding Complete: Missed Call AI Active.",
                status: 'customer'
            }).eq('ghl_contact_id', contactId);

            console.log("✅ [SetupAgent] Onboarding Complete. Client is live.");
            return { success: true };

        } catch (error: any) {
            console.error(`❌ [SetupAgent] Onboarding Failed for ${contactId}:`, error.message);
            return { success: false, error: error.message };
        }
    }
}
