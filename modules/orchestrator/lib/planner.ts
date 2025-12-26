import { Plan, Step } from './types';
import { v4 as uuidv4 } from 'uuid';
import Anthropic from '@anthropic-ai/sdk';
import { GoogleGenerativeAI } from '@google/generative-ai';

export class Planner {
    private anthropic: Anthropic;
    private googleAI: GoogleGenerativeAI;

    constructor() {
        this.anthropic = new Anthropic({
            apiKey: process.env.ANTHROPIC_API_KEY,
        });
        this.googleAI = new GoogleGenerativeAI(process.env.GOOGLE_API_KEY || '');
    }

    async generatePlan(userInput: string): Promise<Plan> {
        const systemPrompt = `
You are an expert Task Planner for an automation agent.
Your goal is to parse natural language user instructions into a structured JSON plan.

AVAILABLE CONNECTORS AND ACTIONS:
1. "GHL" (GoHighLevel) - **CRM & Communications Hub**
   - Contacts:
     - "get_contact" (params: email OR phone)
     - "update_contact" (params: email/phone/contactId, firstName?, lastName?, customFields?)
     - "delete_contact" (params: email/phone/contactId)
     - "upsert_contact" (params: email, phone, firstName, lastName, customFields?)
     - "add_contact_tag" (params: email/phone/contactId, tags OR tag)
     - "remove_contact_tag" (params: email/phone/contactId, tags OR tag)
     - "add_contact_note" (params: email/phone/contactId, note OR body)
   - Opportunities:
     - "create_opportunity" (params: title, contactId?, monetaryValue?)
     - "update_opportunity" (params: opportunityId, title?, status?, monetaryValue?)
     - "delete_opportunity" (params: opportunityId)
     - "update_opportunity_status" (params: opportunityId, status)
     - "get_pipelines" (params: none)
     - "get_pipeline_stages" (params: pipelineId)
   - Calendar & Appointments:
     - "create_appointment" (params: email/phone/contactId, calendarId, startTime, endTime, title?, status?)
     - "update_appointment" (params: appointmentId, startTime?, endTime?, title?, status?)
     - "delete_appointment" (params: appointmentId)
     - "get_appointments" (params: startDate?, endDate?, calendarId?)
     - "get_calendar_availability" (params: calendarId, startDate, endDate, timezone?)
     - "get_calendars" (params: none)
   - Tasks:
     - "create_task" (params: email/phone/contactId, title, body?, dueDate?, assignedTo?)
     - "update_task" (params: taskId, title?, body?, dueDate?, assignedTo?)
     - "complete_task" (params: taskId)
     - "delete_task" (params: taskId)
     - "get_tasks" (params: email/phone/contactId)
   - Workflows & Automation:
     - "trigger_workflow" (params: email/phone/contactId, workflowId, eventStartTime?)
     - "add_contact_to_workflow" (params: email/phone/contactId, workflowId)
     - "remove_contact_from_workflow" (params: email/phone/contactId, workflowId)
   - Forms & Surveys:
     - "get_forms" (params: none)
     - "get_form_submissions" (params: formId, startDate?, endDate?, limit?)
     - "get_surveys" (params: none)
     - "get_survey_submissions" (params: surveyId, startDate?, endDate?, limit?)
   - Custom Fields:
     - "get_custom_fields" (params: none)
     - "update_custom_field" (params: email/phone/contactId, customField, value)
   - Payments & Analytics:
     - "get_transactions" (params: startDate?, endDate?, limit?)
     - "create_subscription" (params: email/phone/contactId, priceId, paymentMode?, quantity?)
     - "get_location_analytics" (params: none)
     - **BROWSER AUTOMATION ONLY**:
     - "create_funnel_page" (params: name, templateId?)
     - "update_workflow_visual" (params: workflowId, actions=[])
     - "upload_media" (params: filePath)
     - "audit_account" (params: none)
   - Communications:
     - "send_email" (params: to, subject, body)
     - "send_sms" (params: to, body)
2. "GoogleMaps" (Use this for "Google", "Zillow", "Leads", or "Search" requests)
   - actions: "search_leads" (params: query) -> returns list of objects with {name, phone, email}
3. "Facebook"
   - actions: "schedule_post" (params: content, time)
4. "Report"
   - actions: "generate_report" (params: type="performance") -> Aggregates all task results.

RULES:
- **CRITICAL**: FOR "landing page", "funnel", or "website" requests: ALWAYS use "create_funnel_page" (GHL connector). NEVER use create_opportunity for this.
- FOR "audit" or "scan" requests: ALWAYS use "audit_account" (GHL connector).
- FOR EMAILING OR TEXTING: ALWAYS use the "GHL" connector. Do NOT invent an "Email" connector.
- ALWAYS add a "Report" step at the end if the user asks for performance reporting.
- **CRITICAL**: Use simple sequential IDs: "step_1", "step_2", etc. NEVER use descriptive IDs like "step_zillow_1" or "step_email".
- If a step needs data from a previous step, use the {{ step_id.result.field }} syntax.
- **EMAIL RULE**: 
  - For "Marketing", "Leads", "Clients", or "Funnel" emails: MUST USE 'GHL' connector ('send_email').
  - For "Admin", "Notification", "Backup", or "System" emails: MUST USE 'Email' connector ('send_email').
- **VERIFICATION RULE**: Always add a final step to 'Report' connector ('generate_report') to confirm execution.
- Return ONLY valid JSON.

EXAMPLE PLAN:
User: "Build a funnel page called 'Offer' and email the link to leads found on Google"
JSON:
{
  "steps": [
    { "id": "step_1", "connectorName": "GHL", "action": "create_funnel_page", "params": { "name": "Offer" } },
    { "id": "step_2", "connectorName": "GoogleMaps", "action": "search_leads", "params": { "query": "leads" } },
    { "id": "step_3", "connectorName": "GHL", "action": "send_email", "params": { "to": "{{step_2.result[*].email}}", "body": "Link: {{step_1.result.funnelId}}" }, "dependsOn": ["step_1", "step_2"] }
  ]
}
`;

        const model = this.googleAI.getGenerativeModel({
            model: "gemini-2.5-pro",
            generationConfig: { responseMimeType: "application/json" }
        });

        let text = '';
        try {
            let retries = 3;
            while (retries > 0) {
                try {
                    const result = await model.generateContent({
                        contents: [{ role: "user", parts: [{ text: systemPrompt + `\n\nCreate a plan for this instruction: "${userInput}"` }] }]
                    });
                    const response = await result.response;
                    text = response.text();
                    break;
                } catch (err: any) {
                    if (err.message?.includes('429') && retries > 1) {
                        const delay = 10000 + Math.random() * 5000;
                        console.log(`[Planner] Rate limited (429). Retrying in ${Math.round(delay / 1000)}s... (${retries - 1} left)`);
                        await new Promise(resolve => setTimeout(resolve, delay));
                        retries--;
                        continue;
                    }
                    throw err;
                }
            }
        } catch (apiError) {
            console.error("[Planner] Critical API Failure:", apiError);
            console.log("Activitating Fallback Protocol: Generating Mock Plan for Demo");
            return this.generateMockPlan(userInput);
        }

        try {
            let jsonStr = text;

            // Cleanup any markdown blocks if the model ignore the "No markdown" rule
            jsonStr = jsonStr.replace(/```json\n?|\n?```/g, '').trim();

            // Find the first '{' and last '}' to handle potential preamble/postscript
            const startIndex = jsonStr.indexOf('{');
            const endIndex = jsonStr.lastIndexOf('}');
            if (startIndex !== -1 && endIndex !== -1) {
                jsonStr = jsonStr.substring(startIndex, endIndex + 1);
            }

            const data = JSON.parse(jsonStr);

            const planId = uuidv4();
            const steps: Step[] = data.steps.map((s: any) => ({
                ...s,
                status: 'PENDING',
                attempts: 0
            }));

            // POST-PROCESSING: SANITIZE STEP IDs
            const idMap: Record<string, string> = {};
            steps.forEach((step, index) => {
                const newId = `step_${index + 1}`;
                if (step.id !== newId) {
                    idMap[step.id] = newId;
                    step.id = newId;
                }
            });

            // Update references in params and dependsOn
            steps.forEach(step => {
                if (step.dependsOn) {
                    step.dependsOn = step.dependsOn.map(oldDep => idMap[oldDep] || oldDep);
                }

                const updateParams = (obj: any) => {
                    for (const key in obj) {
                        if (typeof obj[key] === 'string') {
                            let val = obj[key] as string;
                            Object.keys(idMap).sort((a, b) => b.length - a.length).forEach(oldId => {
                                if (val.includes(`{{${oldId}.`)) {
                                    val = val.replace(new RegExp(`{{${oldId}\\.`, 'g'), `{{${idMap[oldId]}.`);
                                }
                            });
                            obj[key] = val;
                        } else if (typeof obj[key] === 'object' && obj[key] !== null) {
                            updateParams(obj[key]);
                        }
                    }
                };
                if (step.params) {
                    updateParams(step.params);
                }
            });

            // POST-PROCESSING: FORCE FUNNEL CREATION (Browser Action)
            const lowerInput = userInput.toLowerCase();
            const hasLandingPageIntent = lowerInput.includes('funnel') || lowerInput.includes('landing') || lowerInput.includes('website');
            const hasFunnelStep = steps.some(s => s.action === 'create_funnel_page');
            const hasAuditIntent = lowerInput.includes('audit') || lowerInput.includes('check');

            if (hasLandingPageIntent && !hasFunnelStep) {
                console.log("[Planner] LLM Plan missing crucial Funnel Step. FALLING BACK to Deterministic Plan.");
                return this.generateMockPlan(userInput);
            }

            return {
                id: planId,
                originalGoal: userInput,
                steps,
                createdAt: new Date().toISOString(),
                status: 'PENDING'
            };

        } catch (error: any) {
            console.error("Failed to parse plan from LLM:", error);

            // Fallback to Mock Plan if API fails
            console.log("Falling back to Mock Plan due to API Error");
            return this.generateMockPlan(userInput);
        }
    }

