from config import AUDIO_FORMAT, PREFERRED_AUDIO_CODEC, PREFERRED_AUDIO_QUALITY, KEEP_THUMBNAIL
from dw_core import download_media, get_input, check_ffmpeg

def download_audio(urls, base_folder, keep_thumbs=KEEP_THUMBNAIL, use_cookies=False, max_workers=None, resume=False):
    if not check_ffmpeg():
        return []

    postprocessors = [
        {
            'key': 'FFmpegExtractAudio',
            'preferredcodec': PREFERRED_AUDIO_CODEC,
            'preferredquality': PREFERRED_AUDIO_QUALITY,
        },
        {'key': 'FFmpegMetadata'},
        {'key': 'EmbedThumbnail'},
    ]

    return download_media(
        urls=urls,
        base_folder=base_folder,
        format=AUDIO_FORMAT,
        postprocessors=postprocessors,
        keep_thumbs=keep_thumbs,
        use_cookies=use_cookies,
        max_workers=max_workers,
        resume=resume,
    )

def main():
    try:
        urls, base_folder = get_input("audio")
        if not urls:
            return
        download_audio(urls, base_folder)
    except KeyboardInterrupt:
        print("\nInterrupted. Exiting.")
        raise SystemExit(130)

if __name__ == "__main__":
    main()