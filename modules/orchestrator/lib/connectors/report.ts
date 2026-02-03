
import { BaseConnector } from './base';
import { Plan } from '../types';

export class ReportConnector extends BaseConnector {
    name = 'Report';

    async execute(action: string, params: any): Promise<any> {
        this.log(`Generating Report... Action: ${action}`);

        if (action === 'generate_report') {
            const plan: Plan = params.planContext; // Injected by Orchestrator

            if (!plan) {
                return {
                    result: "No plan context available to generate report.",
                    summary: "Use the Orchestrator to run this step."
                };
            }

            const totalSteps = plan.steps.length;
            const completed = plan.steps.filter(s => s.status === 'COMPLETED').length;
            const failed = plan.steps.filter(s => s.status === 'FAILED').length;
            const pending = plan.steps.filter(s => s.status === 'PENDING').length;

            // Extract key metrics
            const leadsStep = plan.steps.find(s => s.connectorName === 'Zillow' || s.action === 'search_leads');
            const leadsCount = leadsStep?.result ? (Array.isArray(leadsStep.result) ? leadsStep.result.length : 1) : 0;

            const emailsStep = plan.steps.find(s => s.action === 'send_email');
            const emailStatus = emailsStep?.status === 'COMPLETED' ? 'Sent' : 'Pending/Failed';

            const postsScheduled = plan.steps.filter(s => s.connectorName === 'Facebook' && s.status === 'COMPLETED').length;

            const report = {
                summary: `Task Execution Report: ${completed}/${totalSteps} steps completed.`,
                metrics: {
                    leadsFound: leadsCount,
                    emailStatus: emailStatus,
                    socialPostsScheduled: postsScheduled,
                    failedSteps: failed
                },
                timestamp: new Date().toISOString()
            };

            this.log(`Report Generated: ${JSON.stringify(report)}`);
            return report;
        }

        throw new Error(`Unknown action: ${action}`);
    }
}
