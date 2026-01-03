
import { createClient, SupabaseClient } from '@supabase/supabase-js';
import * as dotenv from 'dotenv';

dotenv.config({ path: '.env.local' });

export class HeartbeatMonitor {
    private supabase: SupabaseClient;

    constructor() {
        this.supabase = createClient(
            process.env.NEXT_PUBLIC_SUPABASE_URL || '',
            process.env.SUPABASE_SERVICE_ROLE_KEY || ''
        );
    }

    async logHeartbeat(component: string, status: string, metadata: any = {}) {
        console.log(`📡 [Heartbeat] Component: ${component} | Status: ${status}`);

        try {
            await this.supabase.from('system_health').upsert({
                component,
                status,
                last_heartbeat: new Date().toISOString(),
                metadata
            }, { onConflict: 'component' });
        } catch (error) {
            console.error(`❌ [Heartbeat] Failed to log for ${component}:`, error);
        }
    }
}

// Simple test run
if (require.main === module) {
    const monitor = new HeartbeatMonitor();
    monitor.logHeartbeat('OmniLoop', 'ONLINE', { version: '1.0.0-turbo' });
}
