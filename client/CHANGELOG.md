# @squirrel-stats/client

## 0.0.2

### Patch Changes

- 2c21f5f: Updated script to track entry page and not just subsequent navigations

## 0.0.1

### Patch Changes

- 4f2123e: First release of the squirrel-stats client with support for tracking pageviews and events.

    ## Usage Examples

    ### Basic Setup

    ```typescript
    import { SquirrelStats } from '@squirrel-stats/client';

    const tracker = new SquirrelStats('your-site-identifier');
    ```

    ### Track Pageviews

    ```typescript
    // Track current page
    tracker.trackPageview();

    // Track with custom URL
    tracker.trackPageview({ url: '/custom-page' });

    // Track with custom referrer
    tracker.trackPageview({ referrer: 'https://example.com' });
    ```

    ### Track Events

    ```typescript
    // Track simple event
    tracker.trackEvent('button_click');
    ```
