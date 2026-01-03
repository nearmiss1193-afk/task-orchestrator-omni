
import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

export async function GET() {
    try {
        const dbPath = path.join(process.cwd(), '../../../db/clients.json');
        if (!fs.existsSync(dbPath)) {
            return NextResponse.json({ clients: [] });
        }
        const data = fs.readFileSync(dbPath, 'utf8');
        const clients = JSON.parse(data);

        // Sort by recent
        clients.reverse();

        return NextResponse.json({ clients });
    } catch (error) {
        return NextResponse.json({ error: "Failed to fetch clients" }, { status: 500 });
    }
}
