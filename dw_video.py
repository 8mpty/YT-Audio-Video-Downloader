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

def main():
    default_folder = 'download-videos'
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

    download_video(urls, download_folder)
    print(f"\nDownloads completed. Base folder: '{download_folder}'")

if __name__ == "__main__":
    main()