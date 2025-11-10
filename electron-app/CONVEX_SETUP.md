# Convex Setup Guide

## Initial Setup

1. **Install Convex CLI** (if not already installed):
   ```bash
   npm install -g convex
   ```

2. **Initialize Convex in the project**:
   ```bash
   cd electron-app
   npx convex dev
   ```

3. **Create schema files** in `convex/` directory (to be created)

## Schema Structure

Based on the Python version, we need:

### Sessions Table
- `_id`: Id (auto-generated)
- `userId`: string (user ID from WorkOS)
- `startTime`: number (timestamp)
- `endTime`: number | null (timestamp)
- `commands`: Command[]
- `events`: Event[]
- `screenshotIds`: string[] (Convex file storage IDs)

### Commands Table (optional, can be nested in sessions)
- `sessionId`: Id<"sessions">
- `timestamp`: number
- `command`: string
- `screenshotId`: Id<"_storage">
- `region`: { x, y, width, height } | null

### Events Table (optional, can be nested in sessions)
- `sessionId`: Id<"sessions">
- `timestamp`: number
- `type`: string
- `data`: any

## File Storage

Screenshots will be stored in Convex file storage:
- Use `convex.storage.store()` to upload files
- Store file IDs in session records
- Use `convex.storage.getUrl()` to retrieve files

## Next Steps

1. Run `npx convex dev` to initialize
2. Create schema files in `convex/schema.ts`
3. Create mutation/query functions
4. Update `src/renderer/services/convex.ts` with actual Convex client

