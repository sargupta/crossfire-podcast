export type AgentId = 'sovereignist' | 'reformist' | 'technocrat' | 'humanist' | 'shakti';

export interface Agent {
  id: AgentId;
  name: string;
  role: string;
  avatar: string; // Color code or image path
  ideology: string;
  systemPrompt: string;
}

export type SequenceType = 'opening' | 'crossfire' | 'deep_dive' | 'crisis' | 'forecast';

export interface DebateState {
  sequence: SequenceType;
  topic: string;
  isActive: boolean;
  turnCount: number;
  decibelLevel: number; // 0-100
  history: Message[];
  activeSpeakerId: AgentId | 'host' | null;
}

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  speakerId: AgentId | 'host';
  content: string;
  timestamp: number;
  sequence: SequenceType;
}

export const SEQUENCES: SequenceType[] = [
  'opening',
  'crossfire',
  'deep_dive',
  'crisis',
  'forecast'
];
