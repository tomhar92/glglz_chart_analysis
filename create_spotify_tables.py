import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from pathlib import Path

class spotify_table:
    client_credentials_manager = SpotifyClientCredentials(client_id='274d5abed01c455099ac8ad14c6a68e8',
                                                          client_secret='7425a61db8ed45c48d1ccfaa39842e00')
    p = Path('C:/Users/tomha/PycharmProjects/GlglzPredictor/DFs/')

    def __init__(self, decade):
        self.sp = spotipy.Spotify(client_credentials_manager=self.client_credentials_manager)
        self.decade = decade
        self.tracks = self.get_playlist_tracks()
        self.df = self.create_spotify_df()

    def create_spotify_song(self, track):
        song = {}
        song["name"] = track["name"]
        song["artist"] = track["artists"][0]["name"]
        song["year"] = track["album"]["release_date"].split("-")[0]
        song["song_popularity"] = track["popularity"]
        song["artist_popularity"] = self.sp.artist(track['artists'][0]['id'])['popularity']
        song["duration_ms"] = track['duration_ms']
        audio_features = self.sp.audio_features(track['id'])[0]
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


    def select_playlist(self):
        if self.decade == "seventies":
            return '2LtVnWav9EvYZMfmHqOoTw'
        elif self.decade == "eighties":
            return '1a7ijyJwH7ioBt2E00rVeQ'
        elif self.decade == "nineties":
            return '72VsyfunVdH9b6PjVNYXo4'
        elif self.decade == "thousands":
            return '69stUw4FfYwL9851TCHjOx'
        else:
            print("no such decade!")
            exit()

    def get_playlist_tracks(self):
        playlist_id = self.select_playlist()
        results = self.sp.user_playlist_tracks("glglz",playlist_id=playlist_id)
        tracks = results['items']
        while results['next']:
            results = self.sp.next(results)
            tracks.extend(results['items'])
        return tracks


    def create_spotify_df(self):
        spotify_songs = []
        for item in self.tracks:
            spotify_song = self.create_spotify_song(item['track'])
            spotify_songs.append(spotify_song)
            if len(spotify_songs)%100 == 0:
                print("Fetched "+str(len(spotify_songs))+" songs")
        spotify_df = pd.DataFrame(spotify_songs)
        table_name = "spotify_"+self.decade
        export_csv = spotify_df.to_csv(Path(self.p,table_name + '.csv'), index=None,
                              header=True)
        print("Saved table successfully")
        return spotify_df


