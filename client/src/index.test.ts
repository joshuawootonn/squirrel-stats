import { describe, it, expect, beforeEach, vi } from 'vitest';
import { server, createAnalyticsHandlers } from './test-setup.js';
import { SquirrelStats } from './index.js';

describe('SquirrelStats', () => {
    let tracker: SquirrelStats;
    let capturedRequests: Array<{ url: string; params: Record<string, string> }> = [];

    beforeEach(() => {
        // Reset captured requests
        capturedRequests = [];

        // Set up MSW handlers to capture requests
        server.use(...createAnalyticsHandlers());

        // Mock navigator.sendBeacon to capture requests
        vi.stubGlobal('navigator', {
            sendBeacon: vi.fn((url: string) => {
                const urlObj = new URL(url);
                capturedRequests.push({
                    url: urlObj.origin + urlObj.pathname,
                    params: Object.fromEntries(urlObj.searchParams),
                });
                return true;
            }),
        });

        // Set up basic DOM environment
        Object.defineProperty(window, 'location', {
            value: {
                href: 'https://example.com/test-page?utm_source=google&utm_medium=cpc',
                origin: 'https://example.com',
                hostname: 'example.com',
                pathname: '/test-page',
                search: '?utm_source=google&utm_medium=cpc',
            },
            writable: true,
        });

        Object.defineProperty(document, 'referrer', {
            value: 'https://google.com',
            writable: true,
        });

        // Clear any existing canonical links
        document.head.innerHTML = '';

        tracker = new SquirrelStats('site_12345');
    });

    describe('trackPageview', () => {
        it('should send pageview to correct endpoint with basic params', () => {
            tracker.trackPageview();

            expect(capturedRequests).toHaveLength(1);
            expect(capturedRequests[0]?.url).toBe('https://api.usesquirrelstats.com/pv');

            const params = capturedRequests[0]?.params;
            expect(params?.hostname).toBe('https://example.com');
            expect(params?.pathname).toBe('/test-page');
            expect(params?.referrer).toBe('https://google.com');
            expect(params?.siteId).toBe('site_12345');
            expect(params?.buster).toBeDefined();
            expect(Number(params?.buster)).toBeGreaterThan(0);
        });

        it('should include query parameters in tracking', () => {
            tracker.trackPageview();

            const params = capturedRequests[0]?.params;
            const queryParams = JSON.parse(params?.queryParams || '{}');

            expect(queryParams.utm_source).toBe('google');
            expect(queryParams.utm_medium).toBe('cpc');
        });

        it('should use canonical URL when present', () => {
            // Add canonical link to document head
            const canonicalLink = document.createElement('link');
            canonicalLink.rel = 'canonical';
            canonicalLink.href = 'https://canonical-example.com/canonical-page';
            document.head.appendChild(canonicalLink);

            tracker.trackPageview();

            const params = capturedRequests[0]?.params;
            expect(params?.hostname).toBe('https://canonical-example.com');
            expect(params?.pathname).toBe('/canonical-page');
        });

        it('should use custom referrer when provided', () => {
            tracker.trackPageview({ referrer: 'https://custom-referrer.com' });

            const params = capturedRequests[0]?.params;
            expect(params?.referrer).toBe('https://custom-referrer.com');
        });

        it('should filter out same-origin referrer', () => {
            // Set referrer to same origin
            Object.defineProperty(document, 'referrer', {
                value: 'https://example.com/previous-page',
                writable: true,
            });

            tracker.trackPageview();

            const params = capturedRequests[0]?.params;
            expect(params?.referrer).toBe('');
        });

        it('should handle missing pathname', () => {
            Object.defineProperty(window, 'location', {
                value: {
                    href: 'https://example.com',
                    origin: 'https://example.com',
                    hostname: 'example.com',
                    pathname: '',
                    search: '',
                },
                writable: true,
            });

            tracker.trackPageview();

            const params = capturedRequests[0]?.params;
            expect(params?.pathname).toBe('/');
        });
    });

    describe('trackEvent', () => {
        it('should send event to correct endpoint with basic params', () => {
            tracker.trackEvent('button_click');

            expect(capturedRequests).toHaveLength(1);
            expect(capturedRequests[0]?.url).toBe('https://api.usesquirrelstats.com/e');

            const params = capturedRequests[0]?.params;
            expect(params?.eventName).toBe('button_click');
            expect(params?.hostname).toBe('https://example.com');
            expect(params?.pathname).toBe('/test-page');
            expect(params?.referrer).toBe('https://google.com');
            expect(params?.siteId).toBe('site_12345');
            expect(params?.buster).toBeDefined();
        });

        it('should include query parameters in event tracking', () => {
            tracker.trackEvent('purchase');

            const params = capturedRequests[0]?.params;
            const queryParams = JSON.parse(params?.queryParams || '{}');

            expect(queryParams.utm_source).toBe('google');
            expect(queryParams.utm_medium).toBe('cpc');
        });

        it('should use canonical URL for events', () => {
            // Add canonical link
            const canonicalLink = document.createElement('link');
            canonicalLink.rel = 'canonical';
            canonicalLink.href = 'https://canonical-example.com/canonical-page';
            document.head.appendChild(canonicalLink);

            tracker.trackEvent('signup');

            const params = capturedRequests[0]?.params;
            expect(params?.hostname).toBe('https://canonical-example.com');
            expect(params?.pathname).toBe('/canonical-page');
        });

        it('should filter out same-origin referrer for events', () => {
            Object.defineProperty(document, 'referrer', {
                value: 'https://example.com/previous-page',
                writable: true,
            });

            tracker.trackEvent('conversion');

            const params = capturedRequests[0]?.params;
            expect(params?.referrer).toBe('');
        });
    });

    describe('query parameter extraction', () => {
        it('should extract relevant UTM parameters', () => {
            Object.defineProperty(window, 'location', {
                value: {
                    href: 'https://example.com/page?utm_source=facebook&utm_medium=social&utm_campaign=summer2024&utm_content=ad1&utm_term=analytics',
                    origin: 'https://example.com',
                    hostname: 'example.com',
                    pathname: '/page',
                    search: '?utm_source=facebook&utm_medium=social&utm_campaign=summer2024&utm_content=ad1&utm_term=analytics',
                },
                writable: true,
            });

            tracker.trackPageview();

            const params = capturedRequests[0]?.params;
            const queryParams = JSON.parse(params?.queryParams || '{}');

            expect(queryParams.utm_source).toBe('facebook');
            expect(queryParams.utm_medium).toBe('social');
            expect(queryParams.utm_campaign).toBe('summer2024');
            expect(queryParams.utm_content).toBe('ad1');
            expect(queryParams.utm_term).toBe('analytics');
        });

        it('should extract other relevant parameters', () => {
            Object.defineProperty(window, 'location', {
                value: {
                    href: 'https://example.com/page?q=search&ref=homepage&gclid=abc123&msclkid=def456',
                    origin: 'https://example.com',
                    hostname: 'example.com',
                    pathname: '/page',
                    search: '?q=search&ref=homepage&gclid=abc123&msclkid=def456',
                },
                writable: true,
            });

            tracker.trackPageview();

            const params = capturedRequests[0]?.params;
            const queryParams = JSON.parse(params?.queryParams || '{}');

            expect(queryParams.q).toBe('search');
            expect(queryParams.ref).toBe('homepage');
            expect(queryParams.gclid).toBe('abc123');
            expect(queryParams.msclkid).toBe('def456');
        });

        it('should ignore irrelevant parameters', () => {
            Object.defineProperty(window, 'location', {
                value: {
                    href: 'https://example.com/page?utm_source=google&irrelevant=ignore&debug=true',
                    origin: 'https://example.com',
                    hostname: 'example.com',
                    pathname: '/page',
                    search: '?utm_source=google&irrelevant=ignore&debug=true',
                },
                writable: true,
            });

            tracker.trackPageview();

            const params = capturedRequests[0]?.params;
            const queryParams = JSON.parse(params?.queryParams || '{}');

            expect(queryParams.utm_source).toBe('google');
            expect(queryParams.irrelevant).toBeUndefined();
            expect(queryParams.debug).toBeUndefined();
        });
    });

    describe('fallback behavior', () => {
        it('should fallback to image pixel when sendBeacon is not available', () => {
            // Mock navigator without sendBeacon
            vi.stubGlobal('navigator', {});

            // Mock document.createElement and appendChild to capture image requests
            const mockImg = {
                setAttribute: vi.fn(),
                addEventListener: vi.fn(),
                style: {},
                src: '',
            };

            const mockAppendChild = vi.fn();
            vi.spyOn(document, 'createElement').mockReturnValue(mockImg as any);
            vi.spyOn(document.body, 'appendChild').mockImplementation(mockAppendChild);

            tracker.trackPageview();

            expect(document.createElement).toHaveBeenCalledWith('img');
            expect(mockImg.setAttribute).toHaveBeenCalledWith('alt', '');
            expect(mockImg.setAttribute).toHaveBeenCalledWith('aria-hidden', 'true');
            expect(mockAppendChild).toHaveBeenCalledWith(mockImg);
            expect(mockImg.src).toContain('https://api.usesquirrelstats.com/pv');
            expect(mockImg.src).toContain('siteId=site_12345');
        });
    });
});
