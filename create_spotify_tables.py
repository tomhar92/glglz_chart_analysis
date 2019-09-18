import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from pathlib import Path

def create_spotify_song(track):
    song = {}
    song["name"] = track["name"]
    song["artist"] = track["artists"][0]["name"]
    song["year"] = track["album"]["release_date"].split("-")[0]
    song["song_popularity"] = track["popularity"]
    song["artist_popularity"] = sp.artist(track['artists'][0]['id'])['popularity']
    song["duration_ms"] = track['duration_ms']
    audio_features = sp.audio_features(track['id'])[0]
    song["key"] = audio_features["key"]
    song["mode"] = audio_features["mode"]
    song["time_signature"] = audio_features["time_signature"]
    song["acousticness"] = audio_features["acousticness"]
    song["danceability"] = audio_features['danceability']
    song['energy'] = audio_features['energy']
    song['instrumentalness'] = audio_features['instrumentalness']
    song['loudness'] = audio_features['loudness']
    song['speechiness'] = audio_features['speechiness']
    song['valence'] = audio_features['valence']
    song['tempo'] = audio_features['tempo']
    return song


def select_playlist():
    if decade == "seventies":
        return '2LtVnWav9EvYZMfmHqOoTw'
    elif decade == "eighties":
        return '1a7ijyJwH7ioBt2E00rVeQ'
    elif decade == "nineties":
        return '72VsyfunVdH9b6PjVNYXo4'
    elif decade == "thousands":
        return '69stUw4FfYwL9851TCHjOx'
    else:
        print("no such decade!")
        exit()

def get_playlist_tracks():
    playlist_id = select_playlist()
    results = sp.user_playlist_tracks("glglz",playlist_id=playlist_id)
    tracks = results['items']
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])
    return tracks


def create_spotify_df():
    spotify_songs = []
    for item in tracks:
        spotify_song = create_spotify_song(item['track'])
        spotify_songs.append(spotify_song)
        if len(spotify_songs)%100 == 0:
            print("Fetched "+str(len(spotify_songs))+" songs")
    spotify_df = pd.DataFrame(spotify_songs)
    table_name = "spotify_"+decade
    export_csv = spotify_df.to_csv(Path(p,table_name + '.csv'), index=None,
                              header=True)
    print("Saved table successfully")


client_credentials_manager = SpotifyClientCredentials(client_id='***', client_secret='***')
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
print("Which decade are we working on?")
decade = input()
tracks = get_playlist_tracks()
p = Path('C:/Users/tomha/PycharmProjects/GlglzPredictor/DFs/')
create_spotify_df()