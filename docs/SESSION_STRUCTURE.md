# Recording Session Structure

ALIVEOCR now organizes all recording sessions into structured folders for better organization and future database integration.

## Folder Structure

Each recording session creates a folder with the following structure:

```
docs/sessions/
└── YYYYMMDD_HHMMSS_PCNAME_SESSIONID/
    ├── documentation.md          # Main documentation file
    ├── screenshots/             # All captured screenshots
    │   ├── command_20251109_224433_051.png
    │   ├── command_20251109_224444_017.png
    │   └── ...
    └── metadata/                # Session metadata
        └── session_info.json    # Session information (JSON format)
```

## Folder Naming Convention

Session folders are named using the following format:

**`YYYYMMDD_HHMMSS_PCNAME_SESSIONID`**

### Components:

1. **YYYYMMDD** - Date (e.g., `20251109`)
2. **HHMMSS** - Time (e.g., `224512`)
3. **PCNAME** - Abbreviated PC name (first 8 characters, uppercase)
4. **SESSIONID** - Unique session identifier (3-digit milliseconds)

### Example:
```
20251109_224512_MATTHEWF_001
```

This represents:
- Date: November 9, 2025
- Time: 22:45:12
- PC: MATTHEWF (from "Matthew Feroz")
- Session ID: 001

## Session Metadata

Each session includes a `metadata/session_info.json` file with:

```json
{
  "session_id": "20251109_224512_MATTHEWF_001",
  "start_time": "2025-11-09T22:45:12.123456",
  "end_time": "2025-11-09T22:50:30.789012",
  "duration_seconds": 318.67,
  "pc_name": "MATTHEW-FEROZ-PC",
  "pc_name_abbrev": "MATTHEWF",
  "screenshot_count": 5,
  "base_dir": "docs/sessions",
  "session_dir": "docs/sessions/20251109_224512_MATTHEWF_001"
}
```

## Benefits

1. **Organization**: Each recording session is self-contained in its own folder
2. **Database Ready**: Structured format makes it easy to import into databases
3. **Traceability**: Date, time, and PC name make sessions easy to identify
4. **Scalability**: Can easily add more metadata fields as needed
5. **Portability**: Entire session folders can be moved/archived easily

## Future Enhancements

Potential additions to folder naming:
- **Custom Prefix**: `DEMO_20251109_224512_MATTHEWF_001` (for demo recordings)
- **User ID**: `20251109_224512_USER123_MATTHEWF_001` (for multi-user systems)
- **Project Tag**: `PROJ1_20251109_224512_MATTHEWF_001` (for project-specific recordings)
- **Session Type**: `REC_20251109_224512_MATTHEWF_001` (for different recording types)

## Database Integration

When uploading to a database, each session folder can be:
1. **Zipped** and uploaded as a blob
2. **Parsed** and stored as structured records:
   - Session table (session_id, start_time, end_time, duration, pc_name)
   - Screenshot table (screenshot_id, session_id, file_path, timestamp)
   - Documentation table (doc_id, session_id, content, file_path)

## File Paths in Documentation

The markdown documentation uses relative paths for screenshots:
```markdown
![Screenshot 1](screenshots/command_20251109_224433_051.png)
```

This ensures documentation remains portable and works when the session folder is moved.


