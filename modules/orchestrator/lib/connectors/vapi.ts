import axios from 'axios';

export interface VapiCallPayload {
    customer_number: string;
    assistant_id?: string;
    context?: Record<string, any>;
}

export class VapiConnector {
    private apiKey: string;
    private baseUrl: string = 'https://api.vapi.ai';

    constructor() {
        this.apiKey = process.env.VAPI_API_KEY || '';
        if (!this.apiKey) {
            console.warn("⚠️ [Vapi] Missing VAPI_API_KEY. Calls will be mocked.");
        }
    }

    /**
     * Initiates an outbound call to a lead.
     * @param payload Target phone number and context variables.
     */
    async makeCall(payload: VapiCallPayload): Promise<any> {
        console.log(`📞 [Vapi] Initiating call to ${payload.customer_number}...`);

        if (!this.apiKey) {
            return {
                id: `mock_call_${Date.now()}`,
                status: "queued (mock)",
                customer_number: payload.customer_number
            };
        }

        try {
            const response = await axios.post(`${this.baseUrl}/call/phone`, {
                customer: { number: payload.customer_number },
                assistantId: payload.assistant_id || process.env.VAPI_ASSISTANT_ID,
                assistantOverrides: {
                    variableValues: payload.context || {}
                }
            }, {
                headers: {
                    'Authorization': `Bearer ${this.apiKey}`,
                    'Content-Type': 'application/json'
                }
            });

            console.log(`✅ [Vapi] Call initiated. ID: ${response.data.id}`);
            return response.data;
        } catch (error: any) {
            console.error(`❌ [Vapi] Call failed: ${error.message}`);
            throw error;
        }
    }

    /**
     * Generates the System Prompt for the Spartan Appointment Setter.
     */
    getSpartanPrompt(leadName: string, company: string, neuralHook?: string): string {
        return `
        ROLE: "Spartan", Scale Specialist at Agency.
        TONE: Direct, Lowercase, Confident, Helpful (Not Pushy).
        OBJECTIVE: Book a 15-min Discovery Call to fix "Revenue Leaks".

        CONTEXT:
        - Lead Name: ${leadName}
        - Company: ${company}
        - Neural Hook: "${neuralHook || 'saw you hiring on indeed'}"

        SCRIPT FLOW:
        1. "hey ${leadName}, it's nick. ${neuralHook || 'saw you hiring'}. quick question - you handling those leads yourself or using a setter?"
        2. LISTEN.
        3. IF THEY HANDLE: "got it. reason i ask is i see you're missing about 30% of calls. costs you like 2k a week. we have a robot that fixes that instantly. open to seeing how?"
        4. OBJECTION ("send info"): "happy to. but the tech is visual. i can show you in 10 mins tomorrow. 10am or 2pm?"
        5. REFUSAL ("not interested"): "all good. i'll check back in 6 months when you're tired of manual follow-up. good luck."

        GUIDELINES:
        - Speak fast.
        - Don't apologize for calling.
        - If they hang up, do not call back immediately.
        `;
    }
}
