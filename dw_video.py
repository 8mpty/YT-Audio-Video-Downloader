from config import VIDEO_FORMAT, PREFERRED_VIDEO_CODEC, KEEP_THUMBNAIL
from dw_core import download_media, get_input, check_ffmpeg

def download_video(urls, base_folder, keep_thumbs=KEEP_THUMBNAIL, use_cookies=False, max_workers=None, resume=False):
    if not check_ffmpeg():
        return []

    output = download_media(
        urls=urls,
        base_folder=base_folder,
        format=VIDEO_FORMAT,
        preferred_merge_format=PREFERRED_VIDEO_CODEC,
        keep_thumbs=keep_thumbs,
        use_cookies=use_cookies,
        max_workers=max_workers,
        resume=resume,
    )
    return output


def main():
    urls, base_folder = get_input("video")
    if not urls:
        return
    download_video(urls, base_folder)

if __name__ == "__main__":
    main()