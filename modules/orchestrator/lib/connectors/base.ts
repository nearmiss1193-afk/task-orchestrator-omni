import { Connector } from '../types';

export abstract class BaseConnector implements Connector {
    abstract name: string;

    abstract execute(action: string, params: any): Promise<any>;

    validate(action: string, params: any): boolean {
        return true; // Default to true, override for specific validation
    }

    protected log(message: string) {
        console.log(`[${this.name}] ${message}`);
    }
}
