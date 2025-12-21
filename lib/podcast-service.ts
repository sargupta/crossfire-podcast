import textToSpeech from '@google-cloud/text-to-speech';
import { AgentId } from './types';

// Initialize the client
// NOTE: This requires GOOGLE_APPLICATION_CREDENTIALS to be set or default credentials to be available.
const client = new textToSpeech.TextToSpeechClient();

export interface PodcastLine {
    speaker: AgentId;
    text: string;
}

// Voice configuration for each agent
const VOICE_MAP: Record<AgentId, { languageCode: string; name: string; ssmlGender: 'MALE' | 'FEMALE' }> = {
    sovereignist: {
        languageCode: 'en-IN',
        name: 'en-IN-Neural2-B', // Deep Male Indian English
        ssmlGender: 'MALE',
    },
    reformist: {
        languageCode: 'en-GB',
        name: 'en-GB-Neural2-A', // Crisp Female UK English
        ssmlGender: 'FEMALE',
    },
    technocrat: {
        languageCode: 'en-US',
        name: 'en-US-Journey-D', // Male US English (Journey voices are expressive)
        ssmlGender: 'MALE',
    },
    humanist: {
        languageCode: 'en-US',
        name: 'en-US-Neural2-F', // Soft Female US English
        ssmlGender: 'FEMALE',
    },
    shakti: {
        languageCode: 'en-IN',
        name: 'en-IN-Neural2-A', // Powerful Female Indian English
        ssmlGender: 'FEMALE',
    }
};

export async function synthesizeLine(line: PodcastLine): Promise<Buffer | null> {
    const voiceConfig = VOICE_MAP[line.speaker];
    if (!voiceConfig) {
        console.warn(`No voice config for speaker: ${line.speaker}`);
        return null;
    }

    const request = {
        input: { text: line.text },
        voice: {
            languageCode: voiceConfig.languageCode,
            name: voiceConfig.name,
            ssmlGender: voiceConfig.ssmlGender,
        },
        audioConfig: { audioEncoding: 'MP3' as const },
    };

    try {
        const [response] = await client.synthesizeSpeech(request);
        return response.audioContent as Buffer;
    } catch (error) {
        console.error(`Error synthesizing speech for ${line.speaker}:`, error);
        return null;
    }
}

/**
 * Parses a script string into structured lines.
 * Expected format: 
 * [AGENT_ID]: text content
 * [AGENT_ID]: text content
 */
export function parseScript(scriptObj: any): PodcastLine[] {
    // If the LLM returns a structured JSON array, just validate it.
    if (Array.isArray(scriptObj)) {
        return scriptObj.filter(item =>
            item && typeof item.speaker === 'string' && typeof item.text === 'string'
        ) as PodcastLine[];
    }
    return [];
}
