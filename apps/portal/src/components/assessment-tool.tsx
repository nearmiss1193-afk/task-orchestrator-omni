"use client";

import React, { useState } from 'react';

export default function AssessmentTool() {
    const [step, setStep] = useState(1);
    const [formData, setFormData] = useState({
        industry: '',
        companySize: '',
        primaryChallenge: '',
        currentCRM: '',
        email: ''
    });

    const [isSubmitting, setIsSubmitting] = useState(false);
    const [result, setResult] = useState<null | any>(null);

    const handleNext = () => setStep(s => s + 1);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsSubmitting(true);

        try {
            // Send to our new Vercel API route that uses Gemini to grade the assessment
            const res = await fetch('/api/grade-assessment', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });
            const data = await res.json();
            setResult(data);
        } catch (error) {
            console.error("Error submitting assessment:", error);
        } finally {
            setIsSubmitting(false);
        }
    };

    if (result) {
        return (
            <div className="max-w-2xl mx-auto p-8 bg-zinc-900 border border-green-500/30 rounded-2xl text-center">
                <div className="w-20 h-20 bg-green-900/50 rounded-full flex items-center justify-center mx-auto mb-6">
                    <span className="text-4xl">✅</span>
                </div>
                <h2 className="text-3xl font-bold mb-4">Your AI Readiness Score: <span className="text-green-400">{result.score}/100</span></h2>
                <p className="text-zinc-400 mb-8">{result.analysis}</p>
                <div className="p-6 bg-black/50 rounded-xl mb-8 text-left">
                    <h3 className="font-bold text-lg mb-4 text-blue-400">Top 3 Recommended AI Automations for your business:</h3>
                    <ul className="space-y-3">
                        {result.recommendations.map((rec: string, i: number) => (
                            <li key={i} className="flex gap-3 text-zinc-300">
                                <span className="text-blue-500">→</span> {rec}
                            </li>
                        ))}
                    </ul>
                </div>
                <button className="px-8 py-4 bg-blue-600 hover:bg-blue-700 rounded-full font-bold w-full transition-all">
                    Schedule Your Implementation Call
                </button>
            </div>
        );
    }

    return (
        <div className="max-w-2xl mx-auto">
            <div className="mb-8 flex justify-between items-center text-sm font-bold text-zinc-500">
                <span className={step >= 1 ? "text-blue-400" : ""}>1. Business</span>
                <span className={step >= 2 ? "text-blue-400" : ""}>2. Operations</span>
                <span className={step >= 3 ? "text-blue-400" : ""}>3. Tech Stack</span>
                <span className={step >= 4 ? "text-blue-400" : ""}>4. Results</span>
            </div>

            <form onSubmit={handleSubmit} className="p-8 bg-zinc-900 border border-zinc-800 rounded-2xl relative overflow-hidden">
                {step === 1 && (
                    <div className="space-y-6 animate-in fade-in slide-in-from-right-4">
                        <div>
                            <h2 className="text-2xl font-bold mb-2">What industry are you in?</h2>
                            <p className="text-zinc-400 mb-6">We map AI workflows differently based on your specific niche.</p>
                            <div className="grid grid-cols-2 gap-4">
                                {['Home Services (HVAC/Plumbing)', 'Professional Services (Legal/Accounting)', 'Health & Wellness (Gyms/Spas)', 'Real Estate', 'E-Commerce', 'Other'].map(ind => (
                                    <button
                                        type="button"
                                        key={ind}
                                        onClick={() => { setFormData({ ...formData, industry: ind }); handleNext(); }}
                                        className={`p-4 rounded-xl border text-left transition-all ${formData.industry === ind ? 'border-blue-500 bg-blue-900/20' : 'border-zinc-700 hover:border-zinc-500'}`}
                                    >
                                        {ind}
                                    </button>
                                ))}
                            </div>
                        </div>
                    </div>
                )}

                {step === 2 && (
                    <div className="space-y-6 animate-in fade-in slide-in-from-right-4">
                        <div>
                            <h2 className="text-2xl font-bold mb-2">What is your biggest operational bottleneck?</h2>
                            <p className="text-zinc-400 mb-6">Where is your team sinking the most manual hours?</p>
                            <div className="grid grid-cols-1 gap-4">
                                {['We miss inbound calls/leads', 'Following up with cold leads takes too long', 'Manual scheduling and calendar Tetris', 'Answering the same customer questions constantly'].map(challenge => (
                                    <button
                                        type="button"
                                        key={challenge}
                                        onClick={() => { setFormData({ ...formData, primaryChallenge: challenge }); handleNext(); }}
                                        className={`p-4 rounded-xl border text-left transition-all ${formData.primaryChallenge === challenge ? 'border-purple-500 bg-purple-900/20' : 'border-zinc-700 hover:border-zinc-500'}`}
                                    >
                                        {challenge}
                                    </button>
                                ))}
                            </div>
                        </div>
                    </div>
                )}

                {step === 3 && (
                    <div className="space-y-6 animate-in fade-in slide-in-from-right-4">
                        <div>
                            <h2 className="text-2xl font-bold mb-2">What CRM do you currently use?</h2>
                            <p className="text-zinc-400 mb-6">AI needs to integrate with your existing data.</p>
                            <input
                                type="text"
                                placeholder="e.g. GoHighLevel, Hubspot, ServiceTitan, None"
                                value={formData.currentCRM}
                                onChange={(e) => setFormData({ ...formData, currentCRM: e.target.value })}
                                className="w-full p-4 bg-black border border-zinc-700 rounded-xl text-white focus:outline-none focus:border-blue-500 mb-6"
                            />
                            <button
                                type="button"
                                onClick={handleNext}
                                disabled={!formData.currentCRM}
                                className="w-full py-4 bg-zinc-800 hover:bg-zinc-700 disabled:opacity-50 disabled:cursor-not-allowed rounded-xl font-bold transition-all"
                            >
                                Continue
                            </button>
                        </div>
                    </div>
                )}

                {step === 4 && (
                    <div className="space-y-6 animate-in fade-in slide-in-from-right-4">
                        <div className="text-center">
                            <div className="w-16 h-16 bg-blue-900/50 rounded-full flex items-center justify-center mx-auto mb-6">
                                <span className="text-2xl">🤖</span>
                            </div>
                            <h2 className="text-2xl font-bold mb-2">Your Custom AI Roadmap is Ready</h2>
                            <p className="text-zinc-400 mb-8">Enter your email to see your AI Readiness Score and receive your custom technical implementation blueprint.</p>
                            <input
                                type="email"
                                required
                                placeholder="Email address"
                                value={formData.email}
                                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                                className="w-full p-4 bg-black border border-zinc-700 rounded-xl text-white focus:outline-none focus:border-blue-500 mb-6 text-center"
                            />
                            <button
                                type="submit"
                                disabled={isSubmitting || !formData.email}
                                className="w-full py-4 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 rounded-xl font-bold transition-all relative"
                            >
                                {isSubmitting ? (
                                    <span className="flex items-center justify-center gap-2">
                                        <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                                        Generating Assessment...
                                    </span>
                                ) : "Calculate My AI Score"}
                            </button>
                        </div>
                    </div>
                )}
            </form>
        </div>
    );
}
