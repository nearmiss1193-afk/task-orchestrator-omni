import { BaseConnector } from './base';

export class FacebookConnector extends BaseConnector {
    name = 'Facebook';

    async execute(action: string, params: any): Promise<any> {
        this.log(`Facebook Action: ${action}`);

        await new Promise(resolve => setTimeout(resolve, 800));

        if (action === 'schedule_post') {
            return { postId: `fb_${Date.now()}`, scheduledTime: params.time };
        }
        throw new Error(`Unknown action: ${action}`);
    }
}
