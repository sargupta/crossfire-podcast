'use client';

import { Agent, AgentId } from '@/lib/types';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';
import { Mic, MicOff, BarChart2 } from 'lucide-react';

interface AgentCardProps {
    agent: Omit<Agent, 'id'> & { id: AgentId };
    isActive: boolean;
    latestMessage?: string;
}

export function AgentCard({ agent, isActive, latestMessage }: AgentCardProps) {
    return (
        <div className={cn(
            "relative flex flex-col items-center justify-end h-full w-full rounded-lg overflow-hidden border-2 bg-black",
            isActive ? "border-yellow-500 shadow-[0_0_15px_rgba(234,179,8,0.6)]" : "border-slate-800"
        )}>
            {/* "Video" Placeholder / Avatar */}
            <div className={cn("absolute inset-0 opacity-40", agent.avatar)} />

            {/* Static Noise Overlay (Optional Animation) */}
            {!isActive && (
                <div className="absolute inset-0 bg-[url('https://media.giphy.com/media/oEI9uBYSzLpBK/giphy.gif')] opacity-10 bg-cover mix-blend-overlay pointer-events-none" />
            )}

            {/* Live Indicator */}
            {isActive && (
                <div className="absolute top-2 right-2 flex items-center gap-1 bg-red-600 text-white px-2 py-0.5 rounded text-xs font-bold animate-pulse">
                    <div className="w-2 h-2 bg-white rounded-full" />
                    LIVE
                </div>
            )}

            {/* Name Plate */}
            <div className="z-10 w-full bg-gradient-to-t from-black via-black/80 to-transparent p-3 pt-10">
                <div className="flex items-center justify-between">
                    <h3 className="text-white font-bold text-sm uppercase tracking-wider">{agent.name}</h3>
                    {isActive ? <Mic className="w-4 h-4 text-red-500" /> : <MicOff className="w-4 h-4 text-gray-500" />}
                </div>
                <p className="text-xs text-gray-300 font-semibold">{agent.role}</p>

                {/* Caption / Subtitle */}
                <div className="mt-2 min-h-[60px] text-xs text-yellow-100 font-mono leading-tight">
                    {isActive && latestMessage ? (
                        <motion.span
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            className="bg-black/50 p-1 block"
                        >
                            {latestMessage.slice(-100)}...
                        </motion.span>
                    ) : (
                        <span className="text-gray-600 italic">Listening...</span>
                    )}
                </div>
            </div>
        </div>
    );
}
