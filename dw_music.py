import yt_dlp
import os
from get_playlist import get_playlist_info
from config import AUDIO_FORMAT, PREFERRED_AUDIO_CODEC, PREFERRED_AUDIO_QUALITY, WRITE_THUMBNAIL, VERBOSE_MODE, QUIET_MODE, DEFAULT_OUTTEMPLATE, KEEP_THUMBNAIL, delete_thumbnails

def get_ydl_opts(download_folder, outtemplate=DEFAULT_OUTTEMPLATE, is_playlist=False):
    return {
        'format': AUDIO_FORMAT,
        'postprocessors': [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': PREFERRED_AUDIO_CODEC,
                'preferredquality': PREFERRED_AUDIO_QUALITY,
            },
            {
                'key': 'FFmpegMetadata',
            },
            {
                'key': 'EmbedThumbnail',
            }
        ],
        'writethumbnail': WRITE_THUMBNAIL,
        'outtmpl': os.path.join(download_folder, outtemplate),
        'noplaylist': not is_playlist,
        'verbose': VERBOSE_MODE,
        'quiet': QUIET_MODE,
        # 'cookiefile': 'cookies.txt',
    }

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

        ydl_opts = get_ydl_opts(download_folder, is_playlist=is_playlist)

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                result = ydl.download([url])
                if result != 0:
                    print(f"Failed to download: {url}")
                else:
                    if not KEEP_THUMBNAIL:
                        delete_thumbnails(download_folder)
        except Exception as e:
            print(f"An error occurred while downloading {url}: {str(e)}")

def main():
    default_base_folder = 'download-audios'
    user_input = input(
        f"Enter a subfolder name to save into (leave blank to use '{default_base_folder}'): "
    ).strip()

    if not user_input:
        download_folder = default_base_folder
    else:
        download_folder = os.path.join(default_base_folder, user_input)

    print(f"Files will be downloaded to: {download_folder}")

    urls = []
    print("\nEnter URLs (press Enter without typing anything to finish or Ctrl + C to exit):")
    while True:
        url = input("URL: ").strip()
        if not url:
            break
        urls.append(url)

    if not urls:
        print("No URLs provided. Exiting...")
        return

    download_audio(urls, download_folder)

    print(f"\nDownloads completed. Base folder: '{download_folder}'")

if __name__ == "__main__":
    main()