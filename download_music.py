import yt_dlp
import os
import sys
import subprocess
from tqdm import tqdm

def get_default_music_folder():
    if sys.platform == 'win32':
        return os.path.join(os.environ['USERPROFILE'], 'Music')
    elif sys.platform == 'darwin':
        return os.path.expanduser('~/Music')
    elif sys.platform.startswith('linux'):
        return os.path.expanduser('~/Music')
    else:
        return 'Musique_Telechargee'

def check_ffmpeg():
    try:
        subprocess.run(['ffmpeg', '-version'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return True
    except:
        return False

def download_music(urls_file):

    if not check_ffmpeg():
        print("❌ FFmpeg n'est pas installé.")
        return

    if not os.path.exists(urls_file):
        print(f"❌ Le fichier '{urls_file}' est introuvable.")
        return
    
    base_name = os.path.basename(urls_file)
    playlist_folder_name = base_name.replace('_urls.txt', '')
    download_dir = os.path.join(get_default_music_folder(), playlist_folder_name)
    os.makedirs(download_dir, exist_ok=True)

    print(f"📥 Téléchargement vers : {download_dir}")

    ydl_opts = {
        'format': 'bestaudio/best',

        # ✅ Nom du fichier propre
        'outtmpl': os.path.join(download_dir, '%(artist)s - %(title)s.%(ext)s'),

        # ✅ Téléchargement + intégration cover
        'writethumbnail': True,
        'embedthumbnail': True,

        # ✅ Empêche les pauses de 5s
        'sleep_interval': 0,
        'max_sleep_interval': 0,

        # ✅ Empêche les pauses liées au throttle
        'throttledratelimit': 0,

        'ignoreerrors': True,
        'noprogress': True,

        'postprocessors': [
            # ✅ Étape 1 : Conversion en MP3
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192'
            },

            # ✅ Étape 2 : Intégration de la cover
            {
                'key': 'EmbedThumbnail'
            },

            # ✅ Étape 3 : Extraction métadonnées Artiste & Titre
            {
                'key': 'MetadataFromTitle',
                'titleformat': '%(artist)s - %(title)s'
            },

            # ✅ Étape 4 : Tags ID3 (dont Artiste)
            {
                'key': 'FFmpegMetadata',
                'add_metadata': True
            }
        ],

        # ✅ Obligatoire pour Cover + ID3 propre
        'postprocessor_args': {
            'FFmpegMetadata': ['-id3v2_version', '3']
        }
    }

    with open(urls_file, 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip()]

    if not urls:
        print("❌ Aucun lien trouvé.")
        return

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            for url in tqdm(urls, desc="Téléchargement"):
                ydl.download([url])

    except Exception as e:
        print(f"⚠ Erreur : {e}")
        
    print(f"\n✅ Terminé ! Fichiers enregistrés dans : {download_dir}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python download_music.py <fichier_urls.txt>")
        sys.exit(1)
        
    download_music(sys.argv[1])
