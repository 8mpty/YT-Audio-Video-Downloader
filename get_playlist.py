import yt_dlp
import re

def get_playlist_info(url):
    ydl_opts = {
        'quiet': True,
        'extract_flat': False,
        'force_generic_extractor': False
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # if not info:
            #     return False, None
            
            # is_playlist = 'entries' in info and isinstance(info['entries'], list)
            # playlist_title = None

            # is_playlist = bool('entries' in info)
            # playlist_title = info.get('title', '').strip() if is_playlist else None
            
            is_playlist = 'entries' in info
            title = info.get('title', '').strip()
            artist = info.get('artist')
            album = info.get('album')

            if not artist or not album:
                entries = info.get('entries')
                if entries and isinstance(entries, list) and len(entries) > 0:
                    first_entry = entries[0]
                    artist = first_entry.get('artist') or artist
                    album = first_entry.get('album') or album

            print(f"Music title: [{title}]")
            print(f"Music artist: [{artist}]")
            print(f"Music album: [{album}]")

            # Try to parse "Album - Name", "EP - Name", "Single - Name"
            match = re.match(r'^\s*(?:Album|EP|Single)?\s*-\s*(.+)', title, re.IGNORECASE)
            if match:
                parsed_album = match.group(1).strip()
            else:
                parsed_album = album

            if artist and parsed_album:
                playlist_title = f"{artist} - {parsed_album}"
            else:
                playlist_title = title

            if playlist_title:
                invalid_chars = '<>:"/\\|?*'
                for char in invalid_chars:
                    playlist_title = playlist_title.replace(char, '-')

            return is_playlist, playlist_title
        
    except Exception as e:
        print(f"Error getting playlist info: {str(e)}")
        return False, None
