from dw_music import download_audio
from dw_video import download_video

def main():
    while True:
        download_type = input("Enter download type (video/audio): ").lower()
        if download_type in ['video', 'audio']:
            break
        print("Please enter either 'video' or 'audio'")

    default_folder = 'download-videos' if download_type == 'video' else 'download-audios'
    download_folder = input(f"Enter the download folder path (leave blank for default '{default_folder}'): ")
    if not download_folder.strip():
        download_folder = default_folder

    urls = []
    print("\nEnter YouTube URLs (type 'done' to finish):")
    while True:
        url = input("URL: ").strip()
        if url.lower() == 'done':
            break
        if url:
            urls.append(url)

    if not urls:
        print("No URLs provided. Exiting...")
        return

    if download_type == 'video':
        download_video(urls, download_folder)
    else:
        download_audio(urls, download_folder)
            
    print(f"\nDownloads completed. Base folder: '{download_folder}'")

if __name__ == "__main__":
    main()