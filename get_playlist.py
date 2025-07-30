import yt_dlp
import re

def clean_filename(name: str) -> str:
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        name = name.replace(char, '-')
    return name.strip()

def extract_info(url: str) -> dict:
    ydl_opts = {
        'quiet': True,
        'extract_flat': False,
        'force_generic_extractor': False
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(url, download=False)

def extract_artist_album(info: dict) -> tuple[str | None, str | None]:
    artist = info.get('artist')
    album = info.get('album')

    if not artist or not album:
        entries = info.get('entries')
        if entries and isinstance(entries, list) and len(entries) > 0:
            first_entry = entries[0]
            artist = first_entry.get('artist') or artist
            album = first_entry.get('album') or album

    return artist, album

def parse_album_from_title(title: str) -> str | None:
    match = re.match(r'^\s*(?:Album|EP|Single)?\s*-\s*(.+)', title, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return None

def build_playlist_title(title: str, artist: str | None, album: str | None) -> str:
    parsed_album = parse_album_from_title(title) or album

    if artist and parsed_album:
        playlist_title = f"{artist} - {parsed_album}"
    else:
        playlist_title = title

    return clean_filename(playlist_title)

def get_playlist_info(url: str) -> tuple[bool, str | None]:
    try:
        info = extract_info(url)
        is_playlist = 'entries' in info
        title = info.get('title', '').strip()

        artist, album = extract_artist_album(info)

        print(f"Music title: [{title}]")
        print(f"Music artist: [{artist}]")
        print(f"Music album: [{album}]")

        playlist_title = build_playlist_title(title, artist, album)
        return is_playlist, playlist_title

    except Exception as e:
        print(f"Error getting playlist info: {str(e)}")
        return False, None