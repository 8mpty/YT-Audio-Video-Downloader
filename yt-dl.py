from dw_music import download_audio_with_metadata
from dw_video import download_video

def main():
    # Get download type
    while True:
        download_type = input("Enter download type (video/audio): ").lower()
        if download_type in ['video', 'audio']:
            break
        print("Please enter either 'video' or 'audio'")

    # Get download folder
    default_folder = 'download-videos' if download_type == 'video' else 'download-audios'
    download_folder = input(f"Enter the download folder path (leave blank for default '{default_folder}'): ")
    if not download_folder.strip():
        download_folder = default_folder

    # Get URLs
    urls = []
    print("\nEnter YouTube URLs (type 'done' to finish):")
    while True:
        url = input("URL: ")
        if url.lower() == 'done':
            break
        urls.append(url)

    if not urls:
        print("No URLs provided. Exiting...")
        return

    # Download based on type
    if download_type == 'video':
        download_video(urls, download_folder)
    else:
        # For audio, process each URL individually to handle playlists
        for url in urls:
            download_audio_with_metadata(url, download_folder)

    print(f"\nDownloads completed. Base folder: '{download_folder}'")

if __name__ == "__main__":
    main()