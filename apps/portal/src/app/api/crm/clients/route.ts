
import { NextResponse } from 'next/server';

export async function GET() {
    try {
        // Fallback for Vercel deployment where local JSON access is unavailable
        const clients = [
            { name: "David Miller", phone: "555-0123", industry: "HVAC", status: "New", created_at: new Date().toISOString() },
            { name: "Sarah Connor", phone: "555-0999", industry: "Plumbing", status: "Qualified", created_at: new Date(Date.now() - 86400000).toISOString() },
            { name: "Mike Ross", phone: "555-0777", industry: "Legal", status: "Closed", created_at: new Date(Date.now() - 172800000).toISOString() }
        ];

        return NextResponse.json({ clients });
    } catch (error) {
        return NextResponse.json({ error: "Failed to fetch clients" }, { status: 500 });
    }
}
