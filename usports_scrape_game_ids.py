
# Import required libraries
import pandas as pd
import bs4 as bs
import urllib.request
from datetime import date


def get_tables(url):

    source = urllib.request.urlopen(url).read()
    soup = bs.BeautifulSoup(source,'lxml')
    all_tables = soup.find_all('table')

    return all_tables

def scrape_game_ids(team, year):
    # TODO replace this with a proper function header (everything must be well documented!!!)
    # Team format: 
    # Year format: 2022-23
    
    url = "https://usportshoops.ca/history/teamseason.php?Gender=MBB&Season=" + year + "&Team=" + team
    
    table = get_tables(url) # scrape table

    ## Extract info and stats from web page
    # TODO these static numbers should instead be replaced by some sort of element check, so it works for any year (currently only works for previous years)
    game_soup = bs.BeautifulSoup(str(table[7]), features="lxml") # Player info

    links = game_soup.find_all("a")

    ids = [str(link)[(str(link).find("Gameid=") + 7):(str(link).find(">Stats") - 1)] for link in links] # TODO maybe improve the readability on this...
    
    return ids


if __name__ == "__main__":

    # Test using last years queens stats
    print(scrape_game_ids("Queens", "2022-23"))

