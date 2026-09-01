import os
import glob
import json
import time
import shutil
import uuid
from datetime import date
from concurrent.futures import ThreadPoolExecutor, as_completed

import yt_dlp

from get_playlist import get_playlist_info
from config import (
    DEFAULT_OUTTEMPLATE,
    TEMPFOLDER,
    VERBOSE_MODE,
    QUIET_MODE,
    WRITE_THUMBNAIL,
    KEEP_THUMBNAIL,
    MAX_CONCURRENT_DOWNLOADS,
    MAX_RETRIES,
    RETRY_BACKOFF_SECONDS,
    RESUME_FILE,
    HISTORY_FILE,
    MAX_TEMP_AGE_DAYS,
)

THUMBNAIL_EXTS = ('*.webp', '*.jpg', '*.png', '*.jpeg')

def check_ffmpeg() -> bool:
    """Return True if ffmpeg is available, otherwise print a clear error."""
    if shutil.which("ffmpeg"):
        return True
    print(
        "ERROR: ffmpeg was not found on your system.\n"
        "Audio extraction and video merging require ffmpeg.\n"
        "Install it (e.g. `winget install ffmpeg`, `brew install ffmpeg`,\n"
        "`apt install ffmpeg`, or `choco install ffmpeg`) and add it to PATH."
    )
    return False

