# Setting Up Convex for ALIVE Data

## Quick Start

### 1. Install Convex

```bash
cd frontend
npm install convex
```

### 2. Initialize Convex

```bash
npx convex dev
```

This will:
- Create `convex/` folder
- Set up Convex project
- Generate TypeScript types
- Start dev server

### 3. Configure Convex

After initialization, you'll get:
- Convex dashboard URL
- Deployment name
- API keys

### 4. Update Frontend to Use Convex

Install React hooks:
```bash
npm install convex
```

Wrap your app:
```typescript
// frontend/src/main.jsx
import { ConvexProvider, ConvexReactClient } from "convex/react";

const convex = new ConvexReactClient(import.meta.env.VITE_CONVEX_URL);

ReactDOM.createRoot(document.getElementById('root')).render(
  <ConvexProvider client={convex}>
    <App />
  </ConvexProvider>
);
```

### 5. Use Convex in Components

```typescript
import { useQuery, useMutation } from "convex/react";
import { api } from "../convex/_generated/api";

function SessionsList() {
  const sessions = useQuery(api.sessions.listSessions);
  const createSession = useMutation(api.sessions.createSession);

  return (
    <div>
      {sessions?.map(session => (
        <div key={session._id}>{session.sessionId}</div>
      ))}
      <button onClick={() => createSession({})}>New Session</button>
    </div>
  );
}
```

## Hybrid Architecture

### Keep FastAPI for:
- OCR processing (pytesseract)
- AI documentation generation (OpenAI)
- Heavy processing tasks

### Use Convex for:
- Session management
- File storage
- Real-time updates
- Frontend state

### Integration Flow:

```
Frontend → Convex (create session)
         → FastAPI (upload file, process OCR)
         → Convex (store results)
         → Frontend (real-time updates)
```

## Environment Variables

Add to `.env`:
```
VITE_CONVEX_URL=https://your-deployment.convex.cloud
```

## Next Steps

1. Run `npx convex dev` to initialize
2. Copy schema from `convex/schema.ts`
3. Copy functions from `convex/sessions.ts` and `convex/files.ts`
4. Update frontend to use Convex hooks
5. Keep FastAPI for OCR/AI processing

## Benefits You'll Get

- ✅ Real-time session updates
- ✅ Built-in file storage
- ✅ Type-safe database
- ✅ Automatic scaling
- ✅ Free tier available

