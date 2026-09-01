import argparse

from dw_music import download_audio
from dw_video import download_video
from dw_core import get_input, show_history

def main():
    parser = argparse.ArgumentParser(description="Download YouTube audio/video via yt-dlp.")
    parser.add_argument("type", nargs="?", choices=["video", "audio"],
                        help="download type (skips the type prompt)")
    parser.add_argument("--resume", action="store_true",
                        help="retry previously failed downloads (saved in .resume/failed.json)")
    parser.add_argument("--workers", type=int, default=None,
                        help="max concurrent downloads (default from config)")
    parser.add_argument("--subfolder", default=None,
                        help="subfolder to save into (skips the folder prompt)")
    parser.add_argument("--history", nargs="?", const="all", metavar="DATE",
                        help="show download history; optionally filter by a date (YYYY-MM-DD)")
    args = parser.parse_args()

    if args.history is not None:
        show_history(filter_date=args.history)
        return

    download_type = args.type
    if download_type is None:
        while True:
            download_type = input("Enter download type (video/audio): ").lower().strip()
            if download_type in ("video", "audio"):
                break
            print("Please enter either 'video' or 'audio'")

    if args.resume:
        default_folder = 'download-videos' if download_type == 'video' else 'download-audios'
        base_folder = args.subfolder or default_folder
        print(f"[resume] Retrying previously failed downloads into '{base_folder}'...")
        if download_type == 'video':
            download_video([], base_folder, max_workers=args.workers, resume=True)
        else:
            download_audio([], base_folder, max_workers=args.workers, resume=True)
        return

    urls, base_folder = get_input(download_type, subfolder=args.subfolder)
    if not urls:
        print("No URLs provided. Exiting.")
        return

    if download_type == 'video':
        download_video(urls, base_folder, max_workers=args.workers)
    else:
        download_audio(urls, base_folder, max_workers=args.workers)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted. Exiting.")
        raise SystemExit(130)