def read_urls_from_file(path: str) -> list:
    """Read URLs from a text file (one per line; '#' lines are skipped)."""
    urls = []
    with open(path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            urls.append(line)
    return urls

def get_input(download_type: str, subfolder: str = None):
    """Interactively gather a destination folder and a list of URLs.

    URLs can be typed one per line, or you can enter the path of a .txt file
    (one URL per line). Returns (urls, download_folder); urls may be empty.
    """
    default_base_folder = 'download-videos' if download_type == 'video' else 'download-audios'

    if subfolder:
        download_folder = os.path.join(default_base_folder, subfolder)
    else:
        user_input = input(
            f"Enter a subfolder name to save into (leave blank to use '{default_base_folder}'): "
        ).strip()
        download_folder = os.path.join(default_base_folder, user_input) if user_input else default_base_folder

    print(f"Files will be downloaded to: {download_folder}")

    urls = []
    print(
        "\nEnter URLs one per line. You can also enter the path of a .txt file\n"
        "(one URL per line, '#' lines are ignored).\n"
        "Press Enter on an empty line to finish, or Ctrl+C to exit:"
    )
    while True:
        raw = input("URL/file: ").strip()
        if not raw:
            break
        if raw.lower().endswith('.txt') and os.path.isfile(raw):
            file_urls = read_urls_from_file(raw)
            if file_urls:
                urls.extend(file_urls)
                print(f"  -> loaded {len(file_urls)} URL(s) from '{raw}'")
            else:
                print(f"  -> no URLs found in '{raw}'")
        else:
            urls.append(raw)

    return urls, download_folder

def delete_thumbnails(folder):
    deleted = 0
    for ext in THUMBNAIL_EXTS:
        for file in glob.glob(os.path.join(folder, ext)):
            try:
                os.remove(file)
                deleted += 1
            except OSError as e:
                print(f"Failed to delete {file}: {e}")

    if deleted == 0:
        print("No thumbnails found to delete.")

def resolve_cookies(cookie_source):
    """Translate a cookie setting into yt-dlp opts.

    cookie_source may be:
      * False/None        -> no cookies
      * True              -> use .cookies/cookies.txt
      * a file path       -> use that cookies file
      * 'browser:NAME'    -> pull cookies from an installed browser (e.g. 'browser:firefox')
    """
    if cookie_source is True:
        path = os.path.join('.cookies', 'cookies.txt')
        os.makedirs('.cookies', exist_ok=True)
        return {'cookiefile': path}
    if isinstance(cookie_source, str):
        if cookie_source.startswith('browser:'):
            return {'cookiesfrombrowser': (cookie_source.split(':', 1)[1],)}
        return {'cookiefile': cookie_source}
    return {}

def get_common_ydl_opts(format, download_folder, outtemplate, is_playlist, postprocessors=None, cookie_source=False):
    opts = {
        'format': format,
        'outtmpl': os.path.join(download_folder, outtemplate),
        'noplaylist': not is_playlist,
        'verbose': VERBOSE_MODE,
        'quiet': QUIET_MODE,
        'writethumbnail': WRITE_THUMBNAIL,
        'continuedl': True,
    }

    if postprocessors:
        opts['postprocessors'] = postprocessors

    opts.update(resolve_cookies(cookie_source))

    return opts

def _is_partial(name):
    return name.endswith('.part') or name.endswith('.ytdl')

def _move_file_safely(src, dst):
    """Move src to dst without ever silently overwriting an existing file."""
    if os.path.exists(dst):
        base, ext = os.path.splitext(dst)
        n = 1
        while os.path.exists(f"{base} ({n}){ext}"):
            n += 1
        dst = f"{base} ({n}){ext}"
    os.replace(src, dst)

def _remove_partials(folder):
    if not os.path.isdir(folder):
        return
    for name in os.listdir(folder):
        path = os.path.join(folder, name)
        if os.path.isfile(path) and _is_partial(name):
            try:
                os.remove(path)
            except OSError:
                pass

def clean_stale_temp(folder=TEMPFOLDER, max_age_days=MAX_TEMP_AGE_DAYS):
    """Remove .part/.ytdl files (older than max_age_days) and empty subfolders
    left behind by crashed runs. Fresh partials survive so a --resume run can
    continue them."""
    if not os.path.isdir(folder):
        return
    cutoff = time.time() - max_age_days * 86400
    removed = 0
    for root, dirs, files in os.walk(folder, topdown=False):
        for name in files:
            path = os.path.join(root, name)
            if _is_partial(name) and os.path.getmtime(path) < cutoff:
                try:
                    os.remove(path)
                    removed += 1
                except OSError:
                    pass
        try:
            os.rmdir(root)  # only succeeds on empty dirs
        except OSError:
            pass
    if removed:
        print(f"[cleanup] Removed {removed} stale partial file(s) from '{folder}'")

def save_failed_records(records, resume_file=RESUME_FILE):
    """records: iterable of {"url":..., "base_folder":...} dicts (or (url, base) pairs)."""
    cleaned = []
    for item in records:
        if isinstance(item, dict):
            cleaned.append({"url": item["url"], "base_folder": item.get("base_folder")})
        else:
            url, base = item
            cleaned.append({"url": url, "base_folder": base})

    if not cleaned:
        try:
            os.remove(resume_file)
        except OSError:
            pass
        return

    os.makedirs(os.path.dirname(resume_file), exist_ok=True)
    with open(resume_file, 'w', encoding='utf-8') as f:
        json.dump(cleaned, f, indent=2)

def load_failed_records(resume_file=RESUME_FILE):
    """Return a list of {"url":..., "base_folder":...} dicts from the resume file."""
    try:
        with open(resume_file, encoding='utf-8') as f:
            data = json.load(f)
    except (OSError, ValueError):
        return []

    records = []
    if isinstance(data, list):
        for item in data:
            if isinstance(item, str):
                records.append({"url": item, "base_folder": None})
            elif isinstance(item, dict) and item.get("url"):
                records.append({"url": item["url"], "base_folder": item.get("base_folder")})
    return records

def load_history(history_file=HISTORY_FILE):
    """Return {date_str: [urls]} from the history file (empty dict if none)."""
    try:
        with open(history_file, encoding='utf-8') as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def record_downloads(urls, history_file=HISTORY_FILE):
    """Append successfully downloaded URLs to today's entry in the history file."""
    if not urls:
        return

    today = date.today().isoformat()
    history = load_history(history_file)
    entry = history.setdefault(today, [])
    seen = set(entry)
    added = [u for u in urls if u not in seen]
    if not added:
        return

    entry.extend(added)
    os.makedirs(os.path.dirname(history_file), exist_ok=True)
    with open(history_file, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

    print(f"[history] Recorded {len(added)} download(s) to '{history_file}'")


def show_history(history_file=HISTORY_FILE, filter_date=None):
    """Print the download history, optionally filtered to a single date."""
    history = load_history(history_file)

    if not history:
        print(f"No download history found at '{history_file}'.")
        return

    if filter_date and filter_date != "all":
        if filter_date in history:
            print(f"\nDownloads on {filter_date}:")
            for url in history[filter_date]:
                print(f"  - {url}")
        else:
            print(f"No downloads recorded on {filter_date}.")
        return

    print(f"\nDownload history ({history_file}):")
    for d in sorted(history, reverse=True):
        urls = history[d]
        print(f"{d}  ({len(urls)} download(s))")
        for u in urls:
            print(f"   - {u}")


def _determine_destination(url, base_folder):
    is_playlist, playlist_title = get_playlist_info(url)
    if is_playlist and playlist_title:
        final_folder = os.path.join(base_folder, playlist_title)
        print(f"[download] Playlist '{playlist_title}' -> '{final_folder}'")
    else:
        final_folder = base_folder
        print(f"[download] Single link -> '{final_folder}'")
    return is_playlist, final_folder


def _download_one(url, base_folder, fmt, postprocessors, preferred_merge_format,
                  keep_thumbs, cookie_source, task_id):
    """Download a single URL (with retries), then move finished files out of temp."""
    temp_dir = os.path.join(TEMPFOLDER, task_id)
    os.makedirs(temp_dir, exist_ok=True)

    is_playlist, final_folder = _determine_destination(url, base_folder)
    ydl_opts = get_common_ydl_opts(
        format=fmt,
        download_folder=temp_dir,
        outtemplate=DEFAULT_OUTTEMPLATE,
        is_playlist=is_playlist,
        postprocessors=postprocessors,
        cookie_source=cookie_source,
    )
    if preferred_merge_format:
        ydl_opts['merge_output_format'] = preferred_merge_format

    last_error = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                result = ydl.download([url])
            if result == 0:
                last_error = None
                break
            last_error = f"yt-dlp returned exit code {result}"
        except Exception as e:
            last_error = str(e)

        print(f"[retry {attempt}/{MAX_RETRIES}] Failed: {url} -> {last_error}")
        if attempt < MAX_RETRIES:
            time.sleep(RETRY_BACKOFF_SECONDS * attempt)

    if last_error is not None:
        _remove_partials(temp_dir)
        return False, last_error

    if not keep_thumbs:
        delete_thumbnails(temp_dir)

    os.makedirs(final_folder, exist_ok=True)
    for name in os.listdir(temp_dir):
        src = os.path.join(temp_dir, name)
        if os.path.isfile(src) and not _is_partial(name):
            _move_file_safely(src, os.path.join(final_folder, name))

    try:
        os.rmdir(temp_dir)
    except OSError:
        pass

    return True, None

def download_media(urls, base_folder, format, postprocessors=None, preferred_merge_format=None,
                   keep_thumbs=KEEP_THUMBNAIL, use_cookies=False,
                   max_workers=None, resume=False):
    """Download `urls` in parallel with per-URL retries and optional resume.

    Returns the list of failed records ({"url": ..., "base_folder": ...}).
    """
    max_workers = max_workers or MAX_CONCURRENT_DOWNLOADS
    os.makedirs(TEMPFOLDER, exist_ok=True)
    clean_stale_temp()

    tasks = [(url, base_folder) for url in urls]

    if resume:
        previous = load_failed_records()
        existing = {u for u, _ in tasks}
        added = [r for r in previous if r["url"] not in existing]
        if added:
            print(f"[resume] Re-attempting {len(added)} previously failed URL(s).")
            for r in added:
                tasks.append((r["url"], r.get("base_folder") or base_folder))
        else:
            print("[resume] No previously failed URLs to retry.")

    if not tasks:
        print("No URLs to download.")
        return []

    print(f"\nDownloading {len(tasks)} item(s) with up to {max_workers} concurrent worker(s)...\n")

    failed = []
    completed = set()
    executor = ThreadPoolExecutor(max_workers=max_workers)
    try:
        futures = {
            executor.submit(
                _download_one, url, bf, format, postprocessors,
                preferred_merge_format, keep_thumbs, use_cookies, uuid.uuid4().hex,
            ): (url, bf)
            for url, bf in tasks
        }
        for future in as_completed(futures):
            url, bf = futures[future]
            try:
                ok, err = future.result()
            except Exception as e:
                ok, err = False, str(e)
            if ok:
                completed.add(url)
                print(f"OK     : {url}")
            else:
                failed.append({"url": url, "base_folder": bf})
                print(f"FAILED : {url} -> {err}")
    except KeyboardInterrupt:
        print("\nInterrupted by user. Cancelling remaining downloads...")
        executor.shutdown(wait=False, cancel_futures=True)
        failed_urls = {r['url'] for r in failed}
        remaining = [
            {"url": futures[f][0], "base_folder": futures[f][1]}
            for f in futures
            if futures[f][0] not in completed and futures[f][0] not in failed_urls
        ]
        save_failed_records(failed + remaining)
        print(f"Unfinished downloads saved to '{RESUME_FILE}'. Run again with --resume.")
        raise SystemExit(130)
    else:
        executor.shutdown(wait=True)

    record_downloads(sorted(completed))
    save_failed_records(failed)

    ok_count = len(tasks) - len(failed)
    print(f"\nDownloads completed: {ok_count}/{len(tasks)} succeeded, {len(failed)} failed.")
    if failed:
        print(f"Failed URLs saved to '{RESUME_FILE}'. Run again with --resume to retry them.")

    return failed