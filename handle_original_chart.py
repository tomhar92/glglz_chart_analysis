import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from pathlib import Path
import wikipedia
from similarity.levenshtein import Levenshtein
from bs4 import BeautifulSoup
from mwviews.api import PageviewsClient


class original_table:
    levenshtein = Levenshtein()
    pvc = PageviewsClient("Looking for songs")
    client_credentials_manager = SpotifyClientCredentials(client_id='274d5abed01c455099ac8ad14c6a68e8', client_secret='7425a61db8ed45c48d1ccfaa39842e00')

    def __init__(self, decade):
        self.sp = spotipy.Spotify(client_credentials_manager=self.client_credentials_manager)
        self.decade = decade
        table_name = input("Please insert the original chart table name")
        self.original_decade_df = pd.read_csv("DFs/"+table_name+".csv", encoding="utf-8")
        spoti = input("Add Spotify Features?")
        if spoti == 'Y' or spoti == 'y' or spoti == 'yes':
            self.add_spotify_features()
        wiki = input("Add Wikipedia Features?")
        if wiki == 'Y' or wiki == 'y' or wiki == 'yes':
            self.operate_wikipedia()
        #yearly = input("Find in yearly charts?")
        #if yearly == 'Y' or yearly == 'y' or yearly == 'yes':
        #    self.find_in_yearly_chart()
        p = Path('C:/Users/tomha/PycharmProjects/GlglzPredictor/DFs/')
        new_table_name =input("Please insert the new original chart table name")
        export_csv = self.original_decade_df.to_csv(Path(p, new_table_name + '.csv'), index=None, header=True)
        print("Table saved successfully!")

    def add_spotify_features(self):
        spotify_popularity = []
        spotify_valence = []
        spotify_tempo = []
        spotify_instrumentalness = []
        spotify_year = []
        for row in self.original_decade_df.iterrows():
            try:
                result = self.sp.search(q=row[1]['name'], type='track')['tracks']['items'][0]
                spotify_valence.append(self.sp.audio_features(result['id'])[0]['valence'])
                spotify_tempo.append(self.sp.audio_features(result['id'])[0]['tempo'])
                spotify_instrumentalness.append(self.sp.audio_features(result['id'])[0]['instrumentalness'])
                spotify_popularity.append(result['popularity'])
                spotify_year.append(result['album']['release_date'].split("-")[0])
            except:
                spotify_valence.append('None')
                spotify_tempo.append('None')
                spotify_instrumentalness.append('None')
                spotify_popularity.append('None')
                spotify_year.append('None')
        self.original_decade_df['spotify_popularity'] = spotify_popularity
        self.original_decade_df['spotify_valence'] = spotify_valence
        self.original_decade_df['spotify_tempo'] = spotify_tempo
        self.original_decade_df['spotify_instrumentalness'] = spotify_instrumentalness
        self.original_decade_df['spotify_year'] = spotify_year


    def scrape_info_from_wiki(self, page):
        song = {}
        try:
            page_html = wikipedia.WikipediaPage(page).html()
            prettified = BeautifulSoup(page_html, 'html.parser')
            info_table = prettified.findAll("table", {"class": "infobox"})
            song["result"] = page
            song["year"] = 0
            song["genres"] = []
            song["views"] = 0
            for row in info_table[0].find_all("tr"):
                row_year = row.find(text='Released')
                if row_year:
                    song["year"] = get_year(row)
                row_genres = row.find("td", {"class": "category"})
                if row_genres:
                    for genre in row_genres.find_all("a"):
                        if genre.has_attr("title"):
                            song["genres"].append(genre["title"])
            try:
                pop_dict = self.pvc.article_views('en.wikipedia', [page], granularity='monthly', start='20190101', end='20190731')
                for value in pop_dict.items():
                    for i in value[1]:
                        if value[1][i] != None:
                            song["views"] = song["views"] + value[1][i]
            except:
                print("Can't Sum Up Views!")
        except Exception as e:
            print(e)
            song = {
                'result': 'None',
                'year': 0,
                'genres': [],
                'views': 0
            }
        return song

    def get_song_from_wikipedia(self, song_name):
        song = {}
        results = wikipedia.search(song_name)
        found = 0
        for result in results:
            if self.levenshtein.distance(result.split("(")[0], song_name.split("-")[0]) <= 5 and found == 0:
                song = self.scrape_info_from_wiki(result)
                found = 1
        if found == 0:
            print("Name: " + song_name)
            print("Available Results: " + str(results))
            selection = int(input("Select the right result"))
            if selection in range(0,len(results)):
                song = self.scrape_info_from_wiki(results[selection])
            else:
                song = {
                    'result': 'None',
                    'year': 0,
                    'genres': [],
                    'views': 0
                }
        return song

    def operate_wikipedia(self):
        songs_from_wikipedia = []
        for row in self.original_decade_df.iterrows():
            songs_from_wikipedia.append(self.get_song_from_wikipedia(row[1]['name']))
        songs_from_wikipedia = pd.DataFrame(songs_from_wikipedia)
        self.original_decade_df['wikipedia_year'] = songs_from_wikipedia['year']
        self.original_decade_df['genres'] = songs_from_wikipedia['genres']
        self.original_decade_df['views'] = songs_from_wikipedia['views']

    def read_chart_file(self):
        songs = []
        year = 0
        file_name = "DFs/"+self.decade+".txt"
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

    def find_in_yearly_chart(self):
        yearly_positions = []
        songs_from_charts = self.read_chart_file()
        for row in self.original_decade_df.iterrows():
            found_song = 0
            for song in songs_from_charts:
                if self.levenshtein.distance(song['name'], row[1]['name']) <= 1:
                    yearly_positions.append(song['location'])
                    found_song = 1
            if found_song == 0:
                yearly_positions.append(0)
        self.original_decade_df['yearly_position'] = yearly_positions

    def fix_year(self):
        year = []
        year_source = []
        for row in self.original_decade_df.iterrows():
            if int(row[1]['spotify_year']) > 1979 and int(row[1]['spotify_year']) < 1990:
                year.append(int(row[1]['spotify_year']))
                year_source.append('spotify')
            elif int(row[1]['wikipedia_year']) > 1979 and int(row[1]['wikipedia_year']) < 1990:
                year.append(int(row[1]['wikipedia_year']))
                year_source.append('wikipedia')
            else:
                year.append(int(input(row[1]['name'] + " " + row[1]['artist'])))
                year_source.append('manual')
        self.original_decade_df['year'] = year
        self.original_decade_df['year_source'] = year_source


