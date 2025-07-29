import yt_dlp
import os
from get_playlist import get_playlist_info

def download_audio(urls, base_folder):
    for url in urls:
        print(f"Attempting download for URL: [{url}]")
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
            'quiet': False,
            'noplaylist': False,
            # 'cookiefile': 'cookies.txt',
            # 'http_headers': {
            #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            # }
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                result = ydl.download([url])
                if result != 0:
                    print(f"Failed to download: {url}")
        except Exception as e:
            print(f"An error occurred while downloading {url}: {str(e)}")

def main():
    default_folder = 'download-audios'
    download_folder = input(f"Enter the download folder path (leave blank for default '{default_folder}'): ")
    if not download_folder.strip():
        download_folder = default_folder

    urls = []
    print("\nEnter YouTube URLs (type 'done' to finish):")
    while True:
        url = input("URL: ").strip()
        if url.lower() == 'done':
            break
        if url:
            urls.append(url)

    if not urls:
        print("No URLs provided. Exiting...")
        return

    download_audio(urls, download_folder)

    print(f"\nDownloads completed. Base folder: '{download_folder}'")

if __name__ == "__main__":
    main()