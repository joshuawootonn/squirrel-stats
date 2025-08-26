/**
 * Squirrel Stats Analytics Client
 * A simplified analytics client for tracking pageviews and events
 */

/**
 * Options for tracking pageviews
 */
export type PageViewOptions = {
    /** Custom URL to track instead of current page */
    url?: string;
    /** Custom referrer to use */
    referrer?: string;
};

/**
 * Options for tracking events
 */
export type EventOptions = {
    /** Numeric value associated with the event */
    value?: number;
    /** Additional custom properties */
    [key: string]: any;
};

type TrackingParams = {
    [key: string]: string | number;
};

/**
 * Analytics client for tracking pageviews and events
 * @class SquirrelStats
 */
export class SquirrelStats {
    private readonly siteId: string;
    private readonly baseUrl = 'https://api.usesquirrelstats.com';

    /**
     * Creates a new SquirrelStats analytics client
     * @param siteId - The site ID for your analytics property
     */
    constructor(siteId: string) {
        this.siteId = siteId;
        if (siteId == null) {
            console.warn('[SquirrelStats] No siteId provided in constructor; tracking will be disabled.');
        }
        if ('prerendering' in document && document.prerendering) {
            document.addEventListener('prerenderingchange', () => this.trackPageview(), { once: true });
        } else {
            setTimeout(() => this.trackPageview());
        }
    }

    private getQueryParams(): Record<string, string> {
        const data: Record<string, string> = {};
        const pairs = window.location.search.substring(window.location.search.indexOf('?') + 1).split('&');

        const relevantParams = [
            'keyword',
            'q',
            'ref',
            's',
            'utm_campaign',
            'utm_content',
            'utm_medium',
            'utm_source',
            'utm_term',
            'action',
            'name',
            'pagename',
            'tab',
            'via',
            'gclid',
            'msclkid',
        ];

        for (let i = 0; i < pairs.length; i++) {
            if (pairs[i]) {
                const pair = pairs[i]!.split('=');
                const key = decodeURIComponent(pair[0] || '');
                if (relevantParams.indexOf(key) > -1) {
                    data[key] = decodeURIComponent(pair[1] || '');
                }
            }
        }

        return data;
    }

    private getLocation(): URL {
        const canonical = document.querySelector('link[rel="canonical"][href]') as HTMLLinkElement;
        if (canonical) {
            return new URL(canonical.href);
        }

        return new URL(window.location.href);
    }

    private send(url: string, params: TrackingParams): void {
        // Add cache buster to prevent browser caching
        params.buster = Math.floor(Math.random() * 100000000) + 1;

        const targetUrl = new URL(url);
        Object.keys(params).forEach((key) => {
            targetUrl.searchParams.set(key, String(params[key]));
        });

        const fullUrl = targetUrl.toString();

        // Try sendBeacon first (preferred for reliability)
        if (navigator.sendBeacon) {
            navigator.sendBeacon(fullUrl);
            return;
        }

        // Fallback to image pixel tracking
        const img = document.createElement('img');
        img.setAttribute('alt', '');
        img.setAttribute('aria-hidden', 'true');
        img.style.position = 'absolute';
        img.style.left = '-9999px';
        img.src = fullUrl;

        const cleanup = () => {
            if (img.parentNode) {
                img.parentNode.removeChild(img);
            }
        };

        img.addEventListener('load', cleanup);
        img.addEventListener('error', cleanup);
        document.body.appendChild(img);
    }

    /**
     * Tracks a pageview
     */
    trackPageview(opts?: PageViewOptions): void {
        const location = this.getLocation();

        if (!location.host) return;
        if (this.siteId == null) {
            // Warn and skip if siteId was not provided
            console.warn('[SquirrelStats] No siteId provided in constructor; pageview not sent.');
            return;
        }

        const hostname = location.origin;
        const pathname = location.pathname ?? '/';
        const referrer = opts?.referrer ?? (document.referrer.indexOf(hostname) < 0 ? document.referrer : '');

        const params: TrackingParams = {
            h: hostname,
            p: pathname,
            r: referrer,
            sid: this.siteId,
            qs: JSON.stringify(this.getQueryParams()),
        };

        this.send(new URL('pv', this.baseUrl).toString(), params);
    }

    /**
     * Tracks a custom event
     * @param eventName - Name of the event to track
     */
    trackEvent(eventName: string): void {
        const location = this.getLocation();
        const hostname = location.origin;
        const pathname = location.pathname ?? '/';
        const referrer = document.referrer.indexOf(hostname) < 0 ? document.referrer : '';

        if (this.siteId == null) {
            // Warn and skip if siteId was not provided
            console.warn('[SquirrelStats] No siteId provided in constructor; event not sent.', { eventName });
            return;
        }

        const params: TrackingParams = {
            eventName,
            hostname,
            pathname,
            referrer,
            siteId: this.siteId,
            queryParams: JSON.stringify(this.getQueryParams()),
        };

        this.send(new URL('e', this.baseUrl).toString(), params);
    }
}
