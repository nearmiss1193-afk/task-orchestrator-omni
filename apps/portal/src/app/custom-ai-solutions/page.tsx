import React from 'react';
import { Metadata } from 'next';
import Link from 'next/link';

export const metadata: Metadata = {
    title: 'Custom AI Platforms & Agents | AI Service Co',
    description: 'We build bespoke AI agents, internal company dashboards, and proprietary workflow systems for enterprise and aggressive local service businesses.',
};

export default function CustomAIPillarPage() {
    const solutions = [
        { id: 'internal-dashboards', name: 'Internal Data Dashboards', icon: '📊', desc: "Consolidate your CRM, accounting, and operational data into one AI-powered command center." },
        { id: 'quote-calculators', name: 'AI Quote Calculators', icon: '🧮', desc: "Web widgets that interact with users, ask scoping questions, and generate real-time estimates." },
        { id: 'support-chatbots', name: 'Technical Support Bots', icon: '🤖', desc: "Trained on your actual product manuals to solve Tier 1 support tickets autonomously." },
        { id: 'crm-integrations', name: 'Custom CRM Integrations', icon: '🔌', desc: "Bridge GoHighLevel, Salesforce, or Hubspot with your proprietary internal software via API." },
        { id: 'lead-scoring', name: 'Predictive Lead Scoring', icon: '🎯', desc: "Machine learning models that rank your inbound pipeline based on historical conversion data." },
        { id: 'voice-synthesis', name: 'Custom Voice Cloning', icon: '🎙️', desc: "Create an AI receptionist that sounds exactly like you or your top salesperson." }
    ];

    return (
        <div className="min-h-screen bg-[#0a0a0a] text-white">
            <header className="py-24 px-8 text-center bg-gradient-to-b from-purple-900/20 to-transparent relative overflow-hidden">
                <div className="absolute top-0 right-1/4 w-96 h-96 bg-purple-600/10 blur-[100px] rounded-full" />
                <div className="absolute top-20 left-1/4 w-64 h-64 bg-blue-600/10 blur-[80px] rounded-full" />

                <div className="relative z-10">
                    <div className="inline-block px-4 py-2 border border-purple-500/30 rounded-full text-purple-400 font-bold mb-6 text-sm tracking-widest">
                        ENTERPRISE GRADE
                    </div>
                    <h1 className="text-5xl md:text-7xl font-bold mb-6 bg-gradient-to-r from-purple-400 to-blue-500 bg-clip-text text-transparent">
                        Custom AI Platforms & Agents
                    </h1>
                    <p className="text-xl text-zinc-400 max-w-3xl mx-auto mb-10">
                        Off-the-shelf software forces you to change your business to fit the tool. We build proprietary, bespoke AI infrastructure that fits your business perfectly.
                    </p>
                    <div className="flex gap-4 justify-center">
                        <button className="px-8 py-4 bg-purple-600 hover:bg-purple-700 rounded-full font-bold text-lg transition-all shadow-[0_0_30px_rgba(147,51,234,0.3)]">
                            Request Architecture Call
                        </button>
                        <button className="px-8 py-4 bg-zinc-900 border border-zinc-700 hover:bg-zinc-800 rounded-full font-bold text-lg transition-all">
                            View Case Studies
                        </button>
                    </div>
                </div>
            </header>

            <main className="max-w-6xl mx-auto px-8 py-16">
                <section className="mb-24">
                    <div className="text-center mb-16">
                        <h2 className="text-3xl font-bold mb-4">You Dream It. We Build It.</h2>
                        <p className="text-zinc-400 max-w-2xl mx-auto">Click on any core competency below to see technical implementation frameworks and estimated ROI for custom deployments.</p>
                    </div>
                    <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {solutions.map(sol => (
                            <Link href={`/custom-ai-solutions/${sol.id}`} key={sol.id} className="block group">
                                <div className="p-8 bg-zinc-900/80 border border-zinc-800 rounded-2xl hover:border-purple-500 transition-all h-full relative overflow-hidden">
                                    <div className="absolute top-0 right-0 p-4 opacity-0 group-hover:opacity-100 transition-opacity text-purple-500">
                                        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" /></svg>
                                    </div>
                                    <span className="text-5xl mb-6 block group-hover:scale-110 transition-transform origin-left">{sol.icon}</span>
                                    <h3 className="font-bold text-xl mb-3 text-white">{sol.name}</h3>
                                    <p className="text-zinc-400 leading-relaxed">{sol.desc}</p>
                                </div>
                            </Link>
                        ))}
                    </div>
                </section>

                <section className="mb-24">
                    <div className="flex flex-col md:flex-row gap-12 items-center">
                        <div className="flex-1">
                            <h2 className="text-4xl font-bold mb-6">The Development Protocol</h2>
                            <p className="text-zinc-400 leading-relaxed mb-8 text-lg">
                                Building custom AI is not about throwing prompts at an LLM. It's about secure data infrastructure, deterministic fallbacks, and rigorous latency optimization.
                            </p>
                            <ul className="space-y-6">
                                <li className="flex gap-4">
                                    <div className="w-10 h-10 rounded-full bg-purple-900/50 border border-purple-500/50 flex items-center justify-center shrink-0 font-bold">1</div>
                                    <div>
                                        <h4 className="font-bold text-lg mb-1">Architecture Mapping</h4>
                                        <p className="text-zinc-500">We audit your current data lakes and APIs to design a system that integrates natively without disruption.</p>
                                    </div>
                                </li>
                                <li className="flex gap-4">
                                    <div className="w-10 h-10 rounded-full bg-purple-900/50 border border-purple-500/50 flex items-center justify-center shrink-0 font-bold">2</div>
                                    <div>
                                        <h4 className="font-bold text-lg mb-1">Secure Vectorization (RAG)</h4>
                                        <p className="text-zinc-500">Your proprietary data is embedded into a secure vector database that the AI accesses locally. Your data is NEVER used to train public models.</p>
                                    </div>
                                </li>
                                <li className="flex gap-4">
                                    <div className="w-10 h-10 rounded-full bg-purple-900/50 border border-purple-500/50 flex items-center justify-center shrink-0 font-bold">3</div>
                                    <div>
                                        <h4 className="font-bold text-lg mb-1">Deployment & Refinement</h4>
                                        <p className="text-zinc-500">We deploy to edge networks (Vercel) or containerized architectures (Modal) for sub-second latency, monitoring every inference for quality.</p>
                                    </div>
                                </li>
                            </ul>
                        </div>
                        <div className="flex-1">
                            <div className="bg-zinc-900 border border-zinc-800 p-8 rounded-2xl font-mono text-sm text-blue-400 shadow-2xl relative">
                                <div className="absolute top-4 left-4 flex gap-2">
                                    <div className="w-3 h-3 rounded-full bg-red-500"></div>
                                    <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
                                    <div className="w-3 h-3 rounded-full bg-green-500"></div>
                                </div>
                                <div className="mt-8 space-y-4">
                                    <p className="text-purple-400"># Initializing Local Neural Network</p>
                                    <p>Loading proprietary vectors: <span className="text-green-400">[SUCCESS]</span></p>
                                    <p>Connecting CRM Webhook: <span className="text-green-400">[CONNECTED]</span></p>
                                    <p className="text-zinc-500">// Processing incoming query</p>
                                    <p className="text-white">Query = "Generate quote for 2500 sqft roof replacement"</p>
                                    <p>Agent State: <span className="text-yellow-400">ANALYZING PRICING MATRIX</span></p>
                                    <p>Response Latency: <span className="text-blue-500">412ms</span></p>
                                    <p>Output: <span className="text-green-400">[GENERATED PDF / SMS FIRED]</span></p>
                                </div>
                            </div>
                        </div>
                    </div>
                </section>
            </main>
        </div>
    );
}
