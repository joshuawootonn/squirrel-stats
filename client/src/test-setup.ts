import { beforeAll, afterEach, afterAll } from 'vitest';
import { setupServer } from 'msw/node';
import { http, HttpResponse } from 'msw';

// Create MSW server
export const server = setupServer();

// Start server before all tests
beforeAll(() => {
    server.listen({ onUnhandledRequest: 'error' });
});

// Reset handlers after each test
afterEach(() => {
    server.resetHandlers();
});

// Clean up after all tests
afterAll(() => {
    server.close();
});

// Helper to create mock handlers for analytics endpoints
export const createAnalyticsHandlers = () => [
    // Pageview endpoint
    http.get('https://api.usesquirrelstats.com/pv', ({ request }) => {
        const url = new URL(request.url);
        return HttpResponse.json({ success: true, params: Object.fromEntries(url.searchParams) });
    }),

    // Event endpoint
    http.get('https://api.usesquirrelstats.com/e', ({ request }) => {
        const url = new URL(request.url);
        return HttpResponse.json({ success: true, params: Object.fromEntries(url.searchParams) });
    }),
];
