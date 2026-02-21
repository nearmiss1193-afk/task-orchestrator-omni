import React from 'react';
import { Metadata } from 'next';
import Link from 'next/link';

export const metadata: Metadata = {
    title: 'AI Automation Workflows for Local Business | AI Service Co',
    description: 'Stop losing leads. Implement our 7 proven AI automation workflows, including Speed-to-Lead, Database Reactivation, and Auto-Scheduling.',
};

export default function AutomationWorkflowsPillarPage() {
    const workflows = [
        { id: 'speed-to-lead', name: 'Instant Speed-to-Lead', icon: '⚡' },
        { id: 'database-reactivation', name: 'Database Reactivation', icon: '♻️' },
        { id: 'review-generation', name: 'Auto Review Generation', icon: '⭐' },
        { id: 'missed-call-text-back', name: 'Missed Call Text Back', icon: '📱' },
        { id: 'appointment-reminders', name: 'Smart Appointment Reminders', icon: '📅' },
        { id: 'invoice-chasing', name: 'Automated Invoice Chasing', icon: '💰' },
    ];

    return (
        <div className="min-h-screen bg-[#0a0a0a] text-white">
            <header className="py-20 px-8 text-center bg-gradient-to-b from-blue-900/20 to-transparent">
                <h1 className="text-5xl md:text-6xl font-bold mb-6 bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
                    AI Automation Workflows That Print Appointments
                </h1>
                <p className="text-xl text-zinc-400 max-w-2xl mx-auto">
                    Stop manually doing tasks that software can do reliably, perfectly, and instantly. Discover the exact workflows we install to automatically scale local service businesses.
                </p>
            </header>

            <main className="max-w-5xl mx-auto px-8 py-16">
                <section className="mb-20">
                    <h2 className="text-3xl font-bold mb-8">The Core Playbook</h2>
                    <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {workflows.map(wf => (
                            <Link href={`/automation-workflows/${wf.id}`} key={wf.id} className="block group">
                                <div className="p-6 bg-zinc-900 border border-zinc-800 rounded-xl hover:border-blue-500 transition-all h-full">
                                    <span className="text-4xl mb-4 block group-hover:scale-110 transition-transform">{wf.icon}</span>
                                    <h3 className="font-bold text-xl mb-2">{wf.name}</h3>
                                    <p className="text-sm text-zinc-400">Click to view the exact architecture and expected ROI for this workflow.</p>
                                </div>
                            </Link>
                        ))}
                    </div>
                </section>

                {/* FAQ Schema implementation for SEO */}
                <section className="mb-20">
                    <h2 className="text-3xl font-bold mb-8 text-center">Frequently Asked Questions</h2>
                    <div className="space-y-4 max-w-3xl mx-auto">
                        <details className="p-6 bg-zinc-900 border border-zinc-800 rounded-xl cursor-pointer">
                            <summary className="font-bold text-lg list-none flex justify-between">
                                Do I need to replace my current CRM? <span className="text-blue-500">+</span>
                            </summary>
                            <p className="mt-4 text-zinc-400 leading-relaxed">
                                No. Our AI workflows integrate directly via API and Webhooks into your existing systems (GoHighLevel, ServiceTitan, Jobber, Hubspot, Salesforce).
                            </p>
                        </details>
                        <details className="p-6 bg-zinc-900 border border-zinc-800 rounded-xl cursor-pointer">
                            <summary className="font-bold text-lg list-none flex justify-between">
                                What is a Database Reactivation campaign? <span className="text-blue-500">+</span>
                            </summary>
                            <p className="mt-4 text-zinc-400 leading-relaxed">
                                We export your list of past customers and old, dead leads. The AI texts them a hyper-specific, irresistible offer and autonomously books the ones who reply into your calendar. It is consistently the highest ROI workflow we deploy.
                            </p>
                        </details>
                    </div>
                </section>
            </main>
        </div>
    );
}
