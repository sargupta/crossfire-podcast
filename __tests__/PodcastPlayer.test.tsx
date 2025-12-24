/**
 * Unit Tests for PodcastPlayer Component
 * @jest-environment jsdom
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import PodcastPlayer from '../components/PodcastPlayer';

describe('PodcastPlayer Component', () => {
    it('renders without crashing', () => {
        render(<PodcastPlayer initialTopic="Test Topic" />);
        expect(screen.getByText(/CROSSFIRE/i)).toBeInTheDocument();
    });

    it('displays the initial topic', () => {
        const topic = "AI in Healthcare";
        render(<PodcastPlayer initialTopic={topic} />);

        const input = screen.getByPlaceholderText(/debate topic/i);
        expect(input).toHaveValue(topic);
    });

    it('allows changing the topic input', () => {
        render(<PodcastPlayer initialTopic="" />);

        const input = screen.getByPlaceholderText(/debate topic/i);
        fireEvent.change(input, { target: { value: 'New Topic' } });

        expect(input).toHaveValue('New Topic');
    });

    it('has generate podcast button', () => {
        render(<PodcastPlayer initialTopic="Test" />);

        const button = screen.getByRole('button', { name: /generate podcast/i });
        expect(button).toBeInTheDocument();
    });

    it('displays suggested topics', () => {
        render(<PodcastPlayer initialTopic="" />);

        // Check for at least one suggested topic
        expect(screen.getByText(/AI/)).toBeInTheDocument();
    });
});

describe('PodcastPlayer API Integration', () => {
    beforeEach(() => {
        // Mock fetch
        global.fetch = jest.fn();
    });

    afterEach(() => {
        jest.resetAllMocks();
    });

    it('handles successful API response', async () => {
        const mockResponse = {
            script: [
                { speaker: 'shakti', text: 'Welcome!', name: 'Shakti' }
            ]
        };

        (global.fetch as jest.Mock).mockResolvedValueOnce({
            ok: true,
            json: async () => mockResponse
        });

        render(<PodcastPlayer initialTopic="Test Topic" />);

        const button = screen.getByRole('button', { name: /generate podcast/i });
        fireEvent.click(button);

        await waitFor(() => {
            expect(global.fetch).toHaveBeenCalledWith(
                expect.stringContaining('/api/debate/generate'),
                expect.any(Object)
            );
        });
    });

    it('handles API errors gracefully', async () => {
        (global.fetch as jest.Mock).mockRejectedValueOnce(new Error('API Error'));

        render(<PodcastPlayer initialTopic="Test" />);

        const button = screen.getByRole('button', { name: /generate podcast/i });
        fireEvent.click(button);

        await waitFor(() => {
            expect(global.fetch).toHaveBeenCalled();
        });
    });
});

describe('PodcastPlayer State Management', () => {
    it('shows loading state when generating', async () => {
        (global.fetch as jest.Mock).mockImplementation(() =>
            new Promise(resolve => setTimeout(resolve, 1000))
        );

        render(<PodcastPlayer initialTopic="Test" />);

        const button = screen.getByRole('button', { name: /generate podcast/i });
        fireEvent.click(button);

        // Check for loading indicator
        await waitFor(() => {
            expect(button).toBeDisabled();
        });
    });
});
