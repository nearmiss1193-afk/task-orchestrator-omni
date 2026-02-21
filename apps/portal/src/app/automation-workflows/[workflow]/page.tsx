import React from 'react';
import { Metadata } from 'next';
import Link from 'next/link';

export async function generateMetadata({ params }: { params: { workflow: string } }): Promise<Metadata> {
    const formattedWorkflow = params.workflow.split('-').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');

    return {
        title: `${formattedWorkflow} Automation Strategy | AI Service Co`,
        description: `Learn how installing the ${formattedWorkflow} workflow creates autonomous revenue for your local service business without hiring additional staff.`,
    };
}

export function generateStaticParams() {
    return [
        { workflow: 'speed-to-lead' },
        { workflow: 'database-reactivation' },
        { workflow: 'review-generation' },
        { workflow: 'missed-call-text-back' },
        { workflow: 'appointment-reminders' },
        { workflow: 'invoice-chasing' }
    ];
}

export default function AutomationWorkflowDetailPage({ params }: { params: { workflow: string } }) {
    const formattedWorkflow = params.workflow.split('-').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');

    return (
        <div className="min-h-screen bg-[#0a0a0a] text-white">
            <nav className="py-4 px-8 text-sm text-zinc-500 border-b border-zinc-800">
                <Link href="/" className="hover:text-blue-400">Home</Link>
                <span className="mx-2">›</span>
                <Link href="/automation-workflows" className="hover:text-blue-400">Workflows</Link>
                <span className="mx-2">›</span>
                <span className="text-zinc-300">{formattedWorkflow}</span>
            </nav>

            <header className="py-20 px-8 text-center bg-gradient-to-b from-blue-900/20 to-transparent">
                <div className="inline-block px-4 py-2 border border-blue-500/30 rounded-full text-blue-400 font-bold mb-6 text-sm">
                    CORE WORKFLOW
                </div>
                <h1 className="text-5xl md:text-6xl font-bold mb-6 bg-gradient-to-r from-blue-400 to-green-500 bg-clip-text text-transparent">
                    {formattedWorkflow} Architecture
                </h1>
                <p className="text-xl text-zinc-400 max-w-2xl mx-auto">
                    A deep dive into how we architect, install, and optimize the {formattedWorkflow} system for maximum ROI in local service businesses.
                </p>
                <button className="mt-8 px-8 py-4 bg-white text-black hover:bg-zinc-200 rounded-full font-bold text-lg transition-all">
                    Install This Workflow Today
                </button>
            </header>

            <main className="max-w-5xl mx-auto px-8 py-16">
                <section className="mb-20">
                    <h2 className="text-3xl font-bold mb-8">How The Automation Works</h2>
                    <div className="p-8 bg-zinc-900 border border-zinc-800 rounded-xl relative">
                        <div className="absolute top-4 right-4 text-green-500">
                            <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                            </svg>
                        </div>
                        <h3 className="text-2xl font-bold mb-4 text-white">The Blueprint</h3>
                        <p className="text-zinc-400 leading-relaxed mb-6">
                            When designing the {formattedWorkflow} architecture, our primary objective is stripping out human dependency. Your staff shouldn't be clicking buttons or remembering to send texts—the system detects the required trigger event (like a missed call, a completed job, or an incoming web form) and instantly executes the exact communication protocol required to close the loop.
                        </p>
                        <div className="p-4 bg-black/50 border border-white/5 rounded-lg space-y-3 font-mono text-sm text-blue-400">
                            <p>{`Trigger ➔ API Webhook fired`}</p>
                            <p>{`Condition ➔ Verify Lead Status in CRM`}</p>
                            <p>{`Action 1 ➔ AI Generates Hyper-Personalized SMS`}</p>
                            <p>{`Action 2 ➔ Delay 3 Minutes ➔ Send`}</p>
                            <p>{`Action 3 ➔ If Reply = Yes ➔ Auto-Book Calendar`}</p>
                        </div>
                    </div>
                </section>

                <section className="mb-20">
                    <h2 className="text-3xl font-bold mb-8 text-center">Expected ROI Implementation Metrics</h2>
                    <div className="grid md:grid-cols-3 gap-8 text-center">
                        <div className="p-6 bg-zinc-900 border border-zinc-800 rounded-xl">
                            <div className="text-4xl font-black text-blue-500 mb-2">~35%</div>
                            <h3 className="font-bold text-lg mb-2">Conversion Lift</h3>
                            <p className="text-sm text-zinc-400">Average increase in lead-to-appointment conversions after deploying {formattedWorkflow}.</p>
                        </div>
                        <div className="p-6 bg-zinc-900 border border-zinc-800 rounded-xl">
                            <div className="text-4xl font-black text-purple-500 mb-2">0s</div>
                            <h3 className="font-bold text-lg mb-2">Delay Time</h3>
                            <p className="text-sm text-zinc-400">The exact amount of time it takes to trigger the first touchpoint. Software doesn't sleep.</p>
                        </div>
                        <div className="p-6 bg-zinc-900 border border-zinc-800 rounded-xl">
                            <div className="text-4xl font-black text-green-500 mb-2">15hrs</div>
                            <h3 className="font-bold text-lg mb-2">Time Saved Weekly</h3>
                            <p className="text-sm text-zinc-400">Estimated manual admin hours reclaimed by your team every single week.</p>
                        </div>
                    </div>
                </section>

                <section className="p-12 bg-gradient-to-r from-blue-900/40 to-purple-900/40 border border-blue-500/20 rounded-2xl text-center">
                    <h2 className="text-3xl font-bold mb-4">Ready to automate your operations?</h2>
                    <p className="text-zinc-300 mb-8 max-w-xl mx-auto">
                        Stop trying to out-work your competition. Out-systemize them. We can have your custom {formattedWorkflow} live in under 48 hours.
                    </p>
                    <button className="px-8 py-4 bg-blue-600 hover:bg-blue-700 rounded-full font-bold text-lg transition-all w-full md:w-auto">
                        Get Started with AI Service Co
                    </button>
                </section>
            </main>
        </div>
    );
}
