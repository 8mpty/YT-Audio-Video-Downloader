import yt_dlp
import os

def download_video(urls, download_folder):
    """
    Download videos in 1080p with audio using yt-dlp
    
    Args:
        urls (list): List of URLs to download
        download_folder (str): Directory to save the downloaded videos
    """
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    ydl_opts = {
        'format': 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'merge_output_format': 'mp4',
        'outtmpl': os.path.join(download_folder, '%(title)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',
        }],
        'verbose': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"Downloading videos...")
            ydl.download(urls)
            print("Downloads completed successfully!")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

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
            # Clean the playlist title for use as a folder name
            if playlist_title:
                # Remove invalid characters for folder names
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
    # Check if URL is a playlist and get its title
    is_playlist, playlist_title = get_playlist_info(url)
    
    # Determine the download folder
    if is_playlist and playlist_title:
        download_folder = os.path.join(base_folder, playlist_title)
        print(f"\n[download] Downloading playlist: {playlist_title}")
    else:
        download_folder = base_folder
        print(f"\n[download] Downloading single track")
    
    # Create download folder if it doesn't exist
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
        'noplaylist': False,  # Allow playlist downloads
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        print(f"An error occurred: {str(e)}")

def main():
    # Get download type
    while True:
        download_type = input("Enter download type (video/audio): ").lower()
        if download_type in ['video', 'audio']:
            break
        print("Please enter either 'video' or 'audio'")

    # Get download folder
    default_folder = 'download-videos' if download_type == 'video' else 'download-audios'
    download_folder = input(f"Enter the download folder path (leave blank for default '{default_folder}'): ")
    if not download_folder.strip():
        download_folder = default_folder

    # Get URLs
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

    # Download based on type
    if download_type == 'video':
        download_video(urls, download_folder)
    else:
        # For audio, process each URL individually to handle playlists
        for url in urls:
            download_audio_with_metadata(url, download_folder)

    print(f"\nDownloads completed. Base folder: '{download_folder}'")

if __name__ == "__main__":
    main()