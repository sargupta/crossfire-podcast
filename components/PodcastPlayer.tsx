"use client";

import React, { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Play, Pause, Mic2, Sparkles, Zap, Radio } from 'lucide-react';

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

// Agent Color Mapping (BOLD)
const AGENT_COLORS: Record<string, string> = {
    "sovereignist": "#FF6B35",
    "reformist": "#00F5FF",
    "technocrat": "#4CC9F0",
    "humanist": "#39FF14",
    "shakti": "#FF10F0"
};

// Suggested topics
const SUGGESTED_TOPICS = [
    "AI replacing human jobs",
    "Future of cryptocurrency",
    "Climate change solutions",
    "Social media impact",
];

export default function PodcastPlayer({ initialTopic = "" }: PodcastPlayerProps) {
    const [topic, setTopic] = useState(initialTopic);
    const [isGenerating, setIsGenerating] = useState(false);
    const [isPlaying, setIsPlaying] = useState(false);
    const [cast, setCast] = useState<AgentProfile[]>([]);
    const [script, setScript] = useState<ScriptLine[]>([]);
    const [currentLineIndex, setCurrentLineIndex] = useState(-1);
    const audioRef = useRef<HTMLAudioElement | null>(null);

    const generatePodcast = async () => {
        if (!topic.trim()) return;
        setIsGenerating(true);
        setCast([
            { category_id: 'shakti', name: 'Shakti', sub_role: 'Moderator', credential: 'Host', behavior: 'Aggressive' },
            { category_id: 'sovereignist', name: 'Sovereignist', sub_role: 'Traditionalist', credential: 'Defender', behavior: 'Conservative' },
            { category_id: 'reformist', name: 'Reformist', sub_role: 'Revolutionary', credential: 'Disruptor', behavior: 'Progressive' },
            { category_id: 'technocrat', name: 'Technocrat', sub_role: 'Analyst', credential: 'Scientist', behavior: 'Logical' },
            { category_id: 'humanist', name: 'Humanist', sub_role: 'Advocate', credential: 'Activist', behavior: 'Emotional' }
        ]);
        setScript([]);
        setCurrentLineIndex(-1);

        const ws = new WebSocket("ws://localhost:8000/api/debate/stream-production");

        ws.onopen = () => {
            ws.send(JSON.stringify({ topic, turns: 6 }));
        };

        ws.onmessage = async (event) => {
            const data = JSON.parse(event.data);

            if (data.type === 'intro' || data.type === 'turn' || data.type === 'conclusion') {
                // Fetch audio for the line
                try {
                    const ttsRes = await fetch("http://localhost:8000/api/tts", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ text: data.text, speaker_id: data.speaker })
                    });

                    if (ttsRes.ok) {
                        const blob = await ttsRes.blob();
                        const audioUrl = URL.createObjectURL(blob);

                        setScript(prev => {
                            const newLine = {
                                speaker: data.speaker,
                                text: data.text,
                                name: data.agent_name || data.speaker,
                                audio_url: audioUrl
                            };

                            // Auto-play if it's the first line or we're caught up
                            if (prev.length === 0 && !isPlaying) {
                                setTimeout(() => playLine(0, [newLine]), 500);
                            }

                            return [...prev, newLine];
                        });
                    }
                } catch (e) {
                    console.error("TTS Error:", e);
                }
            } else if (data.type === 'complete') {
                setIsGenerating(false);
                ws.close();
            } else if (data.type === 'error') {
                console.error("Stream Error:", data.message);
                setIsGenerating(false);
                ws.close();
            }
        };

        ws.onerror = (e) => {
            console.error("WebSocket Error:", e);
            setIsGenerating(false);
        };
    };

    const playLine = (index: number, currentScript = script) => {
        if (index >= currentScript.length) {
            setIsPlaying(false);
            return;
        }
        setCurrentLineIndex(index);
        setIsPlaying(true);
        const line = currentScript[index];
        if (line.audio_url && audioRef.current) {
            audioRef.current.src = line.audio_url;
            audioRef.current.play().catch(() => { });
            audioRef.current.onended = () => setTimeout(() => playLine(index + 1, currentScript), 400);
            audioRef.current.onerror = () => playLine(index + 1, currentScript);
        } else {
            setTimeout(() => playLine(index + 1, currentScript), 1800);
        }
    };

    const togglePlayback = () => {
        if (!audioRef.current) return;
        if (isPlaying) {
            audioRef.current.pause();
            setIsPlaying(false);
        } else {
            audioRef.current.play();
            setIsPlaying(true);
        }
    };

    const getAvatar = (id: string) => {
        const key = id.toLowerCase();
        if (key.includes("sovereignist")) return AVATAR_MAP.sovereignist;
        if (key.includes("reformist")) return AVATAR_MAP.reformist;
        if (key.includes("technocrat")) return AVATAR_MAP.technocrat;
        if (key.includes("humanist")) return AVATAR_MAP.humanist;
        if (key.includes("shakti")) return AVATAR_MAP.shakti;
        return "/images/shakti.png";
    };

    const getAgentColor = (id: string) => {
        const key = id.toLowerCase();
        if (key.includes("sovereignist")) return AGENT_COLORS.sovereignist;
        if (key.includes("reformist")) return AGENT_COLORS.reformist;
        if (key.includes("technocrat")) return AGENT_COLORS.technocrat;
        if (key.includes("humanist")) return AGENT_COLORS.humanist;
        if (key.includes("shakti")) return AGENT_COLORS.shakti;
        return "#9CA3AF";
    };

    const host = cast.find(c => c.category_id === 'shakti');
    const guests = cast.filter(c => c.category_id !== 'shakti');

    return (
        <div className="min-h-screen relative overflow-hidden">

            {/* BOLD Gradient Background - Always Visible */}
            <div className="fixed inset-0 bg-gradient-to-br from-purple-600 via-pink-600 to-orange-500" />
            <div className="fixed inset-0 bg-gradient-to-tl from-cyan-500 via-blue-600 to-purple-700 opacity-70 mix-blend-multiply" />
            <div className="fixed inset-0 bg-black/20" />

            {/* Grid Pattern Overlay */}
            <div className="fixed inset-0 opacity-10" style={{
                backgroundImage: 'radial-gradient(circle, white 1px, transparent 1px)',
                backgroundSize: '50px 50px'
            }} />

            <div className="relative z-10">
                {/* Compact Header */}
                <header className="bg-black/40 backdrop-blur-xl border-b border-white/20">
                    <div className="max-w-7xl mx-auto px-6 py-6 flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <div className="w-12 h-12 rounded-full bg-gradient-to-r from-pink-500 to-purple-500 flex items-center justify-center">
                                <Mic2 className="w-6 h-6 text-white" />
                            </div>
                            <div>
                                <h1 className="text-3xl font-black text-white">CROSSFIRE</h1>
                                <p className="text-sm text-pink-300">AI Debate Arena</p>
                            </div>
                        </div>
                        <div className="flex gap-2">
                            <div className="px-4 py-2 bg-white/10 backdrop-blur rounded-full text-white text-sm font-medium">
                                <Sparkles className="w-4 h-4 inline mr-1" />
                                Live
                            </div>
                        </div>
                    </div>
                </header>

                {!cast.length ? (
                    /* Landing View - FILL THE SCREEN */
                    <main className="min-h-[calc(100vh-88px)] px-6 py-12">
                        <div className="max-w-6xl mx-auto">
                            {/* Hero Section */}
                            <motion.div
                                initial={{ y: 20, opacity: 0 }}
                                animate={{ y: 0, opacity: 1 }}
                                className="text-center mb-12"
                            >
                                <h2 className="text-6xl md:text-8xl font-black text-white mb-6 leading-tight">
                                    Start Your
                                    <br />
                                    <span className="bg-gradient-to-r from-pink-400 via-purple-400 to-cyan-400 bg-clip-text text-transparent">
                                        AI Debate
                                    </span>
                                </h2>
                                <p className="text-2xl text-white/90 font-medium">
                                    5 AI agents. Unlimited perspectives. One epic discussion.
                                </p>
                            </motion.div>

                            {/* Input Section - BIGGER */}
                            <motion.div
                                initial={{ scale: 0.9, opacity: 0 }}
                                animate={{ scale: 1, opacity: 1 }}
                                transition={{ delay: 0.2 }}
                                className="mb-12"
                            >
                                <div className="bg-white/95 backdrop-blur-xl rounded-3xl p-8 shadow-2xl">
                                    <input
                                        type="text"
                                        value={topic}
                                        onChange={(e) => setTopic(e.target.value)}
                                        placeholder="Enter any topic... (e.g., 'Future of AI')"
                                        className="w-full px-6 py-6 text-2xl font-medium bg-transparent border-none outline-none text-gray-900 placeholder:text-gray-400"
                                        onKeyDown={(e) => e.key === 'Enter' && generatePodcast()}
                                        disabled={isGenerating}
                                    />
                                    <button
                                        onClick={generatePodcast}
                                        disabled={isGenerating || !topic.trim()}
                                        className="mt-4 w-full px-8 py-6 bg-gradient-to-r from-pink-600 via-purple-600 to-cyan-600 hover:from-pink-500 hover:via-purple-500 hover:to-cyan-500 disabled:opacity-50 text-white font-bold text-2xl rounded-2xl shadow-2xl transform hover:scale-105 transition-all duration-300"
                                    >
                                        {isGenerating ? (
                                            "Generating Debate..."
                                        ) : (
                                            <>
                                                <Play className="inline w-7 h-7 mr-2" fill="currentColor" />
                                                Generate Podcast
                                            </>
                                        )}
                                    </button>
                                </div>
                            </motion.div>

                            {/* Suggested Topics */}
                            <motion.div
                                initial={{ y: 20, opacity: 0 }}
                                animate={{ y: 0, opacity: 1 }}
                                transition={{ delay: 0.4 }}
                                className="mb-12"
                            >
                                <p className="text-white/70 text-sm font-medium mb-4">Try these topics:</p>
                                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                                    {SUGGESTED_TOPICS.map((topic, idx) => (
                                        <button
                                            key={idx}
                                            onClick={() => setTopic(topic)}
                                            className="px-4 py-3 bg-white/10 hover:bg-white/20 backdrop-blur rounded-xl text-white text-sm font-medium transition-all"
                                        >
                                            {topic}
                                        </button>
                                    ))}
                                </div>
                            </motion.div>

                            {/* Agent Preview - ALWAYS VISIBLE */}
                            <motion.div
                                initial={{ y: 20, opacity: 0 }}
                                animate={{ y: 0, opacity: 1 }}
                                transition={{ delay: 0.6 }}
                            >
                                <h3 className="text-2xl font-bold text-white mb-6 flex items-center gap-2">
                                    <Zap className="w-6 h-6 text-yellow-400" />
                                    Meet Your Debaters
                                </h3>
                                <div className="grid grid-cols-2 md:grid-cols-5 gap-6">
                                    {Object.entries(AVATAR_MAP).map(([id, avatar], idx) => (
                                        <motion.div
                                            key={id}
                                            initial={{ scale: 0.8, opacity: 0 }}
                                            animate={{ scale: 1, opacity: 1 }}
                                            transition={{ delay: 0.7 + idx * 0.1 }}
                                            className="group"
                                        >
                                            <div className="relative">
                                                <div
                                                    className="absolute -inset-1 rounded-full blur-lg opacity-75 group-hover:opacity-100 transition"
                                                    style={{ background: AGENT_COLORS[id] || '#fff' }}
                                                />
                                                <div
                                                    className="relative w-full aspect-square rounded-full p-1"
                                                    style={{ background: `linear-gradient(135deg, ${AGENT_COLORS[id]}, white)` }}
                                                >
                                                    <img src={avatar} className="w-full h-full rounded-full object-cover" />
                                                </div>
                                            </div>
                                            <p className="mt-3 text-center text-white font-semibold capitalize">{id}</p>
                                        </motion.div>
                                    ))}
                                </div>
                            </motion.div>
                        </div>
                    </main>
                ) : (
                    /* Debate View */
                    <main className="min-h-[calc(100vh-88px)] px-6 py-12">
                        <div className="max-w-7xl mx-auto">
                            {host && (
                                <div className="flex justify-center mb-12">
                                    <AgentCard agent={host} isSpeaking={script[currentLineIndex]?.speaker === 'shakti' && isPlaying} getAvatar={getAvatar} getColor={getAgentColor} size="large" />
                                </div>
                            )}
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-8 mb-12">
                                {guests.map((agent) => (
                                    <AgentCard key={agent.category_id} agent={agent} isSpeaking={script[currentLineIndex]?.speaker === agent.category_id && isPlaying} getAvatar={getAvatar} getColor={getAgentColor} size="medium" />
                                ))}
                            </div>
                            {script.length > 0 && (
                                <div className="flex justify-center">
                                    <button onClick={togglePlayback} className="bg-white text-black rounded-full p-6 shadow-2xl hover:scale-110 transition">
                                        {isPlaying ? <Pause className="w-8 h-8" /> : <Play className="w-8 h-8" fill="currentColor" />}
                                    </button>
                                </div>
                            )}
                        </div>
                    </main>
                )}

                {/* Transcript */}
                <AnimatePresence>
                    {script[currentLineIndex] && (
                        <motion.div
                            initial={{ y: 100, opacity: 0 }}
                            animate={{ y: 0, opacity: 1 }}
                            exit={{ y: 100, opacity: 0 }}
                            className="fixed bottom-8 left-0 right-0 px-6 z-20"
                        >
                            <div className="max-w-5xl mx-auto">
                                <div className="bg-white/95 backdrop-blur-xl rounded-2xl p-8 shadow-2xl">
                                    <p className="font-bold text-sm uppercase mb-2" style={{ color: getAgentColor(script[currentLineIndex].speaker) }}>
                                        {script[currentLineIndex].name}
                                    </p>
                                    <p className="text-gray-900 text-xl leading-relaxed">
                                        "{script[currentLineIndex].text}"
                                    </p>
                                </div>
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>
            </div>

            <audio ref={audioRef} className="hidden" />
        </div>
    );
}

function AgentCard({ agent, isSpeaking, getAvatar, getColor, size = "medium" }: any) {
    const sizeClasses = size === "large" ? "w-48 h-48" : "w-32 h-32";
    const color = getColor(agent.category_id);
    return (
        <motion.div animate={{ scale: isSpeaking ? 1.1 : 1 }} className="flex flex-col items-center">
            <div className="relative">
                {isSpeaking && <div className="absolute -inset-2 rounded-full blur-xl animate-pulse" style={{ background: color }} />}
                <div className={`relative ${sizeClasses} rounded-full p-1`} style={{ background: `linear-gradient(135deg, ${color}, white)` }}>
                    <img src={getAvatar(agent.category_id)} className="w-full h-full rounded-full object-cover" />
                </div>
            </div>
            <p className="mt-3 text-white font-bold" style={{ color: isSpeaking ? color : 'white' }}>{agent.name}</p>
        </motion.div>
    );
}
