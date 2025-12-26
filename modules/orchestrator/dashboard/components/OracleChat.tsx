
'use client';

import { useState } from 'react';
import { useChat } from 'ai/react';
import { Send, Bot } from 'lucide-react';
import { cn } from '@/lib/utils'; // Assuming cn utility is usually set up, but simpler to inline if needed.

export default function OracleChat() {
    const { messages, input, handleInputChange, handleSubmit } = useChat({
        api: '/api/chat',
    });
    const [isOpen, setIsOpen] = useState(false);

    return (
        <div className="fixed bottom-4 right-4 z-50">
            {!isOpen && (
                <button
                    onClick={() => setIsOpen(true)}
                    className="bg-blue-600 hover:bg-blue-700 text-white p-4 rounded-full shadow-lg transition-all"
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
                        <button
                            onClick={() => setIsOpen(false)}
                            className="text-slate-400 hover:text-white"
                        >
                            x
                        </button>
                    </div>

                    {/* Messages */}
                    <div className="flex-1 overflow-y-auto p-4 space-y-4">
                        {messages.length === 0 && (
                            <p className="text-slate-500 text-center text-sm mt-10">
                                Ask me about leads, status, or deployments.
                            </p>
                        )}
                        {messages.map(m => (
                            <div
                                key={m.id}
                                className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}
                            >
                                <div
                                    className={`max-w-[85%] rounded-lg p-3 text-sm ${m.role === 'user'
                                            ? 'bg-blue-600 text-white'
                                            : 'bg-slate-800 text-slate-200 border border-slate-700'
                                        }`}
                                >
                                    {m.content}
                                </div>
                            </div>
                        ))}
                    </div>

                    {/* Input */}
                    <form onSubmit={handleSubmit} className="p-3 bg-slate-800 border-t border-slate-700 flex gap-2">
                        <input
                            className="flex-1 bg-slate-900 text-white text-sm border border-slate-700 rounded-md px-3 py-2 focus:outline-none focus:ring-1 focus:ring-blue-500"
                            value={input}
                            onChange={handleInputChange}
                            placeholder="Ask the Oracle..."
                        />
                        <button
                            type="submit"
                            className="bg-blue-600 hover:bg-blue-700 text-white p-2 rounded-md"
                        >
                            <Send size={18} />
                        </button>
                    </form>
                </div>
            )}
        </div>
    );
}
