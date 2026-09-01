import os

AUDIO_FORMAT = 'bestaudio/best'
VIDEO_FORMAT = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best'

PREFERRED_AUDIO_CODEC = 'mp3'
PREFERRED_VIDEO_CODEC = 'mp4'

PREFERRED_AUDIO_QUALITY = '192'
WRITE_THUMBNAIL = True
VERBOSE_MODE = False
QUIET_MODE = False
DEFAULT_OUTTEMPLATE = '%(title)s.%(ext)s'

KEEP_THUMBNAIL = False
TEMPFOLDER = ".TEMPDOWNLOAD"

# Download behavior
MAX_CONCURRENT_DOWNLOADS = 4      # max parallel downloads
MAX_RETRIES = 3                   # attempts per URL before it's marked failed
RETRY_BACKOFF_SECONDS = 2         # base backoff between retries (linear)

# Resume support
RESUME_FOLDER = ".resume"
RESUME_FILE = os.path.join(RESUME_FOLDER, "failed.json")

# Download history (date -> list of successfully downloaded URLs)
HISTORY_FOLDER = ".history"
HISTORY_FILE = os.path.join(HISTORY_FOLDER, "history.json")

# Temp cleanup: partial (.part/.ytdl) files older than this are purged on start
MAX_TEMP_AGE_DAYS = 1