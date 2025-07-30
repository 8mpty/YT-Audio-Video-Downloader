import os
from dw_music import download_audio
from dw_video import download_video

def main():
    while True:
        download_type = input("Enter download type (video/audio): ").lower()
        if download_type in ['video', 'audio']:
            break
        print("Please enter either 'video' or 'audio'")

    default_base_folder = 'download-videos' if download_type == 'video' else 'download-audios'
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

    if download_type == 'video':
        download_video(urls, download_folder)
    else:
        download_audio(urls, download_folder)
            
    print(f"\nDownloads completed. Base folder: '{download_folder}'")

if __name__ == "__main__":
    main()