import yt_dlp
import os

def download_audio_with_metadata(urls, download_folder):
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
        'noplaylist': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download(urls)

download_folder = input("Enter the download folder path (leave blank for default 'downloads-audio'): ")
if not download_folder.strip():
    download_folder = 'downloads-audio'

urls = []
print("Enter YouTube video URLs (type 'done' to finish):")
while True:
    url = input("URL: ")
    if url.lower() == 'done':
        break
    urls.append(url)
    
download_audio_with_metadata(urls, download_folder)

print(f"Downloaded audio files with metadata are saved in '{download_folder}'")