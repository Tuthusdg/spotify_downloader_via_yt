import yt_dlp
import os
import sys
import subprocess
from tqdm import tqdm

def get_default_music_folder():
    if sys.platform == 'win32':
        return os.path.join(os.environ['USERPROFILE'], 'Music')
    elif sys.platform == 'darwin':
        return os.path.join(os.path.expanduser('~'), 'Music')
    elif sys.platform.startswith('linux'):
        return os.path.join(os.path.expanduser('~'), 'Music')
    else:
        return 'Musique_Telechargee'

def check_ffmpeg():
    try:
        subprocess.run(['ffmpeg', '-version'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False

def download_music(urls_file):
    
    if not check_ffmpeg():
        print("\n---------------------------------------------------------------------------------")
        print("ERREUR : FFmpeg n'est pas installe. La conversion en MP3 est impossible.")
        print("---------------------------------------------------------------------------------")
        return

    if not os.path.exists(urls_file):
        print(f"ERREUR : Le fichier d'URLs '{urls_file}' est introuvable pour le telechargement.")
        return
    
    base_name = os.path.basename(urls_file)
    playlist_folder_name = base_name.replace('_urls.txt', '')

    default_music_path = get_default_music_folder()
    download_dir = os.path.join(default_music_path, playlist_folder_name) 
        
    os.makedirs(download_dir, exist_ok=True)
    print(f"--- Preparation : Telechargement vers : '{download_dir}' ---")

    ydl_opts = {
        'format': 'bestaudio/best', 'extract_audio': True, 'audio_format': 'mp3',
        'outtmpl': os.path.join(download_dir, '%(title)s.%(ext)s'), 
        'verbose': False, 'noprogress': True,
        'ignoreerrors': True, 
        'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}],
    }

    with open(urls_file, 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip()]

    if not urls:
        print("Le fichier d'URLs est vide. Aucune musique a telecharger.")
        return

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            for url in tqdm(urls, desc="Telechargement des titres"):
                ydl.download([url]) 
            
    except Exception as e:
        print(f"Une erreur inattendue est survenue: {e}")
        
    print(f"\nTelechargement termine. Fichiers enregistres dans '{download_dir}'.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python download_music.py <nom_du_fichier_urls.txt>")
        sys.exit(1)
        
    download_music(sys.argv[1])