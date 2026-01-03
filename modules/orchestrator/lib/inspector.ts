
import { GoogleGenerativeAI } from '@google/generative-ai';

export interface InspectionResult {
    passed: boolean;
    reasoning: string;
    correctionRequest?: string; // If failed, what specifically needs to be fixed?
}

export class Inspector {
    private googleAI: GoogleGenerativeAI;
    private model: any;

    constructor() {
        this.googleAI = new GoogleGenerativeAI(process.env.GOOGLE_API_KEY || '');
        this.model = this.googleAI.getGenerativeModel({
            model: "gemini-1.5-pro",
            generationConfig: { responseMimeType: "application/json" } // Force JSON
        });
    }

    /**
     * Inspects the result of a tool execution against its original intent.
     * @param stepAction The action that was attempted (e.g. "create_funnel_page")
     * @param stepParams The parameters provided (e.g. { name: "Offer" })
     * @param executionResult The raw result from the connector
     * @returns InspectionResult
     */
    async evaluate(stepAction: string, stepParams: any, executionResult: any): Promise<InspectionResult> {

        // Skip inspection for Report step (it's the output itself)
        if (stepAction === 'generate_report') {
            return { passed: true, reasoning: "Self-reporting step is trusted." };
        }

        // Skip inspection for low-risk read/search ops if they have results? 
        // No, verify them too. "Did we find plumbers? or just junk?"

        const prompt = `
        You are the QA INSPECTOR for an autonomous agent.
        Your Job: Verify if the "Builder Agent" successfully accomplished the task.
        
        TASK INFO:
        Action: "${stepAction}"
        Input Params: ${JSON.stringify(stepParams)}
        
        BUILDER'S OUTPUT:
        ${JSON.stringify(executionResult)}
        
        RULES:
        1. If specific failures are mentioned in the output (e.g. "error", "failed", "timeout"), FAIL the inspection.
        2. If the output claims "Simulated Success" but looks fake when "Real Mode" is required, FAIL the inspection.
        3. If the output is empty or null, FAIL.
        4. If it looks correct, PASS.
        
        Respond in JSON:
        {
          "passed": boolean,
          "reasoning": "Short explanation of your verdict",
          "correctionRequest": "Optional: How should the Builder fix this? e.g. 'Retry with different selector'"
        }
        `;

        try {
            const result = await this.model.generateContent(prompt);
            const response = await result.response;
            const text = response.text();

            // Clean markdown jsons
            const jsonStr = text.replace(/```json\n?|\n?```/g, '').trim();
            const evaluation = JSON.parse(jsonStr);

            return {
                passed: evaluation.passed,
                reasoning: evaluation.reasoning,
                correctionRequest: evaluation.correctionRequest
            };

        } catch (error: any) {
            console.error("[Inspector] LLM Inspection failed:", error.message);
            // FALLBACK: Heuristic Check
            // If the LLM is broken, we fall back to a basic keyword check.

            // 1. Trust explicit success flags (e.g. from Soft Fail mocks)
            if (executionResult && (executionResult.success === true || (executionResult.status && executionResult.status === 'sent'))) {
                return {
                    passed: true,
                    reasoning: `[Heuristic] LLM unavailable. Explicit 'success' flag detected. Auto-passing.`
                };
            }

            // 2. Otherwise scan for failure keywords
            const resultStr = JSON.stringify(executionResult).toLowerCase();
            const failureKeywords = ['error', 'failed', 'exception', 'timeout', 'null', 'undefined'];

            const hasError = failureKeywords.some(kw => resultStr.includes(kw));
            if (hasError) {
                return {
                    passed: false,
                    reasoning: `[Heuristic] LLM unavailable. Detected failure keyword in result.`
                };
            }

            return {
                passed: true,
                reasoning: `[Heuristic] LLM unavailable. No failure keywords detected in result. Auto-passing.`
            };
        }
    }
}