    public generateMockPlan(userInput: string): Plan {
        const planId = uuidv4();
        const steps: Step[] = [];
        const lowerInput = userInput.toLowerCase();
        let stepCount = 1;

        // 0. Audit (If requested)
        if (lowerInput.includes('audit') || lowerInput.includes('scan') || lowerInput.includes('check')) {
            steps.push({
                id: `step_${stepCount++}`,
                connectorName: 'GHL',
                action: 'audit_account',
                params: {},
                status: 'PENDING',
                attempts: 0
            });
        }

        // 1. Landing Page / Funnel (Browser Action)
        if (lowerInput.includes('funnel') || lowerInput.includes('landing') || lowerInput.includes('website') || lowerInput.includes('page')) {
            steps.push({
                id: `step_${stepCount++}`,
                connectorName: 'GHL',
                action: 'create_funnel_page', // This will trigger browser connector
                params: { name: 'AI Generated Funnel - ' + new Date().toISOString().split('T')[0] },
                status: 'PENDING',
                attempts: 0
            });

            // Add a follow up to email about it?
            if (lowerInput.includes('notify') || lowerInput.includes('email')) {
                steps.push({
                    id: `step_${stepCount++}`,
                    connectorName: 'Email',
                    action: 'send_email',
                    params: { to: process.env.ADMIN_EMAIL || 'admin@example.com', subject: 'Funnel Created', body: 'Your new funnel has been created successfully.' },
                    status: 'PENDING',
                    attempts: 0
                });
            }
        }

        // 2. Scrape Leads (Generic or Google)
        if (lowerInput.includes('google') || lowerInput.includes('leads') || lowerInput.includes('zillow') || lowerInput.includes('find')) {
            steps.push({
                id: `step_${stepCount++}`,
                connectorName: 'GoogleMaps',
                action: 'search_leads',
                params: { query: userInput }, // Pass full query context
                status: 'PENDING',
                attempts: 0
            });
        }

        // 3. Email Leads
        if (lowerInput.includes('email') || lowerInput.includes('message')) {
            const searchStepId = steps.find(s => s.action === 'search_leads')?.id;
            const emailParams: any = {
                to: searchStepId ? `{{${searchStepId}.result[*].email}}` : 'test@example.com',
                subject: 'Service Offer',
                body: 'Hello from AI Agent...'
            };

            steps.push({
                id: `step_${stepCount++}`,
                connectorName: 'GHL',
                action: 'send_email',
                params: emailParams,
                status: 'PENDING',
                attempts: 0,
                dependsOn: searchStepId ? [searchStepId] : []
            });
        }

        // 4. Report
        if (lowerInput.includes('report') || lowerInput.includes('performance')) {
            steps.push({
                id: `step_${stepCount++}`,
                connectorName: 'Report',
                action: 'generate_report',
                params: { type: 'performance' },
                status: 'PENDING',
                attempts: 0,
                dependsOn: steps.length > 0 ? steps.map(s => s.id) : []
            });
        }

        // Fallback default step if nothing matched
        if (steps.length === 0) {
            steps.push({
                id: 'step_1',
                connectorName: 'GHL',
                action: 'create_opportunity',
                params: { title: 'Manual Review needed' },
                status: 'PENDING',
                attempts: 0
            });
        }

        return {
            id: planId,
            originalGoal: userInput,
            steps,
            createdAt: new Date().toISOString(),
            status: 'PENDING'
        };
    }
}
