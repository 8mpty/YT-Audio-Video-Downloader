import yt_dlp
import os
from get_playlist import get_playlist_info

def download_video(urls, base_folder):
    """
    Download multiple videos or playlists.
    
    Args:
        urls (list): List of URLs
        base_folder (str): Base directory for downloads
    """
    for url in urls:
        is_playlist, playlist_title = get_playlist_info(url)

        if is_playlist and playlist_title:
            download_folder = os.path.join(base_folder, playlist_title)
            print(f"\n[download] Downloading playlist: {playlist_title}")
        else:
            download_folder = base_folder
            print(f"\n[download] Downloading single video")

        if not os.path.exists(download_folder):
            os.makedirs(download_folder)

        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best',
            'merge_output_format': 'mp4',
            'writethumbnail': True,
            'outtmpl': os.path.join(download_folder, '%(title)s.%(ext)s'),
            'noplaylist': False,
            # 'verbose': True,
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
            print(f"An error occurred: {str(e)}")


def main():
    default_folder = 'download-videos'
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

    download_video(urls, download_folder)

    print(f"\nDownloads completed. Base folder: '{download_folder}'")

if __name__ == "__main__":
    main()