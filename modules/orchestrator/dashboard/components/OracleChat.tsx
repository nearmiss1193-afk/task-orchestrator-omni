'use client';

import { useState, useRef, useEffect } from 'react';
import { Send, Bot, Loader2 } from 'lucide-react';

export default function OracleChat() {
    const [messages, setMessages] = useState<Array<{ role: 'user' | 'assistant', content: string, id: string }>>([]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [isOpen, setIsOpen] = useState(false);
    const bottomRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages, isOpen]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!input.trim() || isLoading) return;

        const userMsg = { role: 'user' as const, content: input, id: Date.now().toString() };
        setMessages(prev => [...prev, userMsg]);
        setInput('');
        setIsLoading(true);

        try {
            // Simple robust fetch to our Command Mode backend
            const res = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ messages: [...messages, userMsg] })
            });

            if (!res.ok) throw new Error(res.statusText);

            // Backend returns plain text fallback now
            const text = await res.text();

            // If backend returned JSON (old version), parse it. If text, use it.
            let reply = text;
            try {
                const json = JSON.parse(text);
                if (json.fallback) reply = json.fallback;
                if (json.content) reply = json.content;
            } catch (e) {
                // It's just text, keep 'reply' as is
            }

            setMessages(prev => [...prev, { role: 'assistant', content: reply, id: (Date.now() + 1).toString() }]);
        } catch (error) {
            setMessages(prev => [...prev, { role: 'assistant', content: "Connection Error. Try 'Status' command.", id: (Date.now() + 1).toString() }]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="fixed bottom-4 right-4 z-50">
            {!isOpen && (
                <button
                    onClick={() => setIsOpen(true)}
                    className="bg-blue-600 hover:bg-blue-700 text-white p-4 rounded-full shadow-lg transition-all"
                    aria-label="Open Oracle Chat"
                >
                    <Bot size={24} />
                </button>
            )}

            {isOpen && (
                <div className="bg-slate-900 border border-slate-700 rounded-lg shadow-2xl w-80 sm:w-96 flex flex-col h-[500px] overflow-hidden">
                    {/* Header */}
                    <div className="bg-slate-800 p-3 flex justify-between items-center border-b border-slate-700">
                        <h3 className="font-bold text-white flex items-center gap-2">
                            <Bot size={18} /> Empire Oracle
                        </h3>
                        <button onClick={() => setIsOpen(false)} className="text-slate-400 hover:text-white">x</button>
                    </div>

                    {/* Messages */}
                    <div className="flex-1 overflow-y-auto p-4 space-y-4">
                        {messages.length === 0 && (
                            <p className="text-slate-500 text-center text-sm mt-10">
                                System Online.<br />Try: Status, Social, How
                            </p>
                        )}
                        {messages.map(m => (
                            <div key={m.id} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                                <div className={`max-w-[85%] rounded-lg p-3 text-sm whitespace-pre-wrap ${m.role === 'user' ? 'bg-blue-600 text-white' : 'bg-slate-800 text-slate-200 border border-slate-700'
                                    }`}>
                                    {m.content}
                                </div>
                            </div>
                        ))}
                        {isLoading && (
                            <div className="flex justify-start">
                                <div className="bg-slate-800 p-3 rounded-lg border border-slate-700">
                                    <Loader2 className="animate-spin text-blue-500" size={16} />
                                </div>
                            </div>
                        )}
                        <div ref={bottomRef} />
                    </div>

                    {/* Input */}
                    <form onSubmit={handleSubmit} className="p-3 bg-slate-800 border-t border-slate-700 flex gap-2">
                        <input
                            className="flex-1 bg-slate-900 text-white text-sm border border-slate-700 rounded-md px-3 py-2 focus:outline-none focus:ring-1 focus:ring-blue-500"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            placeholder="Command..."
                        />
                        <button
                            type="submit"
                            disabled={isLoading}
                            className="bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white p-2 rounded-md"
                            aria-label="Send Message"
                        >
                            <Send size={18} />
                        </button>
                    </form>
                </div>
            )}
        </div>
    );
}
