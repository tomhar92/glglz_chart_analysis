
import pandas as pd
from pathlib import Path
from similarity.levenshtein import Levenshtein

levenshtein = Levenshtein()

def look_for_song(name):
    location = 0
    year = 0
    for song in songs_from_charts:
        if levenshtein.distance(song['name'], name) <= 1:
            location = song['location']
            year = song['year']
    return location, year


def create_new_row(old_row):
    row = old_row[1]
    new_row = {}
    new_row['name'] = decade+"_"+row['name'].split(" - ")[0]
    new_row['artist'] = row['artist']
    new_row['artist_first_letter'] = row['artist'][0]
    new_row['artist_songs_ratio'] = int(decade_table[decade_table.artist == row['artist']]['name'].count())/int(decade_table.shape[0])
    try:
        if int(row['year_y']) > 0:
            new_row['year'] = row['year_y']
        else:
            new_row['year'] = row['year_x']
    except:
        new_row['year'] = row['year_x']
    new_row['song_popularity'] = row['song_popularity']
    new_row['artist_popularity'] = row['artist_popularity']
    new_row['duration_ms'] = row['duration_ms']
    new_row['key'] = row['key']
    new_row['time_signature'] = row['time_signature']
    new_row['acousticness'] = row['acousticness']
    new_row['danceability'] = row['danceability']
    new_row['energy'] = row['energy']
    new_row['instrumentalness'] = row['instrumentalness']
    new_row['loudness'] = row['loudness']
    new_row['speechiness'] = row['speechiness']
    new_row['valence'] = row['valence']
    new_row['tempo'] = row['tempo']
    new_row['genres'] = row['genres']
    new_row['views'] = row['views']
    chart_location, chart_year = look_for_song(row['name'].split(" - ")[0])
    if chart_year > 0:
        new_row['year'] = chart_year
    new_row['old_chart_position'] = chart_location
    new_row['new_chart_location'] = old_row[0]
    return new_row

def read_chart_file():
    songs = []
    year = 0
    file_name = "DFs/" + decade + ".txt"
    file = open(file_name, "r", encoding="utf8")

    for line in file.readlines():
        song = {}
        try:
            year = int(line)
        except:
            try:
                song["name"] = line[line.find('"') + 1: len(line)-1]
                song["location"] = int(line.split(".")[0][0:2])
                song["year"] = year
                songs.append(song)
            except:
                print("Empty Line")
    return songs


p = Path('C:/Users/tomha/PycharmProjects/GlglzPredictor/DFs')
print("Which decade are we working on?")
decade = input()
try:
    spotify_table_name = "DFs/spotify_" + decade + ".csv"
    data_from_spotify = pd.read_csv(spotify_table_name)
    wiki_table_name = "DFs/wiki_"+decade+".csv"
    data_from_wiki = pd.read_csv(wiki_table_name)
    decade_table = pd.merge(data_from_spotify, data_from_wiki, right_on=['spotify_name', 'spotify_artist'],
                            left_on=['name', 'artist'])
    list_for_new_table = []
    songs_from_charts = read_chart_file()
    for row in decade_table.iterrows():
        list_for_new_table.append(create_new_row(row))
    new_table = pd.DataFrame(list_for_new_table)
    table_name = "united_" + decade
    export_csv = new_table.to_csv(Path(p, table_name + '.csv'), index=None, header=True)
    print("Saved table successfully")
except Exception as e:
    print(e)


