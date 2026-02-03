import { supabase } from './supabase';
import { GHLConnector } from './connectors/ghl';

/**
 * GHLSyncEngine handles the Two-Way synchronization between 
 * GoHighLevel and the Supabase `contacts_master` table.
 */
export class GHLSyncEngine {
    private ghl = new GHLConnector();

    /**
     * Synchronizes a GHL contact payload into the `contacts_master` table.
     * Uses UPSERT based on the `ghl_contact_id`.
     */
    async syncContact(ghlPayload: any) {
        console.log(`[SyncEngine] Processing payload for: ${ghlPayload.email || 'unknown email'}`);

        const contactId = ghlPayload.id || ghlPayload.contact_id || ghlPayload.ghl_contact_id;

        if (!contactId) {
            console.warn('[SyncEngine] No GHL Contact ID found in payload.');
            // If contactId is missing, we try to use email as a fallback for the system
            if (!ghlPayload.email) throw new Error("GHL Contact ID or Email missing from payload");
        }

        const contactData: any = {
            ghl_contact_id: contactId || `temp_${Date.now()}`,
            full_name: ghlPayload.full_name || `${ghlPayload.first_name || ''} ${ghlPayload.last_name || ''}`.trim(),
            email: ghlPayload.email,
            phone: ghlPayload.phone || ghlPayload.phone_number,
            website_url: ghlPayload.website || ghlPayload.website_url,
            status: ghlPayload.status || 'new',
            sentiment: ghlPayload.sentiment || 'neutral',
            lead_score: ghlPayload.lead_score || 0
        };

        // Clean up empty strings
        Object.keys(contactData).forEach(key => {
            if (contactData[key] === '') contactData[key] = null;
        });

        const { data, error } = await supabase
            .from('contacts_master')
            .upsert(contactData, { onConflict: 'ghl_contact_id' })
            .select();

        if (error) {
            console.error('[SyncEngine] Supabase Save Error:', error.message);
            throw error;
        }

        console.log(`[SyncEngine] Successfully synced contact: ${contactId}`);
        return data;
    }

    /**
     * Verifies the GHL API connection by attempting to list forms.
     */
    async verifyGHLConnection() {
        try {
            const forms = await this.ghl.execute('get_forms', {});
            return {
                connected: true,
                formCount: forms.length,
                message: `Successfully connected to GHL. Found ${forms.length} forms.`
            };
        } catch (e: any) {
            return {
                connected: false,
                error: e.message
            };
        }
    }
}
