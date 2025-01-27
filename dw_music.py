import yt_dlp
import os

def get_playlist_info(url):
    """
    Get playlist title if URL is a playlist
    
    Args:
        url (str): URL to check
        
    Returns:
        tuple: (is_playlist, playlist_title)
    """
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'force_generic_extractor': False
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            is_playlist = bool('entries' in info)
            playlist_title = info.get('title', '').strip() if is_playlist else None
            if playlist_title:
                invalid_chars = '<>:"/\\|?*'
                for char in invalid_chars:
                    playlist_title = playlist_title.replace(char, '-')
            return is_playlist, playlist_title
    except Exception as e:
        print(f"Error getting playlist info: {str(e)}")
        return False, None

def download_audio_with_metadata(url, base_folder):
    """
    Download audio with metadata and thumbnail using yt-dlp
    
    Args:
        url (str): URL to download
        base_folder (str): Base directory for downloads
    """
    is_playlist, playlist_title = get_playlist_info(url)
    
    if is_playlist and playlist_title:
        download_folder = os.path.join(base_folder, playlist_title)
        print(f"\n[download] Downloading playlist: {playlist_title}")
    else:
        download_folder = base_folder
        print(f"\n[download] Downloading single track")
    
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            },
            {
                'key': 'FFmpegMetadata',
            },
            {
                'key': 'EmbedThumbnail',
            }
        ],
        'writethumbnail': True,
        'outtmpl': os.path.join(download_folder, '%(title)s.%(ext)s'),
        'noplaylist': False,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        print(f"An error occurred: {str(e)}")

def main():
    default_folder = 'download-audios'
    download_folder = input(f"Enter the download folder path (leave blank for default '{default_folder}'): ")
    if not download_folder.strip():
        download_folder = default_folder

    urls = []
    print("\nEnter YouTube URLs (type 'done' to finish):")
    while True:
        url = input("URL: ")
        if url.lower() == 'done':
            break
        urls.append(url)

    if not urls:
        print("No URLs provided. Exiting...")
        return

    for url in urls:
        download_audio_with_metadata(url, download_folder)

    print(f"\nDownloads completed. Base folder: '{download_folder}'")

if __name__ == "__main__":
    main()