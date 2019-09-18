import pandas as pd
import wikipedia
from similarity.levenshtein import Levenshtein
from bs4 import BeautifulSoup
from mwviews.api import PageviewsClient
from pathlib import Path

levenshtein = Levenshtein()
pvc = PageviewsClient("Looking for songs")

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

def scrape_info_from_wiki(page):
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
            pop_dict = pvc.article_views('en.wikipedia', [page], granularity='monthly', start='20190101', end='20190731')
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

def get_song_from_wikipedia(song_name):
    song = {}
    results = wikipedia.search(song_name)
    found = 0
    for result in results:
        if levenshtein.distance(result.split("(")[0], song_name.split("-")[0]) <= 5 and found == 0:
            song = scrape_info_from_wiki(result)
            found = 1
    if found == 0:
        print("Name: " + song_name)
        print("Available Results: " + str(results))
        selection = int(input("Select the right result"))
        if selection in range(0,len(results)):
            song = scrape_info_from_wiki(results[selection])
        else:
            song = {
                'result': 'None',
                'year': 0,
                'genres': [],
                'views': 0
            }
    return song

def create_table():
    spotify_table_name = "DFs/spotify_" + decade + ".csv"
    data_from_spotify = pd.read_csv(spotify_table_name)
    wiki_songs = []
    for row in data_from_spotify.iterrows():
        name = row[1]['name'].split("-")[0].replace('remastered', '')+" - "+row[1]['artist']
        song = get_song_from_wikipedia(name)
        song["spotify_name"] = row[1]['name']
        song["spotify_artist"] = row[1]['artist']
        wiki_songs.append(song)
        if len(wiki_songs) % 100 == 0:
            print("Fetched " + str(len(wiki_songs)) + " songs")
    wiki_df = pd.DataFrame(wiki_songs)
    table_name = "wiki_" + decade
    export_csv = wiki_df.to_csv(Path(p, table_name + '.csv'), index=None,header=True)
    print("Saved table successfully")

p = Path('C:/Users/tomha/PycharmProjects/GlglzPredictor/DFs')
print("Which decade are we working on?")
decade = input()
create_table()
