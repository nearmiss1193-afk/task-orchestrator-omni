"use client";

import { useState, useEffect } from "react";
import { Send, User, Bot, Loader2, Phone, PhoneOff } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";
import Vapi from "@vapi-ai/web";

// Utility for tailwind class merging
function cn(...inputs: (string | undefined | null | false)[]) {
    return twMerge(clsx(inputs));
}

type Message = {
    id: string;
    role: "user" | "assistant";
    content: string;
    timestamp: Date;
};

// Vapi Configuration
const VAPI_PUBLIC_KEY = "3b065ff0-a721-4b66-8255-30b6b8d6daab";
const ASSISTANT_ID = "033ec1d3-e17d-4611-a497-b47cab1fdb4e";

export function ChatInterface() {
    const [input, setInput] = useState("");
    const [messages, setMessages] = useState<Message[]>([
        {
            id: "1",
            role: "assistant",
            content: "Welcome to Empire Unified. I am your concierge. How can I assist you today?",
            timestamp: new Date(),
        },
    ]);
    const [isLoading, setIsLoading] = useState(false);

    // Vapi State
    const [vapi, setVapi] = useState<any>(null);
    const [callStatus, setCallStatus] = useState<"idle" | "connecting" | "active">("idle");

    useEffect(() => {
        const vapiInstance = new Vapi(VAPI_PUBLIC_KEY);
        setVapi(vapiInstance);

        vapiInstance.on("call-start", () => setCallStatus("active"));
        vapiInstance.on("call-end", () => setCallStatus("idle"));
        vapiInstance.on("error", (e: any) => {
            console.error("Vapi Error:", e);
            setCallStatus("idle");
        });

        return () => {
            vapiInstance.stop();
        };
    }, []);

    const toggleCall = () => {
        if (!vapi) return;

        if (callStatus === "active") {
            vapi.stop();
            setCallStatus("idle"); // Optimistic update
        } else {
            setCallStatus("connecting");
            vapi.start(ASSISTANT_ID);
        }
    };

    const sendMessage = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!input.trim()) return;

        const userMsg: Message = {
            id: Date.now().toString(),
            role: "user",
            content: input,
            timestamp: new Date(),
        };

        setMessages((prev) => [...prev, userMsg]);
        setInput("");
        setIsLoading(true);

        try {
            const res = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: input }),
            });

            const data = await res.json();

            const aiMsg: Message = {
                id: (Date.now() + 1).toString(),
                role: "assistant",
                content: data.response || "Communication Error. Intelligence Module Offline.",
                timestamp: new Date(),
            };
            setMessages((prev) => [...prev, aiMsg]);
        } catch (err) {
            console.error(err);
            const errorMsg: Message = {
                id: (Date.now() + 1).toString(),
                role: "assistant",
                content: "Error connecting to Sovereign Brain. Check API routes.",
                timestamp: new Date(),
            };
            setMessages((prev) => [...prev, errorMsg]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="w-full max-w-md bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-xl shadow-xl overflow-hidden flex flex-col h-[600px]">
            {/* Header */}
            <div className="p-4 border-b border-zinc-200 dark:border-zinc-800 bg-zinc-50/50 dark:bg-zinc-900/50 backdrop-blur flex justify-between items-center">
                <h3 className="font-semibold flex items-center gap-2">
                    <Bot className="w-4 h-4 text-blue-500" />
                    Empire Concierge
                </h3>

                {/* Call Button */}
                <button
                    onClick={toggleCall}
                    aria-label={callStatus === "active" ? "End Call" : "Call Office Manager"}
                    className={cn(
                        "p-2 rounded-full transition-all duration-300 flex items-center gap-2 text-sm font-medium",
                        callStatus === "active"
                            ? "bg-red-500/10 text-red-500 hover:bg-red-500/20"
                            : "bg-green-500/10 text-green-500 hover:bg-green-500/20"
                    )}
                >
                    {callStatus === "connecting" ? (
                        <Loader2 className="w-4 h-4 animate-spin" />
                    ) : callStatus === "active" ? (
                        <>
                            <PhoneOff className="w-4 h-4" />
                            <span>End</span>
                        </>
                    ) : (
                        <>
                            <Phone className="w-4 h-4" />
                            <span>Call Agent</span>
                        </>
                    )}
                </button>
            </div>

            {/* Chat Area */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
                <AnimatePresence initial={false}>
                    {messages.map((message) => (
                        <motion.div
                            key={message.id}
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, scale: 0.9 }}
                            className={cn(
                                "flex w-full",
                                message.role === "user" ? "justify-end" : "justify-start"
                            )}
                        >
                            <div
                                className={cn(
                                    "max-w-[80%] rounded-2xl px-4 py-2 text-sm",
                                    message.role === "user"
                                        ? "bg-blue-600 text-white rounded-br-none"
                                        : "bg-zinc-100 dark:bg-zinc-800 text-zinc-900 dark:text-zinc-100 rounded-bl-none"
                                )}
                            >
                                {message.content}
                            </div>
                        </motion.div>
                    ))}
                </AnimatePresence>
                {isLoading && (
                    <motion.div
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="flex justify-start"
                    >
                        <div className="bg-zinc-100 dark:bg-zinc-800 rounded-2xl rounded-bl-none px-4 py-2">
                            <Loader2 className="w-4 h-4 animate-spin text-zinc-500" />
                        </div>
                    </motion.div>
                )}
            </div>

            {/* Input Area */}
            <form onSubmit={sendMessage} className="p-4 border-t border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900">
                <div className="relative">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder="Type your request..."
                        className="w-full bg-zinc-100 dark:bg-zinc-800 border-none rounded-full px-4 py-3 pr-12 text-sm focus:ring-2 focus:ring-blue-500 outline-none"
                    />
                    <button
                        type="submit"
                        aria-label="Send message"
                        disabled={isLoading || !input.trim()}
                        className="absolute right-1 top-1 p-2 bg-blue-600 text-white rounded-full hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                        <Send className="w-4 h-4" />
                    </button>
                </div>
            </form>
        </div>
    );
}
