# Where to Put .env.local File

## Location

The `.env.local` file should be in the **`frontend/`** folder:

```
ALIVE/
└── frontend/
    ├── .env.local          ← HERE!
    ├── package.json
    ├── src/
    └── ...
```

## Full Path

```
C:\Users\matth\Desktop\ALIVE Data\ALIVE\frontend\.env.local
```

## Contents

Your `.env.local` file should contain:

```
VITE_CONVEX_URL=https://content-oriole-437.convex.cloud
```

## Important Notes

1. **File name**: Must be exactly `.env.local` (starts with a dot)
2. **Location**: Must be in the `frontend/` folder (same level as `package.json`)
3. **Restart required**: After creating/editing `.env.local`, restart the dev server (`npm run dev`)

## How to Create It

**Windows Command Prompt:**
```cmd
cd frontend
echo VITE_CONVEX_URL=https://content-oriole-437.convex.cloud > .env.local
```

**Windows PowerShell:**
```powershell
cd frontend
"VITE_CONVEX_URL=https://content-oriole-437.convex.cloud" | Out-File -FilePath .env.local -Encoding utf8
```

**Or manually:**
1. Navigate to `frontend/` folder
2. Create new file named `.env.local`
3. Add: `VITE_CONVEX_URL=https://content-oriole-437.convex.cloud`
4. Save

## Verify It's Working

After restarting dev server, check browser console:
- Should see: `Convex URL: https://content-oriole-437.convex.cloud`
- If you see `undefined`, the file isn't being loaded