def cut_year_from_cell(cell):
    try:
        return int(cell.contents[0])
    except:
        try:
            return int(cell.contents[0].split(" ")[1])
        except:
            try:
                return int(cell.contents[0].split(" ")[2])
            except:
                return 0

def get_year(row):
    year = 0
    found = 0
    year_cell = row.find("td", {"class": "plainlist"})
    if year_cell is not None:
        if year_cell.find("li") and found == 0:
            year = cut_year_from_cell(year_cell.find("li"))
            if year != 0:
                print("Taken from List! "+str(year))
                found = 1
            else:
                print ("year_li: "+str(year_cell.find("li")))
        elif year_cell.find("a") and year_cell.find("a").has_attr("title"):
            year = year_cell.find("a")["title"].split(" ")[0]
            print("Taken from Link! "+str(year))
            found = 1
        elif year_cell.find("span", {"class": "dtstart"}):
            try:
                year = int(year_cell.find("span", {"class": "dtstart"}).contents[0].split("-")[0])
                print("Taken from span! " +str(year))
                found = 1
            except:
                print(year_cell)
        elif len(year_cell.contents) > 0:
            year = cut_year_from_cell(year_cell)
            if year != 0:
                found = 1
        if found == 0:
            print("year cell: " + str(year_cell))
    return year