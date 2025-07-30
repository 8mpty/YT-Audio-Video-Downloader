import yt_dlp
import os
from get_playlist import get_playlist_info
from config import VIDEO_FORMAT, PREFERRED_VIDEO_CODEC, WRITE_THUMBNAIL, VERBOSE_MODE, QUIET_MODE, DEFAULT_OUTTEMPLATE, TEMPFOLDER, KEEP_THUMBNAIL, delete_thumbnails

def get_ydl_opts(download_folder, outtemplate=DEFAULT_OUTTEMPLATE, is_playlist=False):
    return {
        'format': VIDEO_FORMAT,
        'merge_output_format': PREFERRED_VIDEO_CODEC,
        'writethumbnail': WRITE_THUMBNAIL,
        'outtmpl': os.path.join(download_folder, outtemplate),
        'noplaylist': not is_playlist,
        'verbose': VERBOSE_MODE,
        'quiet': QUIET_MODE,
        # 'cookiefile': 'cookies.txt',
    }


def download_video(urls, base_folder):
    os.makedirs(TEMPFOLDER, exist_ok=True)

    failed = []
    for url in urls:
        print(f"Attempting download for URL: [{url}]")
        is_playlist, playlist_title = get_playlist_info(url)

        ydl_opts = get_ydl_opts(TEMPFOLDER, is_playlist=is_playlist)

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                result = ydl.download([url])
                if result != 0:
                    print(f"Failed to download: {url}")
                    failed.append(url)
        except Exception as e:
            print(f"An error occurred while downloading {url}: {str(e)}")
            failed.append(url)

    if not KEEP_THUMBNAIL:
        delete_thumbnails(TEMPFOLDER)

    if is_playlist and playlist_title:
        final_folder = os.path.join(base_folder, playlist_title)
        print(f"\n[download] Downloading playlist: {playlist_title}")
    else:
        final_folder = base_folder
        print(f"\n[download] Downloading single video")

    if not os.path.exists(final_folder):
        os.makedirs(final_folder)

    for f in os.listdir(TEMPFOLDER):
        src = os.path.join(TEMPFOLDER, f)
        dst = os.path.join(final_folder, f)
        os.replace(src, dst)

    return failed


def main():
    default_base_folder = 'download-videos'
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

    download_video(urls, download_folder)

    print(f"\nDownloads completed. Base folder: '{download_folder}'")

if __name__ == "__main__":
    main()