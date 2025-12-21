"use client";

import React, { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Play, Pause, Activity } from 'lucide-react';

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
            audioRef.current.play();
            audioRef.current.onended = () => {
                setTimeout(() => playLine(index + 1, currentScript), 400);
            };
            audioRef.current.onerror = () => {
                console.error("Audio error", line.audio_url);
                playLine(index + 1, currentScript);
            }
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
        if (id.includes("sovereignist")) return "#FB923C"; // orange
        if (id.includes("reformist")) return "#22D3EE"; // cyan
        if (id.includes("technocrat")) return "#60A5FA"; // blue
        if (id.includes("humanist")) return "#34D399"; // emerald
        if (id.includes("shakti")) return "#C084FC"; // purple
        return "#9CA3AF"; // gray
    };

    const host = cast.find(c => c.category_id === 'shakti');
    const guests = cast.filter(c => c.category_id !== 'shakti');

    return (
        <div className="min-h-screen bg-[var(--bg-primary)] text-[var(--text-primary)] flex flex-col font-sans">

            {/* Header */}
            <header className="border-b border-[var(--bg-tertiary)] backdrop-blur-sm bg-[var(--bg-secondary)]/50">
                <div className="max-w-7xl mx-auto px-6 py-6">
                    <div className="flex items-center justify-between">
                        <div>
                            <h1 className="text-3xl font-bold tracking-tight font-[var(--font-sora,sans-serif)]">
                                CROSSFIRE
                            </h1>
                            <p className="text-sm text-[var(--text-tertiary)] mt-1">
                                AI-Powered Multi-Agent Debates
                            </p>
                        </div>
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <main className="flex-1 flex flex-col items-center justify-center px-6 py-12">

                {/* Topic Input Section */}
                {!cast.length && (
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="w-full max-w-2xl"
                    >
                        <div className="bg-[var(--bg-secondary)] rounded-2xl p-8 shadow-2xl border border-[var(--bg-tertiary)]">
                            <label className="block text-sm font-medium text-[var(--text-secondary)] mb-3">
                                What should we debate today?
                            </label>
                            <input
                                type="text"
                                value={topic}
                                onChange={(e) => setTopic(e.target.value)}
                                placeholder="Enter a debate topic..."
                                className="w-full bg-[var(--bg-tertiary)] border border-[var(--accent-muted)]/20 rounded-xl  px-6 py-4 text-lg focus:outline-none focus:border-[var(--accent-primary)] transition-colors placeholder:text-[var(--text-tertiary)]"
                                onKeyDown={(e) => e.key === 'Enter' && generatePodcast()}
                                disabled={isGenerating}
                            />
                            <button
                                onClick={generatePodcast}
                                disabled={isGenerating || !topic.trim()}
                                className="mt-4 w-full bg-[var(--accent-primary)] hover:bg-[var(--accent-primary)]/90 disabled:opacity-50 disabled:cursor-not-allowed text-white font-medium py-4 rounded-xl transition-all duration-200 flex items-center justify-center gap-2"
                            >
                                {isGenerating ? (
                                    <>
                                        <Activity className="w-5 h-5 animate-spin" />
                                        Generating Debate...
                                    </>
                                ) : (
                                    <>
                                        <Play className="w-5 h-5" fill="currentColor" />
                                        Generate Podcast
                                    </>
                                )}
                            </button>
                        </div>
                    </motion.div>
                )}

                {/* Agents Display */}
                {cast.length > 0 && (
                    <div className="w-full max-w-6xl">
                        {/* Host */}
                        {host && (
                            <motion.div
                                initial={{ opacity: 0, scale: 0.9 }}
                                animate={{ opacity: 1, scale: 1 }}
                                className="flex justify-center mb-12"
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
                            className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-8"
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            transition={{ delay: 0.2 }}
                        >
                            {guests.map((agent, idx) => (
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
                                    className="bg-[var(--bg-secondary)] hover:bg-[var(--bg-tertiary)] border border-[var(--accent-muted)]/20 rounded-full p-4 transition-all duration-200"
                                >
                                    {isPlaying ? (
                                        <Pause className="w-6 h-6" />
                                    ) : (
                                        <Play className="w-6 h-6" fill="currentColor" />
                                    )}
                                </button>
                            </div>
                        )}
                    </div>
                )}

                {/* Transcript Overlay */}
                <AnimatePresence>
                    {script[currentLineIndex] && (
                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -20 }}
                            transition={{ duration: 0.3, ease: "easeOut" }}
                            className="fixed bottom-8 left-1/2 -translate-x-1/2 w-full max-w-3xl px-6"
                        >
                            <div className="bg-[var(--bg-secondary)]/95 backdrop-blur-xl border border-[var(--bg-tertiary)] rounded-2xl p-6 shadow-2xl">
                                <p className="text-xs font-medium uppercase tracking-widest mb-2" style={{ color: getAgentColor(script[currentLineIndex].speaker) }}>
                                    {script[currentLineIndex].name}
                                </p>
                                <p className="text-lg leading-relaxed text-[var(--text-primary)]">
                                    "{script[currentLineIndex].text}"
                                </p>
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>
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
    const sizeClasses = size === "large" ? "w-40 h-40" : "w-28 h-28";
    const color = getColor(agent.category_id);

    return (
        <motion.div
            animate={{
                scale: isSpeaking ? 1.05 : 1,
            }}
            transition={{ duration: 0.2, ease: "easeOut" }}
            className="flex flex-col items-center group"
        >
            <div
                className={`${sizeClasses} rounded-full overflow-hidden transition-all duration-300 ${isSpeaking
                        ? 'ring-4 ring-offset-4 ring-offset-[var(--bg-primary)]'
                        : 'opacity-60 grayscale'
                    }`}
                style={{
                    ringColor: isSpeaking ? color : 'transparent',
                }}
            >
                <img
                    src={getAvatar(agent.category_id)}
                    alt={agent.name}
                    className="w-full h-full object-cover"
                />
            </div>
            <div className={`mt-3 text-center transition-opacity duration-300 ${isSpeaking ? 'opacity-100' : 'opacity-50'}`}>
                <p className="text-sm font-medium">{agent.name}</p>
                <p className="text-xs text-[var(--text-tertiary)] mt-0.5">{agent.sub_role}</p>
            </div>
        </motion.div>
    );
}
