import { google } from '@ai-sdk/google';
import { streamText } from 'ai';
import { getSystemPrompt, PERSONAS } from '@/lib/prompts';
import { AgentId } from '@/lib/types';

export const maxDuration = 30;

// Mock Stream for testing without API Key
function mockStream(text: string) {
    const encoder = new TextEncoder();
    const readable = new ReadableStream({
        async start(controller) {
            const chunks = text.split(' ');
            for (const chunk of chunks) {
                controller.enqueue(encoder.encode(chunk + ' '));
                await new Promise(r => setTimeout(r, 100)); // Simulate typing delay
            }
            controller.close();
        },
    });
    return readable;
}

export async function POST(req: Request) {
    const { messages, agentId, topic, sequence } = await req.json();

    // Check for API Key
    if (!process.env.GOOGLE_GENERATIVE_AI_API_KEY) {
        console.warn("No API Key found. Using Mock Response.");
        // Return a mock stream response
        const mockResponse = `[MOCK MODE] This is a simulated response from ${agentId} about ${topic} in the ${sequence} phase. Real AI requires an API Key.`;

        // We need to return a Data Stream response format that the client expects
        // The 'ai' SDK expects a specific format (0:"text"). 
        // For simplicity in mock, just return a simple text stream if possible or construct the protocol.
        // Actually, the easiest way to mock with 'ai' sdk is using their stream helpers if available, 
        // but manually is fine too if we follow the protocol. 
        // Let's trying to just return a text response that looks right, or better yet, fail gracefully telling user to add key.

        return new Response(mockStream(mockResponse), {
            headers: { 'Content-Type': 'text/plain; charset=utf-8' }
        });
    }

    const agentIdTyped = agentId as AgentId;
    const systemPrompt = getSystemPrompt(agentIdTyped, topic);

    // Dynamic instruction based on Sequence
    let sequenceInstruction = "";
    if (sequence === 'opening') sequenceInstruction = "Give a crisp 2-sentence opening statement establishing your stance.";
    else if (sequence === 'crossfire') sequenceInstruction = "Interject aggressively! Mention another guest by description (e.g., 'The General', 'The Professor') and attack their logic.";
    else if (sequence === 'deep_dive') sequenceInstruction = "Deep Dive: Use specific BNS codes, GDP statistics, or historical treaties. Be hyper-technical.";
    else if (sequence === 'crisis') sequenceInstruction = "React to the crisis scenario presented by the host. Immediate tactical response.";
    else if (sequence === 'forecast') sequenceInstruction = "Give a 10-year prediction. Be bold and ominous or hopeful.";

    const finalSystemPrompt = `${systemPrompt}

CURRENT PHASE: ${sequence.toUpperCase()}
${sequenceInstruction}`;

    const result = await streamText({
        model: google('models/gemini-1.5-pro-latest'), // Leveraging Google Gemini 1.5 Pro
        system: finalSystemPrompt,
        messages,
        temperature: 0.8, // High creativity/aggression
    });

    return result.toDataStreamResponse();
}
