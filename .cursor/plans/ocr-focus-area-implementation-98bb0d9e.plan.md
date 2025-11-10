<!-- 98bb0d9e-87bc-4e16-87f4-b19029fa7c4e 23a6b5f9-0975-46d8-9227-49eff41e464c -->
# Electron Migration and Deployment Plan

## Decision: Electron Framework

**Rationale:**

- Team has existing Electron knowledge
- Faster development than learning Rust (Tauri)
- Large ecosystem and community support
- Can keep Python backend as separate service if needed

## Git Branch Created ✓

**Branch:** `electron-migration`

- Created from `main` branch
- Ready for Electron migration work
- Can merge back when ready

## Architecture Overview

```
┌─────────────────────────────────────┐
│   Electron Frontend (React/Vue)    │
│   - Modern web UI                  │
│   - WorkOS auth                    │
│   - Convex client                  │
└──────────────┬──────────────────────┘
               │ IPC (Electron)
┌──────────────▼──────────────────────┐
│   Node.js Backend (Electron Main)    │
│   - Window tracking (node-ffi)       │
│   - Process monitoring              │
│   - Screenshot capture              │
│   - Event tracking                  │
└──────────────┬──────────────────────┘
               │ HTTP/Subprocess
┌──────────────▼──────────────────────┐
│   Python Service (Optional)          │
│   - OCR (Tesseract)                 │
│   - LLM (OpenAI)                    │
│   - Can be bundled or separate      │
└─────────────────────────────────────┘
               │
┌──────────────▼──────────────────────┐
│   Convex Backend                    │
│   - Session storage                 │
│   - Event data                      │
│   - File storage                    │
└─────────────────────────────────────┘
```

## Migration Strategy

### Phase 1: Project Setup (Week 1)

1. **Initialize Electron project**

   - Use Electron Forge or Electron Builder
   - Set up React/Vue frontend
   - Configure build system

2. **Set up project structure**
   ```
   alive-data-electron/
   ├── src/
   │   ├── main/          # Electron main process
   │   ├── renderer/       # React/Vue frontend
   │   └── shared/         # Shared types/utils
   ├── python-service/     # Optional Python backend
   ├── package.json
   └── electron-builder config
   ```


### Phase 2: Port Windows Features (Week 2-3)

1. **Window Tracking**

   - Use `node-ffi` or `ffi-napi` for Windows API
   - Port window enumeration logic
   - Port window focus tracking

2. **Process Monitoring**

   - Use `node-ps` or `systeminformation`
   - Port process launch/termination tracking

3. **Screenshot Capture**

   - Use `screenshot-desktop` or `node-screenshots`
   - Port capture logic

4. **Event Tracking**

   - Port event tracking logic to Node.js
   - Create event system

### Phase 3: UI Migration (Week 3-4)

1. **Window Selector** → React component
2. **Recording Log** → React component
3. **Toolbar** → Electron frameless window
4. **Settings** → React forms

### Phase 4: Service Integration (Week 4-5)

1. **OCR:** tesseract.js OR Python service OR Cloud API
2. **LLM:** OpenAI Node.js SDK
3. **WorkOS:** JavaScript SDK
4. **Convex:** JavaScript SDK

### Phase 5: Packaging & Deployment (Week 5-6)

1. Configure Electron Builder
2. Optimize bundle
3. Set up auto-updates

## Technology Stack

### Frontend

- **Framework:** React or Vue
- **Build Tool:** Vite or Webpack
- **UI Library:** Tailwind CSS or Material-UI

### Electron

- **Main Process:** Node.js with Windows API bindings
- **IPC:** Electron IPC
- **Native Modules:** node-ffi, ffi-napi

### Backend Services

- **OCR:** tesseract.js OR Python service
- **LLM:** OpenAI Node.js SDK
- **Auth:** WorkOS JavaScript SDK
- **Database:** Convex JavaScript SDK

## Key Libraries Needed

```json
{
  "electron": "^28.0.0",
  "electron-builder": "^24.0.0",
  "ffi-napi": "^4.0.3",
  "systeminformation": "^5.21.0",
  "screenshot-desktop": "^1.15.0",
  "tesseract.js": "^5.0.0",
  "@workos-inc/node": "^1.0.0",
  "convex": "^1.0.0",
  "openai": "^4.0.0"
}
```

## Next Steps

1. ✓ **Branch created:** `electron-migration`
2. **Initialize Electron project** in new directory
3. **Set up basic Electron app** with React/Vue
4. **Port one feature** as proof of concept
5. **Iterate** on remaining features

### To-dos

- [ ] Create electron-migration branch for the migration work
- [ ] Initialize Electron project with React/Vue frontend and configure build system
- [ ] Port window tracking functionality to Node.js using ffi-napi or similar
- [ ] Port process monitoring to Node.js using systeminformation or node-ps
- [ ] Port screenshot capture to Node.js using screenshot-desktop
- [ ] Build React/Vue components for window selector, recording log, and toolbar
- [ ] Integrate WorkOS authentication in Electron renderer process
- [ ] Set up Convex project and implement data sync for sessions and events
- [ ] Choose and implement OCR solution (tesseract.js, Python service, or cloud API)
- [ ] Configure electron-builder for packaging and creating installers