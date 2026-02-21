import React from 'react';
import { Metadata } from 'next';
import Link from 'next/link';
import AssessmentTool from '@/components/assessment-tool';

export const metadata: Metadata = {
    title: 'Free AI Readiness Assessment | AI Service Co',
    description: 'Calculate exactly how much revenue your business is losing to manual operations, and get a technical blueprint for the AI workflows you need to deploy.',
};

export default function AssessmentPage() {
    return (
        <div className="min-h-screen bg-[#0a0a0a] text-white">
            <nav className="py-4 px-8 text-sm text-zinc-500 border-b border-zinc-800">
                <Link href="/" className="hover:text-blue-400">Home</Link>
                <span className="mx-2">›</span>
                <span className="text-zinc-300">AI Readiness Assessment</span>
            </nav>

            <header className="py-16 px-8 text-center bg-gradient-to-b from-blue-900/10 to-transparent">
                <h1 className="text-4xl md:text-5xl font-bold mb-6 text-white">
                    Discover Your <span className="text-blue-500">AI Readiness</span> Score
                </h1>
                <p className="text-xl text-zinc-400 max-w-2xl mx-auto mb-10">
                    Takes 45 seconds. Find out exactly which AI automations your competitors are using, and get a custom blueprint for your specific business.
                </p>
            </header>

            <main className="max-w-4xl mx-auto px-8 pb-32">
                <AssessmentTool />

                <div className="mt-20 p-8 border border-zinc-800 bg-zinc-900/50 rounded-2xl flex flex-col md:flex-row gap-8 items-center text-center md:text-left">
                    <div className="text-5xl shrink-0">📈</div>
                    <div>
                        <h3 className="text-xl font-bold mb-2">Why Take the Assessment?</h3>
                        <p className="text-zinc-400 leading-relaxed">
                            Generic AI advice doesn't work for local businesses. A plumbing company needs deeply integrated emergency dispatch routing; a real estate developer needs autonomous high-ticket nurturing. Our algorithm determines exactly which <strong className="text-white">three AI automations</strong> will generate the highest immediate ROI for your specific operation.
                        </p>
                    </div>
                </div>
            </main>
        </div>
    );
}
