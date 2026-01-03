import { Plan, Step, Connector } from './types';
import { StateManager } from './state-manager';
import { GHLConnector } from './connectors/ghl';
import { GHLBrowserConnector } from './connectors/ghl-browser';
import { GoogleConnector } from './connectors/google';
import { EmailConnector } from './connectors/email';
import { FacebookConnector } from './connectors/facebook';
import { ReportConnector } from './connectors/report';
import { IntelConnector } from './connectors/intel';
import { Inspector } from './inspector';
import { v4 as uuidv4 } from 'uuid';

export class Orchestrator {
    private connectors: Map<string, Connector>;
    private inspector: Inspector; // [NEW]

    constructor() {
        this.connectors = new Map();
        this.inspector = new Inspector(); // [NEW]
        this.registerConnector(new GHLConnector());
        this.registerConnector(new GHLBrowserConnector());
        this.registerConnector(new GoogleConnector());
        this.registerConnector(new EmailConnector());
        this.registerConnector(new FacebookConnector());
        this.registerConnector(new ReportConnector());
        this.registerConnector(new IntelConnector());

        // HEARTBEAT PROTOCOL: Log "Alive" status every 30 seconds if executing
        setInterval(() => {
            // Only log if we have active plans? For now, just a system pulse check.
            // verify system is not sleeping
        }, 30000);
    }

    private heartbeat(planId: string) {
        this.logToArtifact(`💓 **SYSTEM HEARTBEAT**: Orchestrator Active. processing...`, planId);
    }

    registerConnector(connector: Connector) {
        this.connectors.set(connector.name, connector);
    }

    async executePlan(planId: string) {
        const plan = StateManager.getPlan(planId);
        if (!plan) throw new Error("Plan not found");

        plan.status = 'RUNNING';
        StateManager.savePlan(plan);

        let running = true;
        while (running) {
            const currentPlan = StateManager.getPlan(planId)!;
            const pendingSteps = currentPlan.steps.filter(s => s.status === 'PENDING');
            const runningSteps = currentPlan.steps.filter(s => s.status === 'RUNNING');

            if (pendingSteps.length === 0 && runningSteps.length === 0) {
                running = false;
                const failed = currentPlan.steps.some(s => s.status === 'FAILED');
                currentPlan.status = failed ? 'FAILED' : 'COMPLETED';
                StateManager.savePlan(currentPlan);
                break;
            }

            const readySteps = pendingSteps.filter(step => {
                if (!step.dependsOn || step.dependsOn.length === 0) return true;
                return step.dependsOn.every(depId => {
                    const depStep = currentPlan.steps.find(s => s.id === depId);
                    return depStep && depStep.status === 'COMPLETED';
                });
            });

            if (readySteps.length === 0 && runningSteps.length === 0) {
                currentPlan.status = 'FAILED';
                StateManager.savePlan(currentPlan);
                running = false;
                break;
            }

            await Promise.all(readySteps.map(step => this.executeStep(currentPlan, step)));

            // Heartbeat
            this.heartbeat(currentPlan.id);
            await new Promise(r => setTimeout(r, 1000));
        }
    }

    private hasBrowserFallback(action: string): boolean {
        // List of actions that might have browser fallbacks or are browser-only
        const browserActions = ['create_funnel_page', 'update_workflow_visual', 'upload_media', 'send_email'];
        return browserActions.includes(action);
    }

