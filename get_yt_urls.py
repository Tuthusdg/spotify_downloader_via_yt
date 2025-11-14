import pandas as pd
import yt_dlp
import sys
import os
from tqdm import tqdm
import time 


def find_youtube_url(artist, title):
    search_query = f"ytsearch1:{artist} - {title}" 
    
    ydl_opts = {
        'format': 'bestaudio/best', 'noplaylist': True, 'quiet': True, 'extract_flat': True, 
        'force_generic_extractor': True, 'default_search': 'ytsearch', 'skip_download': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'no_warnings': True,
        'retries': 5, 
        'retry_sleep': 5,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(search_query, download=False)
            
            if info and 'entries' in info and info['entries']:
                video_id = info['entries'][0].get('id')
                if video_id:
                    return f"https://www.youtube.com/watch?v={video_id}"
                
    except Exception:
        pass 
        
    return None


def search_youtube_urls(csv_filename):
    if not os.path.exists(csv_filename):
        print(f"ERREUR : Le fichier CSV '{csv_filename}' est introuvable pour la recherche.")
        return None

    try:
        df = pd.read_csv(csv_filename)
    except Exception as e:
        print(f"ERREUR : Impossible de lire le fichier CSV. {e}")
        return None

    output_filename = csv_filename.replace('_tracks.csv', '_urls.txt').replace('.csv', '_urls.txt')
        
    url_count = 0
    total_tracks = len(df)
    
    with open(output_filename, 'w', encoding='utf-8') as f:
        for index, row in tqdm(df.iterrows(), total=total_tracks, desc="Recherche YouTube"):
            title = row['Titre']
            artists = row['Artistes']
            
            youtube_url = find_youtube_url(artists, title)

            
            if youtube_url:
                f.write(f"{youtube_url}\n")
                url_count += 1
            
    print(f"\nTermine : {url_count}/{total_tracks} URLs trouvees.")
    return output_filename

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python get_yt_urls.py <nom_du_fichier.csv>")
        sys.exit(1)
    
    search_youtube_urls(sys.argv[1])