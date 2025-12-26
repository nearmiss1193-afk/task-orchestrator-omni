import { GHLConnector } from './connectors/ghl';
import { GoogleGenerativeAI } from '@google/generative-ai';

/**
 * ConciergeAgent handles appointment booking and calendar coordination.
 */
export class ConciergeAgent {
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
     * Checks calendar availability and proposes slots to a lead.
     */
    async handleBooking(lead: any, calendarId: string) {
        console.log(`[Concierge] Handling booking for ${lead.email}...`);

        try {
            // 1. Get available slots for the next 7 days
            const startDate = new Date().toISOString();
            const endDate = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString();

            const slots = await this.ghl.execute('get_calendar_availability', {
                calendarId,
                startDate,
                endDate
            });

            if (!slots || slots.length === 0) {
                console.log('[Concierge] No free slots found.');
                return { success: false, reason: 'no_slots' };
            }

            // 2. Pick top 3 slots
            const topSlots = slots.slice(0, 3).map((s: any) => s.startTime);

            // 3. Generate a personalized booking message
            const prompt = `
                You are a professional concierge for 'AI Service Co'. 
                Lead: ${lead.full_name || lead.email}
                Context: They recently expressed interest in our AI automation services.
                Available Slots: ${topSlots.join(', ')}

                Write a short, friendly SMS/Email inviting them to book a 15-minute 
                strategy call. Present the 3 slots and ask which works best.
                Be concise and high-energy.
            `;

            const result = await this.model.generateContent(prompt);
            const message = result.response.text();

            // 4. Send the message via GHL
            await this.ghl.execute('send_sms', {
                to: lead.phone || lead.email,
                body: message,
                contactId: lead.ghl_contact_id
            });

            console.log('[Concierge] Booking invitation sent.');
            return { success: true, slots: topSlots };

        } catch (error: any) {
            console.error('[Concierge] Error:', error.message);
            throw error;
        }
    }
}