    private async executeStep(plan: Plan, step: Step) {
        step.status = 'RUNNING';
        StateManager.savePlan(plan);
        StateManager.addLog({
            id: uuidv4(),
            planId: plan.id,
            stepId: step.id,
            timestamp: new Date().toISOString(),
            level: 'info',
            message: `Starting step: ${step.action}`
        });

        // [OVERSEER] Log start of step to artifact
        this.logToArtifact(`> **Starting Step**: ${step.id} - ${step.action}`, plan.id);

        try {
            // Try to get the requested connector
            let connector = this.connectors.get(step.connectorName);

            // Special handling: If action is browser-only but GHL was requested, switch to GHL_Browser
            if (step.connectorName === 'GHL' && this.hasBrowserFallback(step.action)) {
                const browserConnector = this.connectors.get('GHL_Browser');
                if (browserConnector) {
                    connector = browserConnector;
                    // Log the switch for debugging
                    StateManager.addLog({
                        id: uuidv4(),
                        planId: plan.id,
                        stepId: step.id,
                        timestamp: new Date().toISOString(),
                        level: 'info',
                        message: `Switching to GHL_Browser connector for action: ${step.action}`
                    });
                }
            }

            if (!connector) throw new Error(`Connector ${step.connectorName} not found`);

            let result = null;
            const maxRetries = 3;

            for (let i = 0; i < maxRetries; i++) {
                try {
                    step.attempts = i + 1;

                    // Resolve params (substitute {{variables}})
                    const resolvedParams = this.resolveParams(step.params, plan);
                    const executionParams = { ...resolvedParams, planContext: plan };

                    result = await connector.execute(step.action, executionParams);
                    break;
                } catch (err: any) {
                    // Start of fallback logic
                    const isApiError = err.message.includes('API Failed') || err.message.includes('404') || err.message.includes('500') || err.message.includes('Not implemented');
                    if (isApiError && this.hasBrowserFallback(step.action)) {
                        console.log(`[Orchestrator] API failed for ${step.action}, attempting Browser Fallback...`);
                        const browser = this.connectors.get('GHL_Browser');
                        if (browser) {
                            try {
                                // Re-create execution params for fallback
                                const resolvedFallback = this.resolveParams(step.params, plan);
                                const fallbackParams = { ...resolvedFallback, planContext: plan };
                                result = await browser.execute(step.action, fallbackParams);
                                break; // Fallback succeeded
                            } catch (browserErr: any) {
                                console.log(`[Orchestrator] Browser fallback also failed: ${browserErr.message}`);
                                // Continue to standard retry logic below
                            }
                        }
                    }

                    StateManager.addLog({
                        id: uuidv4(),
                        planId: plan.id,
                        stepId: step.id,
                        timestamp: new Date().toISOString(),
                        level: 'warn',
                        message: `Attempt ${i + 1} failed: ${err.message}`
                    });
                    if (i === maxRetries - 1) throw err;
                    await new Promise(r => setTimeout(r, 1000 * (i + 1)));
                }
            }

            step.status = 'COMPLETED';
            step.result = result;
            // Log successful completion
            StateManager.addLog({
                id: uuidv4(),
                planId: plan.id,
                stepId: step.id,
                timestamp: new Date().toISOString(),
                level: 'info',
                message: `Step completed successfully`,
                details: result
            });

            // ---------------------------------------------------------
            // ARCHITECT-BUILDER-INSPECTOR: INSPECTION PHASE
            // ---------------------------------------------------------
            if (this.inspector && step.connectorName !== 'Report') {
                const auditStartMsg = `🕵️ **OVERSEER AUDIT**: Checking '${step.action}'...`;
                this.logToArtifact(auditStartMsg, plan.id);

                const inspection = await this.inspector.evaluate(step.action, step.params, result);

                if (inspection.passed) {
                    const passMsg = `✅ **PASSED**: ${inspection.reasoning}`;
                    this.log(passMsg); // Console
                    this.logToArtifact(passMsg, plan.id); // Artifact
                } else {
                    const failMsg = `❌ **REJECTED**: ${inspection.reasoning}\n   🛠️ **FIX REQUIRED**: ${inspection.correctionRequest}`;
                    this.log(failMsg);
                    this.logToArtifact(failMsg, plan.id);

                    // STRICT MODE: Fail the task (trigger retry loop)
                    step.status = 'FAILED';
                    step.error = `Inspector Rejected: ${inspection.reasoning}`;
                    StateManager.savePlan(plan);

                    // Throw error to trigger orchestrator retry logic
                    throw new Error(`Inspector Rejected: ${inspection.reasoning} (Fix: ${inspection.correctionRequest})`);
                }
            }
            // ---------------------------------------------------------

            step.status = 'COMPLETED';
            step.result = result;

            // Log completion
            this.logToArtifact(`> **Step Completed**: ${step.id}\n**Result**:\n\`\`\`json\n${JSON.stringify(result, null, 2)}\n\`\`\`\n---\n`, plan.id);

            // Update plan state
            StateManager.savePlan(plan);
        }

        catch (error: any) {
            const errorMsg = `🚨 **CRITICAL ERROR**: ${error.message}`;
            this.log(errorMsg);
            this.logToArtifact(errorMsg, plan.id);

            step.status = 'FAILED';
            step.error = error.message;
            StateManager.savePlan(plan);
        }

        const freshPlan = StateManager.getPlan(plan.id);
        if (freshPlan) {
            const freshStepIndex = freshPlan.steps.findIndex(s => s.id === step.id);
            if (freshStepIndex !== -1) {
                freshPlan.steps[freshStepIndex] = step;
                StateManager.savePlan(freshPlan);
            }
        }
    }

