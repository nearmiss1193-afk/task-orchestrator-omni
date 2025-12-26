
export type TaskStatus = 'PENDING' | 'RUNNING' | 'COMPLETED' | 'FAILED';

export interface ConnectorConfig {
    [key: string]: any;
}

export interface Step {
    id: string;
    connectorName: string;
    action: string;
    params: Record<string, any>;
    status: TaskStatus;
    result?: any;
    error?: string;
    attempts: number;
    dependsOn?: string[]; // array of step IDs
}

export interface Plan {
    id: string;
    originalGoal: string;
    steps: Step[];
    createdAt: string;
    status: TaskStatus;
}

export interface ExecutionLog {
    id: string;
    planId: string;
    stepId?: string;
    timestamp: string;
    level: 'info' | 'warn' | 'error';
    message: string;
    details?: any;
}

export interface Connector {
    name: string;
    execute(action: string, params: any): Promise<any>;
    validate(action: string, params: any): boolean;
}
