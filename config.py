import os, glob

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

def delete_thumbnails(folder):
    thumbnail_exts = ['*.webp']

    deleted_files = 0
    for ext in thumbnail_exts:
        for file in glob.glob(os.path.join(folder, ext)):
            try:
                os.remove(file)
                print(f"Deleted thumbnail: {file}")
                deleted_files += 1
            except Exception as e:
                print(f"Failed to delete {file}: {str(e)}")

    if deleted_files == 0:
        print("No thumbnails found to delete.")