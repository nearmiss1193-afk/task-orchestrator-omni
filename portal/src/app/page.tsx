'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    router.push('/dashboard');
  }, [router]);

  return (
    <div className="flex min-h-screen bg-[#050505] items-center justify-center">
      <div className="text-gray-500 font-mono text-xs animate-pulse tracking-[0.4em]">
        INITIALIZING SOVEREIGN UPLINK...
      </div>
    </div>
  );
}
