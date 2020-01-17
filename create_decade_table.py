
import pandas as pd
from pathlib import Path
import sys
import re
from similarity.levenshtein import Levenshtein
from create_wiki_tables import wiki_table
from create_spotify_tables import spotify_table
from handle_original_chart import original_table

class decade_table:
    levenshtein = Levenshtein()
    decade_dict = {
        'seventies': [1969, 1980],
        'eighties': [1979, 1990],
        'nineties': [1989, 2000],
        'thousands': [1999, 2010]
    }
    p = Path('C:/Users/tomha/PycharmProjects/GlglzPredictor/DFs')

    def __init__(self):
        print("Which decade are we working on?")
        self.decade = input()
        self.songs_from_charts = self.read_chart_file()
        self.spoti_table = None
        self.wikipedia_table = None

        spoti = input("Create Spotify Table?")
        if spoti == 'Y' or spoti == 'y' or spoti == 'yes':
            self.spoti_table = spotify_table(self.decade)
        else:
            self.spoti_table =  pd.read_csv("DFs/spotify_" + self.decade + ".csv")

        wiki = input("Create Wikipedia Table?")
        if wiki == 'Y' or wiki == 'y' or wiki == 'yes':
            self.wikipedia_table = wiki_table(self.decade)
        else:
            self.wikipedia_table = pd.read_csv("DFs/wiki_" + self.decade + ".csv")
        decade = input("Create decade Table?")
        if decade == 'Y' or decade == 'y' or decade == 'yes':
            self.decade_table = self.merge_table()
        else:
            self.decade_table = pd.read_csv("DFs/united_" + self.decade + ".csv")

        original = input("Handle original chart?")
        if original == 'Y' or original == 'y' or original == 'yes':
            self.original_chart = original_table(self.decade)
            self.update_year_in_original_chart()

    def merge_table(self):
        temp_table = pd.merge(self.spoti_table, self.wikipedia_table, right_on=['spotify_name'],
                                     left_on=['name'])
        list_for_new_table = []
        print("Please tag release years of the following songs")
        for row in temp_table.iterrows():
            list_for_new_table.append(self.create_new_row(row))
        new_table = pd.DataFrame(list_for_new_table)
        table_name = "united_" + self.decade
        export_csv = new_table.to_csv(Path(self.p, table_name + '.csv'), index=None, header=True)
        print("Saved table successfully")
        return new_table

    def look_for_song(self, name):
        location = 0
        year = 0
        for song in self.songs_from_charts:
            if self.levenshtein.distance(song['name'].split(" - ")[1], name) <= 1:
                location = song['location']
                year = song['year']
        return location, year

    def create_new_row(self, old_row):
        row = old_row[1]
        new_row = {}
        new_row['name'] = self.decade+"_"+row['name'].split(" - ")[0]
        if len(row['name'].split(" - ")) > 1:
            new_row['version_exists'] = 1
        else:
            new_row['version_exists'] = 0
        new_row['artist'] = row['artist']
        if row['artist'][:2] == 'The' or row['artist'][:2] == 'the':
            new_row['artist_first_letter'] = row['artist'][4]
        else:
            new_row['artist_first_letter'] = row['artist'][0]
        try:
            if int(row['year_y']) > self.decade_dict[self.decade][0] and int(row['year_y']) < self.decade_dict[self.decade][1]:
                new_row['year'] = row['year_y']
                new_row['year_source'] = 'wikipedia'
            elif int(row['year_x']) > self.decade_dict[self.decade][0] and int(row['year_x']) < self.decade_dict[self.decade][1]:
                new_row['year'] = row['year_x']
                new_row['year_source'] = 'spotify'
            else:
                new_row['year'] = input(new_row['name']+" "+new_row['artist'])
                new_row['year_source'] = 'manual'
        except:
            new_row['year'] = input(new_row['name']+" "+new_row['artist'])
            new_row['year_source'] = 'manual'
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
        chart_location, chart_year = self.look_for_song(row['name'].split(" - ")[0])
        if chart_year > 0:
            new_row['year'] = chart_year
        new_row['old_chart_position'] = chart_location
        new_row['new_chart_location'] = old_row[0]
        return new_row

    def update_year_in_original_chart(self):
        yearly_positions = []
        for row in self.original_chart.original_decade_df.iterrows():
            chart_location, chart_year = self.look_for_song(row[1]['name'])
            yearly_positions.append(chart_location)
        self.original_chart.original_decade_df['yearly_position'] = yearly_positions
        p = Path('C:/Users/tomha/PycharmProjects/GlglzPredictor/DFs/')
        new_table_name = input("Please insert the new original chart table name")
        self.original_chart.original_decade_df.to_csv(Path(p, new_table_name + '.csv'), index=None, header=True)

    def read_chart_file(self):
        songs = []
        type = input("Do you have a .csv file of the yearly charts?")
        if type == 'y' or type == 'Y' or type == 'yes':
            yearly_csv = pd.read_csv('DFs/' +self.decade+".csv")
            for song_in_csv in yearly_csv.iterrows():
                song = {}
                song['name'] = song_in_csv[1]['Artist']+ " - "+song_in_csv[1]['Song']
                song['location'] = song_in_csv[1]['Location']
                song['year'] = song_in_csv[1]['Year']
                songs.append(song)
        else:
            year = 0
            file_name = "DFs/" + self.decade + ".txt"
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
        print("Yearly charts are ready!")
        return songs



print("Welcome to Glglz decade charts table creator!")
decade_chart = decade_table()


