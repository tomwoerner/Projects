#!/usr/bin/env python3
"""
Plex Exporter
-------------
Export Plex playlist items to a plain text file (one track per line).

Supports:
- Hardcoded defaults
- CLI overrides
- Interactive prompts
- Playlist lookup by name

How to use:
    everything hardcoded (defaults):
    > python plex_exporter.py
    pass playlist ID directly:
    > python plex_exporter.py --playlist-id 76911
    lookup playlist by name:
    > python plex_exporter.py --playlist-name "Eurodance Essentials"
    override token at runtime:
    > python plex_exporter.py --token T5JfVV2Tj1FyEX-sv3yY --playlist-id 76911
"""

import argparse
import os
import sys
import requests
import xml.etree.ElementTree as ET
from urllib.parse import quote
from pathlib import Path

# =========================
# 🔧 DEFAULT CONFIG (OPTIONAL)
# =========================

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_PLEX_URL = "http://192.168.50.3:32400"
DEFAULT_PLEX_TOKEN = "T5JfVV2Tj1FyEX-sv3yY"   # <-- put token here if you want, else leave empty

# =========================
# 🧠 HELPERS
# =========================

def choose_playlist_interactively(server_url, token):
    playlists = get_playlists(server_url, token)

    if not playlists:
        sys.exit("No playlists found on server.")

    print("\nAvailable Playlists:")
    print("-" * 60)

    for pl in playlists:
        print(f"[{pl['id']}]  {pl['title']}")

    print("-" * 60)

    while True:
        choice = input("Enter Playlist ID to export: ").strip()
        if any(pl["id"] == choice for pl in playlists):
            return choice
        print("Invalid Playlist ID. Please try again.")

def prompt_if_missing(value, prompt_text, secret=False):
    if value:
        return value
    if secret:
        import getpass
        return getpass.getpass(prompt_text)
    return input(prompt_text).strip()


def plex_get(url, token):
    headers = {
        "Accept": "application/xml",
    }
    params = {
        "X-Plex-Token": token
    }
    r = requests.get(url, headers=headers, params=params)
    if r.status_code != 200:
        raise RuntimeError(f"HTTP {r.status_code}: {r.text}")
    return r.text


# =========================
# 🎵 PLAYLIST LOGIC
# =========================

def get_playlists(server_url, token):
    url = f"{server_url}/playlists"
    xml = plex_get(url, token)
    root = ET.fromstring(xml)

    playlists = []
    for pl in root.findall(".//Playlist"):
        playlists.append({
            "id": pl.attrib.get("ratingKey"),
            "title": pl.attrib.get("title")
        })
    return playlists


def find_playlist_id_by_name(server_url, token, name):
    playlists = get_playlists(server_url, token)
    for pl in playlists:
        if pl["title"].lower() == name.lower():
            return pl["id"]
    return None


def export_playlist(server_url, token, playlist_id, output_file):
    url = f"{server_url}/playlists/{playlist_id}/items"
    xml = plex_get(url, token)
    root = ET.fromstring(xml)

    lines = []

    for track in root.findall(".//Track"):
        artist = track.attrib.get("grandparentTitle", "")
        album = track.attrib.get("parentTitle", "")
        title = track.attrib.get("title", "")

        if artist:
            line = f"{artist} - {title}"
        else:
            line = title

        lines.append(line)

    with open(output_file, "w", encoding="utf-8") as f:
        for line in lines:
            f.write(line + "\n")

    return len(lines)


# =========================
# 🚀 MAIN
# =========================

def main():
    parser = argparse.ArgumentParser(description="Plex Exporter (playlist → text)")
    parser.add_argument("--token", help="Plex token (overrides hardcoded)")
    parser.add_argument("--playlist-id", help="Playlist ID")
    parser.add_argument("--playlist-name", help="Playlist name (exact match)")
    parser.add_argument("--out", default="playlist.txt", help="Output text file")

    args = parser.parse_args()

    # Resolve token
    token = args.token or DEFAULT_PLEX_TOKEN
    token = prompt_if_missing(token, "Enter Plex token: ", secret=True)

    # Resolve playlist ID
    playlist_id = args.playlist_id

    if not playlist_id:
        playlist_id = choose_playlist_interactively(
            DEFAULT_PLEX_URL,
            token
        )
    
    # Export
    output_path = SCRIPT_DIR / f"playlist_{playlist_id}.txt"

    count = export_playlist(
        DEFAULT_PLEX_URL,
        token,
        playlist_id,
        str(output_path)
    )

    print(f"✅ Exported {count} tracks to {args.out}")


if __name__ == "__main__":
    main()
