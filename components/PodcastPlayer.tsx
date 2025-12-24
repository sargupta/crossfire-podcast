"use client";

import React, { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Play, Pause, Activity, Sparkles } from 'lucide-react';

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

// Agent Color Mapping (Vivid)
const AGENT_COLORS: Record<string, string> = {
    "sovereignist": "#FF6B35",
    "reformist": "#00F5FF",
    "technocrat": "#4CC9F0",
    "humanist": "#39FF14",
    "shakti": "#FF10F0"
};

export default function PodcastPlayer({ initialTopic = "" }: PodcastPlayerProps) {
    const [topic, setTopic] = useState(initialTopic);
    const [status, setStatus] = useState<string>("Ready");
    const [isGenerating, setIsGenerating] = useState(false);
    const [isPlaying, setIsPlaying] = useState(false);
    const [cast, setCast] = useState<AgentProfile[]>([]);
    const [script, setScript] = useState<ScriptLine[]>([]);
    const [currentLineIndex, setCurrentLineIndex] = useState(-1);
    const audioRef = useRef<HTMLAudioElement | null>(null);

    const generatePodcast = async () => {
        if (!topic.trim()) return;
        setIsGenerating(true);
        setStatus("Generating...");
        setCast([]);
        setScript([]);
        setCurrentLineIndex(-1);

        try {
            const res = await fetch("http://localhost:8000/api/debate/generate", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ topic, turns: 8 }),
            });

            if (!res.ok) throw new Error("Failed to generate");

            const data = await res.json();
            setCast(data.cast);
            setScript(data.script);
            setStatus("Ready to play");

            // Auto-play
            setTimeout(() => playLine(0, data.script), 800);

        } catch (e) {
            console.error(e);
            setStatus("Error occurred");
        } finally {
            setIsGenerating(false);
        }
    };

    const playLine = (index: number, currentScript = script) => {
        if (index >= currentScript.length) {
            setIsPlaying(false);
            setStatus("Finished");
            return;
        }

        setCurrentLineIndex(index);
        setIsPlaying(true);
        const line = currentScript[index];

        if (line.audio_url && audioRef.current) {
            audioRef.current.src = line.audio_url;
            audioRef.current.play().catch(() => { });
            audioRef.current.onended = () => {
                setTimeout(() => playLine(index + 1, currentScript), 400);
            };
            audioRef.current.onerror = () => {
                playLine(index + 1, currentScript);
            };
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
        <div className="min-h-screen bg-[#0a0a0f] text-white overflow-hidden relative">

            {/* Animated Gradient Background */}
            <div className="fixed inset-0 bg-gradient-to-br from-violet-600/20 via-pink-500/20 to-cyan-500/20 animate-gradient-shift" />

            {/* Floating Particles Effect */}
            <FloatingParticles />

            {/* Header */}
            <header className="relative z-10 border-b border-white/10 backdrop-blur-md">
                <div className="max-w-7xl mx-auto px-6 py-8">
                    <motion.div
                        initial={{ y: -20, opacity: 0 }}
                        animate={{ y: 0, opacity: 1 }}
                        className="text-center"
                    >
                        <h1 className="text-7xl font-black tracking-tighter text-glow-pink font-[var(--font-sora,sans-serif)] mb-2">
                            CROSSFIRE
                        </h1>
                        <p className="text-2xl font-bold bg-gradient-to-r from-pink-400 via-purple-400 to-cyan-400 bg-clip-text text-transparent flex items-center justify-center gap-2">
                            <Sparkles className="w-6 h-6 text-pink-400" />
                            AI-Powered Debate Arena
                            <Sparkles className="w-6 h-6 text-cyan-400" />
                        </p>
                    </motion.div>
                </div>
            </header>

            {/* Main Content */}
            <main className="relative z-10 flex flex-col items-center justify-center px-6 py-12 min-h-[calc(100vh-120px)]">

                {/* Topic Input Section */}
                {!cast.length && (
                    <motion.div
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        className="w-full max-w-3xl"
                    >
                        {/* Neon Border Card */}
                        <div className="relative p-[3px] rounded-3xl bg-gradient-to-r from-pink-500 via-purple-500 to-cyan-500 animate-gradient-shift">
                            <div className="bg-[#1a1a2e] rounded-3xl p-10">
                                <label className="block text-lg font-bold text-white mb-4 text-glow-cyan">
                                    ⚡ Enter Debate Topic
                                </label>
                                <input
                                    type="text"
                                    value={topic}
                                    onChange={(e) => setTopic(e.target.value)}
                                    placeholder="What's the hot topic today?"
                                    className="w-full px-6 py-5 text-xl bg-gradient-to-r from-violet-950/50 to-purple-950/50 border-2 border-pink-500/30 focus:border-cyan-400 rounded-xl text-white placeholder:text-gray-400 transition-all duration-300 focus:shadow-[0_0_30px_rgba(0,245,255,0.3)]"
                                    onKeyDown={(e) => e.key === 'Enter' && generatePodcast()}
                                    disabled={isGenerating}
                                />
                                <button
                                    onClick={generatePodcast}
                                    disabled={isGenerating || !topic.trim()}
                                    className="mt-6 w-full px-8 py-6 bg-gradient-to-r from-pink-600 to-purple-600 hover:from-pink-500 hover:to-purple-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-bold text-xl rounded-xl shadow-[0_10px_50px_rgba(255,0,110,0.5)] transform hover:scale-105 transition-all duration-300 flex items-center justify-center gap-3"
                                >
                                    {isGenerating ? (
                                        <>
                                            <Activity className="w-6 h-6 animate-spin" />
                                            Generating Debate...
                                        </>
                                    ) : (
                                        <>
                                            <Play className="w-6 h-6" fill="currentColor" />
                                            Start Debate
                                        </>
                                    )}
                                </button>
                            </div>
                        </div>
                    </motion.div>
                )}

                {/* Agents Display */}
                {cast.length > 0 && (
                    <div className="w-full max-w-7xl">
                        {/* Host */}
                        {host && (
                            <motion.div
                                initial={{ opacity: 0, scale: 0.8 }}
                                animate={{ opacity: 1, scale: 1 }}
                                className="flex justify-center mb-16"
                            >
                                <AgentCard
                                    agent={host}
                                    isSpeaking={script[currentLineIndex]?.speaker === 'shakti' && isPlaying}
                                    getAvatar={getAvatar}
                                    getColor={getAgentColor}
                                    size="large"
                                />
                            </motion.div>
                        )}

                        {/* Guests Grid */}
                        <motion.div
                            className="grid grid-cols-2 md:grid-cols-4 gap-8 mb-12"
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            transition={{ delay: 0.3 }}
                        >
                            {guests.map((agent) => (
                                <AgentCard
                                    key={agent.category_id}
                                    agent={agent}
                                    isSpeaking={script[currentLineIndex]?.speaker === agent.category_id && isPlaying}
                                    getAvatar={getAvatar}
                                    getColor={getAgentColor}
                                    size="medium"
                                />
                            ))}
                        </motion.div>

                        {/* Playback Controls */}
                        {script.length > 0 && (
                            <div className="flex justify-center">
                                <button
                                    onClick={togglePlayback}
                                    className="bg-gradient-to-r from-pink-600 to-purple-600 hover:from-pink-500 hover:to-purple-500 rounded-full p-6 transition-all duration-300 transform hover:scale-110 shadow-[0_10px_50px_rgba(255,0,110,0.5)]"
                                >
                                    {isPlaying ? (
                                        <Pause className="w-8 h-8" />
                                    ) : (
                                        <Play className="w-8 h-8" fill="currentColor" />
                                    )}
                                </button>
                            </div>
                        )}
                    </div>
                )}

                {/* Transcript Overlay - TV Style Lower Third */}
                <AnimatePresence>
                    {script[currentLineIndex] && (
                        <motion.div
                            initial={{ y: 100, opacity: 0 }}
                            animate={{ y: 0, opacity: 1 }}
                            exit={{ y: 100, opacity: 0 }}
                            transition={{ duration: 0.4, ease: "easeOut" }}
                            className="fixed bottom-8 left-0 right-0 px-6 z-20"
                        >
                            <div className="max-w-5xl mx-auto">
                                {/* Speaker Name Tag */}
                                <div
                                    className="inline-block px-6 py-2 rounded-t-xl font-bold uppercase tracking-widest text-sm text-white"
                                    style={{
                                        background: `linear-gradient(135deg, ${getAgentColor(script[currentLineIndex].speaker)}, ${lightenColor(getAgentColor(script[currentLineIndex].speaker), 30)})`
                                    }}
                                >
                                    {script[currentLineIndex].name}
                                </div>

                                {/* Dialogue Box */}
                                <div className="relative">
                                    <div className="absolute inset-0 bg-gradient-to-r from-gray-900/95 to-black/95 rounded-b-2xl rounded-tr-2xl backdrop-blur-xl" />
                                    <div className="relative p-8">
                                        <p className="text-white text-2xl leading-relaxed font-medium">
                                            "{script[currentLineIndex].text}"
                                        </p>
                                    </div>
                                    {/* Progress Bar */}
                                    <div
                                        className="absolute bottom-0 left-0 right-0 h-1 animate-progress"
                                        style={{
                                            background: `linear-gradient(to right, ${getAgentColor(script[currentLineIndex].speaker)}, #00F5FF)`
                                        }}
                                    />
                                </div>
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>

                {/* Audio Waveform Visualization */}
                {isPlaying && <AudioWaveform />}
            </main>

            <audio ref={audioRef} className="hidden" />
        </div>
    );
}

// --- Agent Card Component ---
function AgentCard({
    agent,
    isSpeaking,
    getAvatar,
    getColor,
    size = "medium"
}: {
    agent: AgentProfile;
    isSpeaking: boolean;
    getAvatar: (id: string) => string;
    getColor: (id: string) => string;
    size?: "medium" | "large";
}) {
    const sizeClasses = size === "large" ? "w-48 h-48" : "w-36 h-36";
    const color = getColor(agent.category_id);

    return (
        <motion.div
            animate={{
                scale: isSpeaking ? 1.1 : 0.95,
            }}
            transition={{ duration: 0.3, ease: "easeOut" }}
            className="flex flex-col items-center group cursor-pointer"
        >
            <div className="relative">
                {/* Neon Glow Ring */}
                {isSpeaking && (
                    <div
                        className="absolute -inset-2 rounded-full blur-2xl animate-glow-pulse"
                        style={{ background: `radial-gradient(circle, ${color}, transparent)` }}
                    />
                )}

                {/* Avatar with Gradient Border */}
                <div
                    className={`relative ${sizeClasses} rounded-full p-1 transition-all duration-300`}
                    style={{
                        background: isSpeaking
                            ? `linear-gradient(135deg, ${color}, white)`
                            : `linear-gradient(135deg, ${color}80, ${color}40)`,
                        boxShadow: isSpeaking ? `0 0 40px ${color}` : 'none'
                    }}
                >
                    <img
                        src={getAvatar(agent.category_id)}
                        alt={agent.name}
                        className="w-full h-full rounded-full object-cover"
                    />
                </div>

                {/* Mini Waveform */}
                {isSpeaking && (
                    <div className="absolute -bottom-2 left-1/2 -translate-x-1/2 flex gap-1">
                        {[...Array(5)].map((_, i) => (
                            <div
                                key={i}
                                className="w-1 bg-white rounded-full animate-wave"
                                style={{
                                    height: `${12 + Math.random() * 12}px`,
                                    animationDelay: `${i * 0.1}s`,
                                    background: color
                                }}
                            />
                        ))}
                    </div>
                )}
            </div>

            {/* Name Tag */}
            <div className="mt-4 text-center">
                <p
                    className="text-lg font-bold transition-all duration-300"
                    style={{
                        color: isSpeaking ? color : 'white',
                        textShadow: isSpeaking ? `0 0 20px ${color}` : 'none'
                    }}
                >
                    {agent.name}
                </p>
                {isSpeaking && (
                    <div
                        className="h-1 w-16 mx-auto mt-2 rounded-full"
                        style={{
                            background: color,
                            boxShadow: `0 0 10px ${color}`
                        }}
                    />
                )}
            </div>
        </motion.div>
    );
}

// --- Floating Particles Component ---
function FloatingParticles() {
    return (
        <div className="fixed inset-0 pointer-events-none overflow-hidden">
            {[...Array(30)].map((_, i) => (
                <motion.div
                    key={i}
                    className="absolute w-2 h-2 rounded-full"
                    style={{
                        background: ['#FF006E', '#00F5FF', '#FFD60A'][i % 3],
                        left: `${Math.random() * 100}%`,
                        top: `${Math.random() * 100}%`,
                        filter: 'blur(2px)'
                    }}
                    animate={{
                        y: [0, -30, 0],
                        opacity: [0.3, 0.6, 0.3],
                    }}
                    transition={{
                        duration: 3 + Math.random() * 2,
                        repeat: Infinity,
                        delay: Math.random() * 2,
                    }}
                />
            ))}
        </div>
    );
}

// --- Audio Waveform Component ---
function AudioWaveform() {
    return (
        <div className="fixed bottom-0 left-0 right-0 h-20 bg-black/40 backdrop-blur-lg border-t border-white/10 z-10">
            <div className="flex items-end justify-center h-full gap-1 px-8">
                {[...Array(64)].map((_, i) => (
                    <div
                        key={i}
                        className="w-1.5 rounded-t-full animate-wave"
                        style={{
                            height: `${20 + Math.random() * 60}%`,
                            background: `linear-gradient(to top, #FF006E, #00F5FF)`,
                            animationDelay: `${i * 0.02}s`,
                            animationDuration: `${0.4 + Math.random() * 0.4}s`
                        }}
                    />
                ))}
            </div>
        </div>
    );
}

// --- Helper Function ---
function lightenColor(hex: string, percent: number): string {
    const num = parseInt(hex.replace("#", ""), 16);
    const amt = Math.round(2.55 * percent);
    const R = (num >> 16) + amt;
    const G = (num >> 8 & 0x00FF) + amt;
    const B = (num & 0x0000FF) + amt;
    return "#" + (
        0x1000000 +
        (R < 255 ? (R < 1 ? 0 : R) : 255) * 0x10000 +
        (G < 255 ? (G < 1 ? 0 : G) : 255) * 0x100 +
        (B < 255 ? (B < 1 ? 0 : B) : 255)
    ).toString(16).slice(1);
}
