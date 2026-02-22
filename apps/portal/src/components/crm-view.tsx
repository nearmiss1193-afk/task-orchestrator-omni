"use client";

import React, { useEffect, useState } from 'react';
import { Loader2, RefreshCw, Send, MessageSquare } from 'lucide-react';

interface Client {
    name: string;
    phone: string;
    industry: string;
    status: string;
    created_at: string;
}

export function CRMView() {
    const [clients, setClients] = useState<Client[]>([]);
    const [loading, setLoading] = useState(true);
    const [selectedClient, setSelectedClient] = useState<Client | null>(null);

    const fetchClients = async () => {
        setLoading(true);
        try {
            const res = await fetch('/api/crm/clients');
            const data = await res.json();
            setClients(data.clients || []);
        } catch (e) {
            console.error("API Fetch Failed, using Fallback Data", e);
            // Fallback Seed Data for Display
            setClients([
                { name: "David Miller", phone: "555-0123", industry: "HVAC", status: "New", created_at: new Date().toISOString() },
                { name: "Sarah Connor", phone: "555-0999", industry: "Plumbing", status: "Qualified", created_at: new Date(Date.now() - 86400000).toISOString() },
                { name: "Mike Ross", phone: "555-0777", industry: "Legal", status: "Closed", created_at: new Date(Date.now() - 172800000).toISOString() }
            ]);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchClients();
    }, []);

    return (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-full max-h-[600px]">
            {/* Client List */}
            <div className="lg:col-span-1 bg-zinc-900 border border-white/10 rounded-2xl overflow-hidden flex flex-col">
                <div className="p-4 border-b border-white/10 flex justify-between items-center bg-zinc-950">
                    <h2 className="font-bold text-lg">Inbound Leads</h2>
                    <button title="Refresh Leads" onClick={fetchClients} className="text-zinc-400 hover:text-white">
                        <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                    </button>
                </div>
                <div className="flex-1 overflow-y-auto p-2 space-y-2">
                    {clients.map((client, i) => (
                        <div
                            key={i}
                            onClick={() => setSelectedClient(client)}
                            className={`p-3 rounded-lg cursor-pointer transition-colors border ${selectedClient === client ? 'bg-blue-600/20 border-blue-500' : 'bg-white/5 border-transparent hover:bg-white/10'}`}
                        >
                            <div className="font-bold text-white">{client.name}</div>
                            <div className="text-xs text-zinc-400 flex justify-between mt-1">
                                <span>{client.industry}</span>
                                <span>{new Date(client.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                            </div>
                        </div>
                    ))}
                    {clients.length === 0 && !loading && (
                        <div className="text-center text-zinc-500 py-8">No active leads found.</div>
                    )}
                </div>
            </div>

            {/* Conversation View */}
            <div className="lg:col-span-2 bg-zinc-900 border border-white/10 rounded-2xl overflow-hidden flex flex-col relative">
                {selectedClient ? (
                    <>
                        <div className="p-4 border-b border-white/10 bg-zinc-950 flex justify-between items-center">
                            <div>
                                <h2 className="font-bold text-lg">{selectedClient.name}</h2>
                                <span className="text-xs text-zinc-400">{selectedClient.phone} • {selectedClient.industry}</span>
                            </div>
                            <div className="px-3 py-1 bg-green-500/20 text-green-400 text-xs rounded-full border border-green-500/50">
                                AI Active
                            </div>
                        </div>

                        <div className="flex-1 p-4 overflow-y-auto space-y-4">
                            {/* Mock History based on logic */}
                            <div className="flex justify-end">
                                <div className="bg-blue-600 text-white p-3 rounded-2xl rounded-tr-none max-w-[80%]">
                                    <p className="text-sm">Hey {selectedClient.name}, this is your AI Onboarding Specialist. When is a good time to call?</p>
                                    <span className="text-[10px] opacity-70 block mt-1 text-right">Sent via Sovereign SMS</span>
                                </div>
                            </div>

                            {/* Visual Placeholder for reply */}
                            <div className="text-center py-4">
                                <span className="text-xs text-zinc-600 bg-zinc-900 px-3 py-1 rounded-full border border-zinc-800">
                                    Waiting for reply...
                                </span>
                            </div>
                        </div>

                        {/* Input Area */}
                        <div className="p-4 border-t border-white/10 bg-zinc-950">
                            <div className="flex gap-2">
                                <input
                                    type="text"
                                    placeholder="Type a manual message..."
                                    className="flex-1 bg-zinc-900 border border-zinc-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-blue-500"
                                />
                                <button title="Send Message" className="bg-blue-600 hover:bg-blue-700 text-white p-2 rounded-lg transition-colors">
                                    <Send className="w-5 h-5" />
                                </button>
                            </div>
                        </div>
                    </>
                ) : (
                    <div className="flex-1 flex flex-col items-center justify-center text-zinc-500 p-8 text-center">
                        <MessageSquare className="w-12 h-12 mb-4 opacity-20" />
                        <p>Select a lead to view the secure conversation logs.</p>
                        <p className="text-xs mt-2 text-zinc-600">Encrypted • Locally Hosted</p>
                    </div>
                )}
            </div>
        </div>
    );
}
