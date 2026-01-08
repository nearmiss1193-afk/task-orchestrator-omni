'use client'
import { useState } from 'react'
import { supabase } from '@/lib/supabase'

export default function LoginPage() {
    const [email, setEmail] = useState('')
    const [loading, setLoading] = useState(false)
    const [msg, setMsg] = useState('')

    const handleLogin = async (e: any) => {
        e.preventDefault()
        setLoading(true)

        const { error } = await supabase.auth.signInWithOtp({
            email,
            options: {
                emailRedirectTo: `${location.origin}/auth/callback`,
            },
        })

        if (error) setMsg(error.message)
        else setMsg('Magic link sent! Check your email.')

        setLoading(false)
    }

    return (
        <main className="flex min-h-screen flex-col items-center justify-center p-24">
            <div className="z-10 max-w-md w-full items-center justify-between font-mono text-sm">
                <h1 className="text-4xl font-bold mb-8 text-center bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-600">
                    EMPIRE PORTAL
                </h1>

                <div className="bg-slate-900 p-8 rounded-xl border border-slate-800 shadow-2xl">
                    <form onSubmit={handleLogin} className="flex flex-col gap-4">
                        <label>Email Access</label>
                        <input
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            className="p-3 bg-slate-800 rounded border border-slate-700 focus:border-blue-500 outline-none"
                            placeholder="client@example.com"
                        />
                        <button
                            disabled={loading}
                            className="p-3 bg-blue-600 hover:bg-blue-700 rounded font-bold transition-all disabled:opacity-50"
                        >
                            {loading ? 'Sending...' : 'Send Magic Link'}
                        </button>
                        {msg && <p className="text-center text-sm mt-4 text-green-400">{msg}</p>}
                    </form>
                </div>
            </div>
        </main>
    )
}
