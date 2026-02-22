import React from 'react';
import { Metadata } from 'next';
import Link from 'next/link';

export async function generateMetadata({ params }: { params: { solution: string } }): Promise<Metadata> {
    const formattedSolution = params.solution.split('-').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');

    return {
        title: `${formattedSolution} Development | Custom AI Service Co`,
        description: `We design, train, and deploy enterprise-grade ${formattedSolution} specifically adapted to your proprietary business data and operational workflows.`,
    };
}

export default function CustomAISolutionDetailPage({ params }: { params: { solution: string } }) {
    const formattedSolution = params.solution.split('-').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');

    return (
        <div className="min-h-screen bg-[#0a0a0a] text-white">
            <nav className="py-4 px-8 text-sm text-zinc-500 border-b border-zinc-800">
                <Link href="/" className="hover:text-purple-400">Home</Link>
                <span className="mx-2">›</span>
                <Link href="/custom-ai-solutions" className="hover:text-purple-400">Custom Solutions</Link>
                <span className="mx-2">›</span>
                <span className="text-zinc-300">{formattedSolution}</span>
            </nav>

            <header className="py-24 px-8 text-center bg-zinc-900 border-b border-zinc-800 relative overflow-hidden">
                <div className="absolute top-0 right-1/4 w-96 h-96 bg-purple-600/5 blur-[100px] rounded-full" />

                <div className="relative z-10">
                    <div className="inline-block px-4 py-2 bg-purple-900/40 text-purple-400 font-bold mb-6 text-sm tracking-widest rounded-sm border border-purple-500/20">
                        DEVELOPMENT SPECIFICATION
                    </div>
                    <h1 className="text-5xl md:text-6xl font-bold mb-6 text-white">
                        {formattedSolution}
                    </h1>
                    <p className="text-xl text-zinc-400 max-w-3xl mx-auto mb-10">
                        Stop buying generic SaaS. We engineer bespoke {formattedSolution} that integrate directly into your existing architecture, turning your data into an autonomous asset.
                    </p>
                    <button className="px-10 py-4 bg-purple-600 hover:bg-purple-700 font-bold text-lg transition-all rounded-sm">
                        Request a Technical Audit
                    </button>
                </div>
            </header>

            <main className="max-w-4xl mx-auto px-8 py-20">

                {/* Tech Stack Diagram Section */}
                <section className="mb-20">
                    <h2 className="text-3xl font-bold mb-8">Standard Deployment Architecture</h2>
                    <div className="p-8 bg-[#0f0f0f] border border-zinc-800 rounded-lg font-mono text-sm leading-relaxed overflow-x-auto">
                        <div className="flex flex-col gap-4 text-zinc-400">
                            <div className="flex gap-4 items-center">
                                <div className="w-48 text-right text-purple-400 font-bold">Data Ingestion:</div>
                                <div className="p-3 bg-zinc-900 border border-zinc-800 rounded w-full">Extracts from Client CRM / APIs / Postgres</div>
                            </div>
                            <div className="flex justify-center text-zinc-600">↓</div>
                            <div className="flex gap-4 items-center">
                                <div className="w-48 text-right text-purple-400 font-bold">Vectorization (RAG):</div>
                                <div className="p-3 bg-zinc-900 border border-zinc-800 rounded w-full flex justify-between">
                                    <span>Pinecone / Supabase Vec</span>
                                    <span className="text-blue-500">Encrypted</span>
                                </div>
                            </div>
                            <div className="flex justify-center text-zinc-600">↓</div>
                            <div className="flex gap-4 items-center">
                                <div className="w-48 text-right text-purple-400 font-bold">LLM Reasoning:</div>
                                <div className="p-3 bg-zinc-900 border border-zinc-800 rounded w-full">GPT-4 Omni / Claude 3.5 Sonnet / Grok 3</div>
                            </div>
                            <div className="flex justify-center text-zinc-600">↓</div>
                            <div className="flex gap-4 items-center">
                                <div className="w-48 text-right text-green-400 font-bold">Output Execution:</div>
                                <div className="p-3 bg-zinc-900 border border-green-500/30 text-green-400 rounded w-full">Action executed in UI or sent via Webhook</div>
                            </div>
                        </div>
                    </div>
                </section>

                <section className="mb-20">
                    <h2 className="text-3xl font-bold mb-8">Why Custom Build?</h2>
                    <div className="space-y-6">
                        <div className="flex gap-6 items-start">
                            <div className="w-12 h-12 bg-zinc-900 border border-zinc-800 rounded flex items-center justify-center shrink-0">🔒</div>
                            <div>
                                <h3 className="text-xl font-bold mb-2">Data Sovereignty</h3>
                                <p className="text-zinc-400">When using off-the-shelf AI, your proprietary business data is often used to train their models. We build isolated instances where your data remains 100% private and owned by you.</p>
                            </div>
                        </div>
                        <div className="flex gap-6 items-start">
                            <div className="w-12 h-12 bg-zinc-900 border border-zinc-800 rounded flex items-center justify-center shrink-0">⚙️</div>
                            <div>
                                <h3 className="text-xl font-bold mb-2">Infinite Customization</h3>
                                <p className="text-zinc-400">Generic tools hit a wall when you need a specific feature. Because we build your API architecture from the ground up, we can integrate with any obscure software or legacy system your business runs on.</p>
                            </div>
                        </div>
                        <div className="flex gap-6 items-start">
                            <div className="w-12 h-12 bg-zinc-900 border border-zinc-800 rounded flex items-center justify-center shrink-0">📈</div>
                            <div>
                                <h3 className="text-xl font-bold mb-2">Asset Creation</h3>
                                <p className="text-zinc-400">You aren't just paying a monthly fee for software. You are investing in a proprietary AI asset that increases the enterprise value of your company.</p>
                            </div>
                        </div>
                    </div>
                </section>

                <section className="p-12 bg-zinc-900 border-l-4 border-purple-500">
                    <h2 className="text-2xl font-bold mb-4">Development Timelines</h2>
                    <p className="text-zinc-400 mb-6">
                        Custom {formattedSolution} projects typically follow a 3-week sprint cycle:
                        <br /><br />
                        <strong>Week 1:</strong> Architecture scoping and data ingestion mapping.<br />
                        <strong>Week 2:</strong> Model training, vectorization, and frontend UI design.<br />
                        <strong>Week 3:</strong> API integration, latency optimization, and live deployment.
                    </p>
                    <button className="text-purple-400 font-bold hover:text-purple-300 underline underline-offset-4">
                        Discuss Your Project Scope →
                    </button>
                </section>
            </main>
        </div>
    );
}