    private resolveParams(params: any, plan: Plan): any {
        if (!params) return params;

        // Deep clone to avoid mutating original params
        const resolved = JSON.parse(JSON.stringify(params));

        for (const key in resolved) {
            const value = resolved[key];
            if (typeof value === 'string' && value.startsWith('{{') && value.endsWith('}}')) {
                // Extract variable: step_id.result.field or step_id.result[*].field
                const varContent = value.substring(2, value.length - 2).trim();
                console.log(`[Orchestrator] Resolving variable: ${varContent}`);

                // Handle Array Mapping: step_id.result[*].field
                if (varContent.includes('[*]')) {
                    const [stepRef, fieldPath] = varContent.split('[*].');
                    const stepId = stepRef.replace('.result', '');
                    const sourceStep = plan.steps.find(s => s.id === stepId || s.id === stepId.replace('step_', ''));

                    if (sourceStep) {
                        console.log(`[Orchestrator] Found source step for array map: ${sourceStep.id}`);
                        if (Array.isArray(sourceStep.result)) {
                            // Extract field, filtering out null/undefined
                            resolved[key] = sourceStep.result
                                .map((item: any) => item[fieldPath])
                                .filter((val: any) => val !== undefined && val !== null && val !== '');

                            console.log(`[Orchestrator] Resolved array to length: ${resolved[key].length}`);
                        } else {
                            console.log(`[Orchestrator] WARN: Source result is not array: ${JSON.stringify(sourceStep.result)}`);
                        }
                    } else {
                        // Try Case Insensitive Match
                        const caseInsensitive = plan.steps.find(s => s.id.toLowerCase() === stepId.toLowerCase());
                        if (caseInsensitive) {
                            console.log(`[Orchestrator] Found step via case-insensitive match: ${caseInsensitive.id}`);
                            if (Array.isArray(caseInsensitive.result)) {
                                resolved[key] = caseInsensitive.result
                                    .map((item: any) => item[fieldPath])
                                    .filter((val: any) => val !== undefined && val !== null && val !== '');
                            }
                        } else {
                            console.log(`[Orchestrator] WARN: Source step not found: ${stepId}. Available IDs: ${plan.steps.map(s => s.id).join(', ')}`);
                        }
                    }
                } else {
                    // Handle Direct Access: step_id.result.field
                    const parts = varContent.split('.');
                    if (parts.length >= 2) {
                        const stepId = parts[0];
                        const sourceStep = plan.steps.find(s => s.id === stepId);
                        if (sourceStep && sourceStep.result) {
                            // Traverse result
                            let val = sourceStep.result;
                            for (let i = 2; i < parts.length; i++) { // skip stepId and 'result'
                                if (val) val = val[parts[i]];
                            }
                            resolved[key] = val;
                            console.log(`[Orchestrator] Resolved value: ${val}`);
                        }
                    }
                }
            }
        }
        return resolved;
    }

    private log(message: string) {
        console.log(message);
    }

    private logToArtifact(message: string, planId?: string) {
        // Append to Overseer Log Artifact
        const logPath = "C:\\Users\\nearm\\.gemini\\antigravity\\brain\\94a03651-4a96-4031-ae35-3695ec99a776\\execution_log.md";
        const timestamp = new Date().toISOString();
        const displayTime = new Date().toLocaleTimeString();
        const line = `\n**[${displayTime}]** ${message}\n`;
        const fs = require('fs');
        try {
            // Ensure file exists or append
            fs.appendFileSync(logPath, line);

            // [UI SYNC] specific for User Visibility: Also push to StateManager logs
            if (planId) {
                StateManager.addLog({
                    id: uuidv4(),
                    planId: planId,
                    stepId: 'overseer', // generic source
                    timestamp: timestamp,
                    level: message.includes('❌') ? 'error' : 'info',
                    message: message
                });
            }
        } catch (e) {
            console.error("Failed to write to execution log artifact", e);
        }
    }
}
