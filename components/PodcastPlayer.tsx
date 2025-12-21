"use client";

import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Mic, Play, Square, Users, Radio, Activity, Volume2, Globe } from 'lucide-react';

// --- Types ---
interface AgentProfile {
    category_id: string;
    name: string;
    sub_role: string;
    credential: string;
    behavior: string;
}

interface ScriptLine {
    speaker: string;
    text: string;
    name: string;
    audio_url?: string;
}

interface PodcastPlayerProps {
    initialTopic?: string;
}

// --- Asset Mapping ---
const AVATAR_MAP: Record<string, string> = {
    "sovereignist": "/images/sovereignist.png",
    "reformist": "/images/reformist.png",
    "technocrat": "/images/technocrat.png",
    "humanist": "/images/humanist.png",
    "shakti": "/images/shakti.png"
};

export default function PodcastPlayer({ initialTopic = "" }: PodcastPlayerProps) {
    const [topic, setTopic] = useState(initialTopic);
    const [status, setStatus] = useState<string>("Ready to Broadcast");
    const [isGenerating, setIsGenerating] = useState(false);
    const [isPlaying, setIsPlaying] = useState(false);
    const [cast, setCast] = useState<AgentProfile[]>([]);
    const [script, setScript] = useState<ScriptLine[]>([]);
    const [currentLineIndex, setCurrentLineIndex] = useState(-1);
    const audioRef = useRef<HTMLAudioElement | null>(null);

    const generatePodcast = async () => {
        if (!topic.trim()) return;
        setIsGenerating(true);
        setStatus("Establishing Uplink...");
        setCast([]);
        setScript([]);
        setCurrentLineIndex(-1);

        try {
            setStatus("Casting & Producing Entire Episode (Please Wait)...");
            const res = await fetch("http://localhost:8000/api/debate/generate", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ topic, turns: 8 }),
            });

            if (!res.ok) throw new Error("Production Failed");

            const data = await res.json();
            setCast(data.cast);
            setScript(data.script);
            setStatus("Production Complete. Starting Stream...");

            // Auto-play
            setTimeout(() => playLine(0, data.script), 1000);

        } catch (e) {
            console.error(e);
            setStatus("Connection Lost.");
        } finally {
            setIsGenerating(false);
        }
    };

    const playLine = (index: number, currentScript = script) => {
        if (index >= currentScript.length) {
            setIsPlaying(false);
            setStatus("Broadcast Ended.");
            return;
        }

        setCurrentLineIndex(index);
        setIsPlaying(true);
        const line = currentScript[index];

        setStatus(`Speaking: ${line.name}`);

        if (line.audio_url && audioRef.current) {
            audioRef.current.src = line.audio_url;
            audioRef.current.play();
            audioRef.current.onended = () => {
                setTimeout(() => playLine(index + 1, currentScript), 500);
            };
            audioRef.current.onerror = () => {
                console.error("Audio Playback Error", line.audio_url);
                playLine(index + 1, currentScript);
            }
        } else {
            // Fallback or skip if no audio
            setTimeout(() => playLine(index + 1, currentScript), 2000);
        }
    };

    // Helper to get agent image or default
    const getAvatar = (id: string) => {
        const key = id.toLowerCase();
        if (key.includes("sovereignist")) return AVATAR_MAP.sovereignist;
        if (key.includes("reformist")) return AVATAR_MAP.reformist;
        if (key.includes("technocrat")) return AVATAR_MAP.technocrat;
        if (key.includes("humanist")) return AVATAR_MAP.humanist;
        if (key.includes("shakti")) return AVATAR_MAP.shakti;
        return "/images/shakti.png"; // Default
    };

    // Helper for Glow Colors
    const getGlowColor = (id: string) => {
        const key = id.toLowerCase();
        if (key.includes("sovereignist")) return "shadow-orange-500 border-orange-500";
        if (key.includes("reformist")) return "shadow-cyan-500 border-cyan-500";
        if (key.includes("technocrat")) return "shadow-blue-500 border-blue-600";
        if (key.includes("humanist")) return "shadow-emerald-500 border-emerald-500";
        if (key.includes("shakti")) return "shadow-purple-500 border-purple-500";
        return "shadow-white border-white";
    }

    return (
        <div className="flex flex-col h-screen bg-black text-white font-sans overflow-hidden relative">

            {/* Immersive Background */}
            <div className="absolute inset-0 z-0">
                <img
                    src="/images/studio_bg.png"
                    alt="Studio"
                    className="w-full h-full object-cover opacity-60"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black via-black/50 to-transparent" />
            </div>

            {/* --- Header --- */}
            <header className="flex items-center justify-between px-8 py-4 z-50 relative">
                <div className="flex items-center space-x-3 bg-black/40 backdrop-blur-md px-4 py-2 rounded-full border border-white/10">
                    <Globe className="text-red-600 animate-pulse" size={20} />
                    <h1 className="text-xl font-black tracking-tighter text-white uppercase italic">
                        CROSSFIRE <span className="text-red-600">PODCAST</span>
                    </h1>
                </div>

                <div className="flex items-center space-x-2 max-w-xl w-full mx-auto">
                    <input
                        type="text"
                        value={topic}
                        onChange={(e) => setTopic(e.target.value)}
                        placeholder="Enter Global Topic..."
                        className="w-full bg-black/60 backdrop-blur-md border border-white/20 rounded-full py-3 px-6 text-sm focus:outline-none focus:border-blue-500 transition-all text-center tracking-wide shadow-2xl"
                        onKeyDown={(e) => e.key === 'Enter' && generatePodcast()}
                    />
                    <button
                        onClick={generatePodcast}
                        disabled={isGenerating}
                        className="bg-blue-600 hover:bg-blue-500 text-white p-3 rounded-full transition-all shadow-[0_0_15px_rgba(37,99,235,0.5)] disabled:opacity-50"
                    >
                        {isGenerating ? <Activity className="animate-spin" /> : <Play fill="currentColor" />}
                    </button>
                </div>

                <div className="w-[150px] text-right">
                    <span className="text-xs font-mono text-emerald-400 drop-shadow-md">{status}</span>
                </div>
            </header>

            {/* --- Main Visual Stage --- */}
            <main className="flex-1 relative z-10 flex flex-col items-center justify-center p-4">

                {/* Host (Center) */}
                <div className="absolute bottom-10 left-1/2 -translate-x-1/2 z-20">
                    {cast.find(c => c.category_id === 'shakti') && (
                        <AgentVisual
                            agent={cast.find(c => c.category_id === 'shakti')!}
                            isSpeaking={script[currentLineIndex]?.speaker === 'shakti' && isPlaying}
                            isHost={true}
                        />
                    )}
                </div>

                {/* Guests (Grid) */}
                {cast.length > 0 ? (
                    <div className="grid grid-cols-4 gap-8 w-full max-w-6xl mb-24">
                        {cast.filter(c => c.category_id !== 'shakti').map((agent) => (
                            <div key={agent.category_id} className="flex justify-center">
                                <AgentVisual
                                    agent={agent}
                                    isSpeaking={script[currentLineIndex]?.speaker === agent.category_id && isPlaying}
                                />
                            </div>
                        ))}
                    </div>
                ) : (
                    <div className="text-white/30 text-2xl font-thin tracking-[1em] uppercase animate-pulse">
                        Studio Offline
                    </div>
                )}

            </main>

            {/* --- Dynamic Transcript Overlay --- */}
            <AnimatePresence>
                {script[currentLineIndex] && (
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -20 }}
                        className="absolute bottom-32 left-1/2 -translate-x-1/2 w-full max-w-3xl z-50 text-center"
                    >
                        <div className="bg-black/70 backdrop-blur-xl border border-white/10 p-6 rounded-2xl shadow-2xl">
                            <h3 className={`text-sm font-bold uppercase tracking-widest mb-2 ${getAgentColorText(script[currentLineIndex].speaker)}`}>
                                {script[currentLineIndex].name}
                            </h3>
                            <p className="text-xl md:text-2xl font-light leading-relaxed text-white drop-shadow-lg">
                                "{script[currentLineIndex].text}"
                            </p>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>

            <audio ref={audioRef} className="hidden" />
        </div>
    );

    function AgentVisual({ agent, isSpeaking, isHost = false }: { agent: AgentProfile, isSpeaking: boolean, isHost?: boolean }) {
        const glow = getGlowColor(agent.category_id);

        return (
            <motion.div
                animate={{
                    scale: isSpeaking ? 1.1 : 1,
                    y: isSpeaking ? -10 : 0
                }}
                className={`relative flex flex-col items-center group transition-all duration-500`}
            >
                <div className={`
                  relative rounded-2xl overflow-hidden border-2 transition-all duration-300
                  ${isHost ? 'w-48 h-48 md:w-64 md:h-64' : 'w-32 h-32 md:w-40 md:h-40'}
                  ${isSpeaking ? `border-opacity-100 shadow-[0_0_50px_rgba(var(--tw-shadow-color),0.8)] ${glow}` : 'border-white/20 grayscale opacity-70'}
              `}>
                    <img
                        src={getAvatar(agent.category_id)}
                        alt={agent.name}
                        className="w-full h-full object-cover"
                    />
                    {/* Overlay for Info */}
                    <div className="absolute inset-0 bg-gradient-to-t from-black/90 to-transparent opacity-0 group-hover:opacity-100 transition-opacity flex flex-col justify-end p-2">
                        <p className="text-[10px] uppercase font-bold text-white">{agent.sub_role}</p>
                    </div>
                </div>

                {/* Name Tag */}
                <div className={`mt-3 px-4 py-1 rounded-full bg-black/80 backdrop-blur border border-white/10 ${isSpeaking ? 'opacity-100' : 'opacity-50'}`}>
                    <span className="text-xs font-bold uppercase tracking-wider">{agent.name}</span>
                </div>
            </motion.div>
        )
    }

    function getAgentColorText(id: string) {
        if (id.includes("sovereignist")) return "text-orange-400";
        if (id.includes("reformist")) return "text-cyan-400";
        if (id.includes("technocrat")) return "text-blue-400";
        if (id.includes("humanist")) return "text-emerald-400";
        if (id.includes("shakti")) return "text-purple-400";
        return "text-gray-400";
    }
}
