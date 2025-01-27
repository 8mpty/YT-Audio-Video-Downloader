import yt_dlp

def download_video(url, output_path='downloads'):
    """
    Download video in 1080p with audio using yt-dlp
    
    Args:
        url (str): URL of the video to download
        output_path (str): Directory to save the downloaded video
    """
    ydl_opts = {
        'format': 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'merge_output_format': 'mp4',
        'outtmpl': f'{output_path}/%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',
        }],
        'verbose': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"Downloading video from: {url}")
            ydl.download([url])
            print("Download completed successfully!")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

def main():
    # Example usage
    video_url = input("Enter the video URL: ")
    output_directory = input("Enter output directory (press Enter for default 'downloads-videos'): ")
    
    if not output_directory:
        output_directory = 'downloads-videos'
    
    download_video(video_url, output_directory)

if __name__ == "__main__":
    main()