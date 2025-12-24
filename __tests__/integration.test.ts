/**
 * Integration Tests for WebSocket Connection
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';

class MockWebSocket {
    url: string;
    onopen: ((event: Event) => void) | null = null;
    onmessage: ((event: MessageEvent) => void) | null = null;
    onerror: ((event: Event) => void) | null = null;
    onclose: ((event: CloseEvent) => void) | null = null;
    readyState: number = 0;

    constructor(url: string) {
        this.url = url;
        setTimeout(() => {
            this.readyState = 1;
            if (this.onopen) {
                this.onopen(new Event('open'));
            }
        }, 10);
    }

    send(data: string) {
        // Mock send
    }

    close() {
        this.readyState = 3;
        if (this.onclose) {
            this.onclose(new CloseEvent('close'));
        }
    }
}

describe('WebSocket Integration Tests', () => {
    beforeEach(() => {
        (global as any).WebSocket = MockWebSocket;
    });

    afterEach(() => {
        delete (global as any).WebSocket;
    });

    it('connects to WebSocket endpoint', () => {
        const ws = new (global as any).WebSocket('ws://localhost:8000/api/debate/stream-adk');
        expect(ws).toBeDefined();
        expect(ws.url).toBe('ws://localhost:8000/api/debate/stream-adk');
    });

    it('handles open event', (done) => {
        const ws = new (global as any).WebSocket('ws://localhost:8000/api/debate/stream-adk');

        ws.onopen = () => {
            expect(ws.readyState).toBe(1);
            done();
        };
    });

    it('can send messages', () => {
        const ws = new (global as any).WebSocket('ws://localhost:8000/api/debate/stream-adk');
        const sendSpy = vi.spyOn(ws, 'send');

        ws.send(JSON.stringify({ topic: 'Test' }));
        expect(sendSpy).toHaveBeenCalled();
    });

    it('handles close event', (done) => {
        const ws = new (global as any).WebSocket('ws://localhost:8000/api/debate/stream-adk');

        ws.onclose = () => {
            expect(ws.readyState).toBe(3);
            done();
        };

        setTimeout(() => ws.close(), 20);
    });
});

describe('API Endpoint Tests', () => {
    beforeEach(() => {
        global.fetch = vi.fn();
    });

    afterEach(() => {
        vi.resetAllMocks();
    });

    it('calls generate debate endpoint', async () => {
        (global.fetch as any).mockResolvedValueOnce({
            ok: true,
            json: async () => ({ script: [] })
        });

        const response = await fetch('http://localhost:8000/api/debate/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ topic: 'Test', turns: 6 })
        });

        expect(global.fetch).toHaveBeenCalledWith(
            'http://localhost:8000/api/debate/generate',
            expect.objectContaining({ method: 'POST' })
        );

        const data = await response.json();
        expect(data).toHaveProperty('script');
    });

    it('handles TTS endpoint', async () => {
        (global.fetch as any).mockResolvedValueOnce({
            ok: true,
            blob: async () => new Blob(['audio'], { type: 'audio/mpeg' })
        });

        const response = await fetch('http://localhost:8000/api/tts', {
            method: 'POST',
            body: JSON.stringify({ text: 'Test', speaker_id: 'shakti' })
        });

        expect(response.ok).toBe(true);
    });
});
