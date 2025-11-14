import os
import sys

try:
    from spotify_exporter import export_spotify_data
    from get_yt_urls import search_youtube_urls
    from download_music import download_music
except ImportError as e:
    print(f"ERREUR D'IMPORTATION : Assurez-vous que spotify_exporter.py, get_yt_urls.py, et download_music.py sont presents et syntaxiquement corrects.")
    print(f"Detail de l'erreur: {e}")
    sys.exit(1)

def cleanup_files(files_to_delete):
    print("\n--- Nettoyage des fichiers intermediaires ---")
    deleted_count = 0
    for f in files_to_delete:
        if os.path.exists(f):
            try:
                os.remove(f)
                print(f"Fichier supprime : {f}")
                deleted_count += 1
            except OSError as e:
                print(f"Erreur de suppression du fichier {f}: {e}")
    print(f"Nettoyage termine. {deleted_count} fichiers supprimes.")


def run_full_workflow():
    print("--- Demarrage du Workflow Automatise ---")

    intermediate_files = []
    csv_filename = None
    urls_filename = None
    
    print("\n[ETAPE 1/3] : Exportation Spotify vers CSV...")
    try:
        csv_filename = export_spotify_data()
        
        if not csv_filename:
            print("Echec de l'exportation Spotify. Abandon du workflow.")
            return
            
        intermediate_files.append(csv_filename)
        print(f"Exportation Spotify reussie. Fichier CSV : {csv_filename}")
        
    except Exception as e:
        print(f"Erreur lors de l'etape 1 : {e}. Abandon.")
        return

    print("\n[ETAPE 2/3] : Recherche des URLs YouTube...")
    try:
        urls_filename = search_youtube_urls(csv_filename)
        
        if not urls_filename:
            print("Echec de la recherche d'URLs YouTube. Abandon du workflow.")
            cleanup_files(intermediate_files)
            return
            
        intermediate_files.append(urls_filename)
        print(f"Recherche YouTube reussie. Fichier URLs : {urls_filename}")
        
    except Exception as e:
        print(f"Erreur lors de l'etape 2 : {e}. Abandon.")
        cleanup_files(intermediate_files)
        return

    print("\n[ETAPE 3/3] : Telechargement et conversion en MP3...")
    try:
        download_music(urls_filename) 
        
        print("Telechargement termine avec succes.")
        
    except Exception as e:
        print(f"Erreur fatale lors de l'etape 3 : {e}.")
        cleanup_files(intermediate_files)
        return

    print("\n--- Workflow termine ---")
    cleanup_files(intermediate_files)


if __name__ == "__main__":
    run_full_workflow()