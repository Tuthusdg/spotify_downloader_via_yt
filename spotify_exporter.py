import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
from dotenv import load_dotenv 
import os
import sys

load_dotenv()
CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI", 'http://127.0.0.1:9090') 
SCOPE = 'playlist-read-private user-library-read' 

def authenticate_spotify_generic():
    if not CLIENT_ID or not CLIENT_SECRET:
        print("ERREUR: Le fichier .env n'est pas correctement configure.")
        return None
    try:
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=CLIENT_ID, client_secret=CLIENT_SECRET, 
            redirect_uri=REDIRECT_URI, scope=SCOPE, cache_path=".spotipy_cache" 
        ))
        print("Authentification reussie.")
        return sp
    except Exception as e:
        print(f"Erreur lors de l'authentification. Erreur: {e}")
        return None

def get_user_playlist_choice(sp):
    print("\n--- Playlists de votre bibliotheque ---")
    
    playlist_items = [{'index': 1, 'name': "Coups de Coeur (Liked Songs)", 'identifier': 'LIKED_SONGS_ENDPOINT'}]
    user_me = sp.me()
    if user_me is None:
        print("Impossible de recuperer les informations de l'utilisateur.")
        return None

    current_user_id = user_me['id']
    playlists = sp.current_user_playlists()
    
    while playlists:
        for playlist in playlists['items']:
            if playlist['owner']['id'] == current_user_id or playlist['owner']['display_name'] != 'Spotify':
                playlist_items.append({'index': len(playlist_items) + 1, 'name': playlist['name'], 'identifier': playlist['external_urls']['spotify']})
        if playlists['next']: playlists = sp.next(playlists)
        else: playlists = None

    for item in playlist_items:
        print(f"[{item['index']}]: {item['name']}")

    while True:
        try:
            choice = input("\nEntrez le numero de la playlist a exporter (ou 'Q' pour quitter) : ").strip()
            if choice.upper() == 'Q': return None
            choice_index = int(choice) - 1
            if 0 <= choice_index < len(playlist_items):
                return playlist_items[choice_index]['identifier']
            else: print("Choix invalide.")
        except ValueError: print("Entree invalide.")
            
def get_playlist_tracks(sp, playlist_identifier):
    tracks_data = []
    try:
        if playlist_identifier == 'LIKED_SONGS_ENDPOINT':
            playlist_name = "Coups_de_Coeur_Liked_Songs"
            results = sp.current_user_saved_tracks()
        else:
            playlist_id = playlist_identifier.split('/')[-1].split('?')[0]
            playlist = sp.playlist(playlist_id)
            playlist_name = playlist['name']
            results = sp.playlist_items(playlist_id)

        tracks = results['items']
        while results['next']:
            results = sp.next(results)
            tracks.extend(results['items'])

        for item in tracks:
            if item and item.get('track') and item['track'] and item['track'].get('id'):
                track = item['track']
                title = track['name']
                artists = ", ".join([artist['name'] for artist in track['artists']])
                tracks_data.append({'Titre': title, 'Artistes': artists})
        
        return tracks_data, playlist_name
    except Exception as e:
        print(f"Erreur lors de la recuperation des titres. Erreur: {e}")
        return None, None

def export_spotify_data():
    sp = authenticate_spotify_generic()
    if not sp: return None

    playlist_identifier = get_user_playlist_choice(sp)
    if not playlist_identifier: return None

    tracks_data, playlist_name = get_playlist_tracks(sp, playlist_identifier)

    if tracks_data:
        df = pd.DataFrame(tracks_data)
        safe_playlist_name = "".join([c for c in playlist_name if c.isalnum() or c in (' ', '_', '-')]).rstrip().replace(' ', '_')
        csv_filename = f"{safe_playlist_name}_tracks.csv"
        
        df.to_csv(csv_filename, index=False, encoding='utf-8')
        
        return csv_filename
    
    return None

if __name__ == "__main__":
    print("Mode test du script d'exportation. Le coordinateur sera execute automatiquement.")
    export_spotify_data()