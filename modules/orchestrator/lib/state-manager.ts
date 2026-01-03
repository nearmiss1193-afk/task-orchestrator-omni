import fs from 'fs';
import path from 'path';
import { Plan, ExecutionLog } from './types';

const DATA_DIR = path.join(process.cwd(), 'data');
const PLANS_FILE = path.join(DATA_DIR, 'plans.json');
const LOGS_FILE = path.join(DATA_DIR, 'logs.json');

// Ensure data directory exists
if (!fs.existsSync(DATA_DIR)) {
    fs.mkdirSync(DATA_DIR, { recursive: true });
}

// Initialize files if they don't exist
if (!fs.existsSync(PLANS_FILE)) {
    fs.writeFileSync(PLANS_FILE, JSON.stringify([]));
}
if (!fs.existsSync(LOGS_FILE)) {
    fs.writeFileSync(LOGS_FILE, JSON.stringify([]));
}

export class StateManager {
    static getPlans(): Plan[] {
        try {
            const data = fs.readFileSync(PLANS_FILE, 'utf-8');
            return JSON.parse(data);
        } catch (error) {
            console.error("Error reading plans:", error);
            return [];
        }
    }

    static savePlan(plan: Plan): void {
        const plans = this.getPlans();
        const index = plans.findIndex((p) => p.id === plan.id);
        if (index >= 0) {
            plans[index] = plan;
        } else {
            plans.push(plan);
        }
        fs.writeFileSync(PLANS_FILE, JSON.stringify(plans, null, 2));
    }

    static getPlan(id: string): Plan | undefined {
        return this.getPlans().find((p) => p.id === id);
    }

    static addLog(log: ExecutionLog): void {
        try {
            const data = fs.readFileSync(LOGS_FILE, 'utf-8');
            const logs: ExecutionLog[] = JSON.parse(data);
            logs.push(log);
            fs.writeFileSync(LOGS_FILE, JSON.stringify(logs, null, 2));
        } catch (e) {
            console.error("Failed to write log", e)
        }
    }

    static getLogs(planId: string): ExecutionLog[] {
        try {
            const data = fs.readFileSync(LOGS_FILE, 'utf-8');
            const logs: ExecutionLog[] = JSON.parse(data);
            return logs.filter((l) => l.planId === planId);
        } catch (e) {
            return [];
        }
    }
}
