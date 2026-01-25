# Plex Exporter

Plex Exporter is a small Python utility for exporting Plex **music playlists** to a plain text file.  
Each track is written line-by-line, making the output easy to read, diff, script against, or import elsewhere.

The tool is intentionally simple, reliable, and designed to grow beyond playlists in future versions.

---

## Features (Current)

- Connects directly to a Plex Media Server via the local API
- Uses a Plex authentication token
- Lists all playlists on the server
- Lets the user **interactively choose a playlist by ID**
- Exports playlist items to a text file:
  ```
  playlist_<PLAYLIST_ID>.txt
  ```
- Always writes output **next to the script**, regardless of working directory

---

## Requirements

- Python 3.8+
- `requests` library

Install dependency:
```bash
pip install requests
```

---

## Configuration

### Plex Server
The server URL is currently hardcoded near the top of the script:

```python
DEFAULT_PLEX_URL = "http://192.168.50.3:32400"
```

The port is assumed to remain constant.

---

### Plex Token

You may either:

1. **Hardcode the token in the script**:
   ```python
   DEFAULT_PLEX_TOKEN = "YOUR_PLEX_TOKEN"
   ```

2. **Pass it as a command-line argument**:
   ```bash
   python plex_exporter.py --token YOUR_PLEX_TOKEN
   ```

3. **Enter it interactively** when prompted (if not provided elsewhere)

The priority order is:
```
CLI argument → hardcoded token → interactive prompt
```

> ⚠️ Treat your Plex token like a password.  
> Do not commit it to version control.

---

## Usage

### Basic interactive mode (recommended)
```bash
python plex_exporter.py
```

This will:
1. Prompt for a Plex token (if not provided)
2. Query the server for all playlists
3. Display playlist names and IDs
4. Ask you to choose a playlist ID
5. Export the playlist

---

### Provide token via CLI
```bash
python plex_exporter.py --token YOUR_PLEX_TOKEN
```

---

### Example interactive output
```
Available Playlists:
------------------------------------------------------------
[76911]  Eurodance Essentials
[77102]  80s Rock
[77255]  Chill Ambient
------------------------------------------------------------
Enter Playlist ID to export: 76911
```

Output file:
```
playlist_76911.txt
```

---

## Output Format

Plain text, one track per line:

```
Artist - Track Title
Artist - Track Title
Artist - Track Title
```

If artist metadata is missing, the track title alone is used.

This format is intentionally minimal and script-friendly.

---

## Design Notes

- Playlist **IDs** are used instead of names to avoid ambiguity
- XML responses from Plex are parsed directly
- No Plex Web dependencies or browser automation
- No working-directory assumptions
- Minimal dependencies for long-term stability

---

## Future Work / Planned Expansion

The current codebase is structured to support easy extension.

### Playlist Enhancements
- Export all playlists at once
- Include playlist name in output filename
- CSV and JSON output formats
- Preserve playlist order explicitly
- Include additional metadata (album, year, duration)

### Library Export
- Export entire music library
- Artist → album → track hierarchy
- Per-artist or per-album text files
- Library filtering (genre, year, rating)

### Automation & Scripting
- Non-interactive / cron-friendly mode
- Environment-variable token support
- Read-only token workflows
- Batch exports

### Interop
- Generate M3U playlists
- Import into other media players
- Bridge to Apple Music / Spotify workflows

---

## License / Usage

This script is intended for **personal use** with your own Plex server.  
Modify and extend freely.

---

## Notes

If the Plex API returns `401` or `403`, your token is likely invalid or revoked.  
Re-authenticate via Plex Web and extract a new token if needed.

---

Happy exporting 🎶
