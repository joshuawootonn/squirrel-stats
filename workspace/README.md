# Squirrel Stats Workspace

This is a pnpm workspace containing:

## Packages

### `@squirrel-stats/app`

The TanStack Start dashboard application for viewing analytics.

### `@squirrel-stats/script`

The analytics tracking script (similar to Fathom's script.js).

## Getting Started

```bash
# Install dependencies
pnpm install

# Run the app in development mode
pnpm -F @squirrel-stats/app run dev

# Build all packages
pnpm build
```

## Workspace Structure

```
workspace/
├── packages/
│   ├── app/          # TanStack Start dashboard app
│   └── script/       # Analytics tracking script
├── pnpm-workspace.yaml
└── package.json
```
