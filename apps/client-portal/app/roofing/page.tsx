'use client';

import { useEffect } from 'react';
import Head from 'next/head';

// John's Roofing Assistant Configuration
const JOHN_ASSISTANT_ID = "78b4c14a-b44a-4096-82f5-a10106d1bfd2";

export default function RoofingPage() {
    useEffect(() => {
        // Inject Vapi Widget
        const script = document.createElement('script');
        script.src = "https://cdn.jsdelivr.net/gh/VapiAI/html-script-tag@latest/dist/assets/index.js";
        script.defer = true;
        script.async = true;

        script.onload = () => {
            // @ts-ignore
            window.vapiSDK.run({
                apiKey: "e906c7fa-1200-47d3-83eb-c340b8a1c6a2", // Public key (using one from recent tool calls or env if available)
                assistant: JOHN_ASSISTANT_ID,
                config: {
                    position: "bottom-right",
                    offset: "40px",
                    width: "50px",
                    height: "50px",
                    idle: {
                        color: "rgb(255, 100, 50)", // Roofing orange
                        type: "pill",
                        title: "Speak with John (Roofing Expert)",
                        subtitle: "Get an instant estimate",
                        icon: "https://unpkg.com/lucide-static@0.321.0/icons/hard-hat.svg",
                    },
                    loading: {
                        color: "rgb(200, 80, 40)",
                    },
                    active: {
                        color: "rgb(255, 60, 0)",
                        type: "pill",
                        title: "John is listening...",
                        subtitle: "Ask about roof replacement or repairs",
                        icon: "https://unpkg.com/lucide-static@0.321.0/icons/mic.svg",
                    },
                },
            });
        };

        document.body.appendChild(script);

        return () => {
            document.body.removeChild(script);
        };
    }, []);

    return (
        <div className="min-h-screen bg-slate-50 text-slate-900 font-sans">
            <Head>
                <title>Roofing Estimates | Instant AI Quote</title>
            </Head>

            {/* Hero Section */}
            <header className="bg-slate-900 text-white py-20 px-6 text-center relative overflow-hidden">
                <div className="absolute inset-0 bg-orange-600/10 z-0"></div>
                <div className="relative z-10 max-w-4xl mx-auto">
                    <div className="inline-block bg-orange-600 text-white text-xs font-bold px-3 py-1 rounded-full mb-4">
                        AI-POWERED ESTIMATES
                    </div>
                    <h1 className="text-5xl font-extrabold mb-6 tracking-tight">
                        Roof Replacement Estimates <br />
                        <span className="text-orange-500">In Seconds, Not Days.</span>
                    </h1>
                    <p className="text-xl text-slate-300 mb-10 max-w-2xl mx-auto">
                        Talk to John, our AI roofing specialist. He can assess your needs, check availability,
                        and schedule a crew inspection instantly.
                    </p>
                    <div className="flex justify-center gap-4">
                        <button className="bg-orange-600 hover:bg-orange-500 text-white px-8 py-4 rounded-lg font-bold text-lg shadow-lg hover:shadow-orange-500/30 transition-all transform hover:-translate-y-1">
                            Start Estimate Online
                        </button>
                        <button className="bg-white/10 hover:bg-white/20 text-white px-8 py-4 rounded-lg font-bold text-lg border border-white/10 backdrop-blur-sm transition-all">
                            Call John: (863) 692-8548
                        </button>
                    </div>
                </div>
            </header>

            {/* Features */}
            <section className="py-20 px-6 max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-10">
                <div className="bg-white p-8 rounded-2xl shadow-sm border border-slate-100 hover:shadow-md transition-shadow">
                    <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center mb-6 text-orange-600">
                        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
                    </div>
                    <h3 className="text-xl font-bold mb-3">Instant Quotes</h3>
                    <p className="text-slate-600">No waiting for a callback. John can give you rough estimates based on your square footage and material choice immediately.</p>
                </div>
                <div className="bg-white p-8 rounded-2xl shadow-sm border border-slate-100 hover:shadow-md transition-shadow">
                    <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-6 text-blue-600">
                        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>
                    </div>
                    <h3 className="text-xl font-bold mb-3">Live Scheduling</h3>
                    <p className="text-slate-600">John connects directly to our crew's calendar. Book your inspection without playing phone tag.</p>
                </div>
                <div className="bg-white p-8 rounded-2xl shadow-sm border border-slate-100 hover:shadow-md transition-shadow">
                    <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-6 text-green-600">
                        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                    </div>
                    <h3 className="text-xl font-bold mb-3">Zero Pressure</h3>
                    <p className="text-slate-600">Get the information you need without a salesperson in your living room. John is helpful, not pushy.</p>
                </div>
            </section>

            {/* Pricing Section */}
            <section className="py-20 px-6 bg-slate-900 text-white" id="pricing">
                <div className="max-w-6xl mx-auto">
                    <div className="text-center mb-16">
                        <span className="text-orange-500 font-bold tracking-wider uppercase text-sm">Investment</span>
                        <h2 className="text-4xl font-extrabold mt-2 mb-4">Simple, Transparent Pricing</h2>
                        <p className="text-slate-400 text-lg">No contracts. Cancel anytime. 7-Day Free Trial included.</p>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                        {/* Starter */}
                        <div className="bg-slate-800 border border-slate-700 rounded-2xl p-8 flex flex-col">
                            <h3 className="text-slate-400 text-lg font-medium">Starter</h3>
                            <div className="text-4xl font-bold my-4">$99<span className="text-sm font-normal text-slate-500">/mo</span></div>
                            <ul className="space-y-4 mb-8 flex-1">
                                <li className="flex gap-3 text-slate-300"><span className="text-orange-500">✓</span> 24/7 Call Answering</li>
                                <li className="flex gap-3 text-slate-300"><span className="text-orange-500">✓</span> Missed Call Text-Back</li>
                                <li className="flex gap-3 text-slate-300"><span className="text-orange-500">✓</span> Instant Notifications</li>
                            </ul>
                            <a href="/checkout.html?plan=starter" className="block text-center py-3 border border-orange-500 text-orange-500 rounded-lg hover:bg-orange-500 hover:text-white transition-colors font-bold">Start 7-Day Trial</a>
                        </div>

                        {/* Lite (Most Popular) */}
                        <div className="bg-slate-800 border-2 border-orange-500 rounded-2xl p-8 flex flex-col relative transform md:-translate-y-4 shadow-xl shadow-orange-500/10">
                            <div className="absolute top-0 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-orange-500 text-white px-4 py-1 rounded-full text-xs font-bold uppercase">Most Popular</div>
                            <h3 className="text-slate-400 text-lg font-medium">Lite</h3>
                            <div className="text-4xl font-bold my-4">$199<span className="text-sm font-normal text-slate-500">/mo</span></div>
                            <ul className="space-y-4 mb-8 flex-1">
                                <li className="flex gap-3 text-slate-300"><span className="text-orange-500">✓</span> <strong>Everything in Starter</strong></li>
                                <li className="flex gap-3 text-slate-300"><span className="text-orange-500">✓</span> Appointment Booking</li>
                                <li className="flex gap-3 text-slate-300"><span className="text-orange-500">✓</span> 3 Custom AI Workflows</li>
                                <li className="flex gap-3 text-slate-300"><span className="text-orange-500">✓</span> CRM Integration</li>
                            </ul>
                            <a href="/checkout.html?plan=lite" className="block text-center py-3 bg-orange-600 text-white rounded-lg hover:bg-orange-500 transition-colors font-bold shadow-lg">Start 7-Day Trial</a>
                        </div>

                        {/* Growth */}
                        <div className="bg-slate-800 border border-slate-700 rounded-2xl p-8 flex flex-col">
                            <h3 className="text-slate-400 text-lg font-medium">Growth</h3>
                            <div className="text-4xl font-bold my-4">$297<span className="text-sm font-normal text-slate-500">/mo</span></div>
                            <ul className="space-y-4 mb-8 flex-1">
                                <li className="flex gap-3 text-slate-300"><span className="text-orange-500">✓</span> <strong>Everything in Lite</strong></li>
                                <li className="flex gap-3 text-slate-300"><span className="text-orange-500">✓</span> Database Reactivation</li>
                                <li className="flex gap-3 text-slate-300"><span className="text-orange-500">✓</span> Advanced Analytics</li>
                                <li className="flex gap-3 text-slate-300"><span className="text-orange-500">✓</span> Priority Support</li>
                            </ul>
                            <a href="/checkout.html?plan=growth" className="block text-center py-3 border border-orange-500 text-orange-500 rounded-lg hover:bg-orange-500 hover:text-white transition-colors font-bold">Start 7-Day Trial</a>
                        </div>
                    </div>
                </div>
            </section>

        </div>
    );
}
