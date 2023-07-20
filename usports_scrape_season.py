
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

def preprocess(info, stats):
    print(info)
    print(stats)
    data = (stats.set_index("Player")).join((info.set_index("Player")), how="left")

    # Drop team totals row
    data.drop("* Team Totals", axis=0, inplace=True)

    def split_on_dash(col):
        return data[col].str.split("-", expand=True)

    # Split columns into two stats
    data[["3PM", "3PA"]] = split_on_dash("3 Pt")
    data[["FGM", "FGA"]] = split_on_dash("Field Goals")
    data[["FTM", "FTA"]] = split_on_dash("Free Throws")
    data[["TORB", "TDRB"]] = split_on_dash("Rebounds")

    # Rename columns
    data.rename(columns={"3 Pt.1" : "3P%", "Field Goals.1" : "FG%", "Free Throws.1" : "FT%", "Rebounds.1" : "TRB"}, inplace=True)

    # Adjust shooting percentages to actual percentages
    for stat in ["3P%", "FG%", "FT%"]:
        data[stat] = data[stat]/100

    # Fix datatypes
    data[["3PM", "3PA", "FGM", "FGA", "FTM", "FTA", "TORB", "TDRB"]] = data[["3PM", "3PA", "FGM", "FGA", "FTM", "FTA", "TORB", "TDRB"]].astype("float64")
        
    # Drop columns
    data.drop(["3 Pt", "Field Goals", "Free Throws", "Rebounds", "Hometown", "High School (Prior Team)"], axis=1, inplace=True)

    # Fix NaN weight values
    data["Wt"] = data["Wt"].fillna(-1)

    return data

def feature_extraction(df):
    
    # Calculate 2pt stats
    df["2PA"] = df["FGA"] - df["3PA"]
    df["2PM"] = df["FGM"] - df["3PM"]
    df["2P%"] = df["2PM"] / df["2PA"]

    # Calculate true shooting
    df["TS%"] = df["Pts"]/(2*(df["FGA"] + (0.44 * df["FTA"])))

    # Calculate box efficiency
    df["EFF"] = (df["Pts"] + df["TRB"] + df["A"] + df["St"] + df["Bl"] - (df["FGA"] - df["FGM"]) - (df["FTA"] - df["FGM"]) - df["To"]) / df["GP"]

    return df

def scrape_season(team, year, output, verbose):
    # TODO replace this with a proper function header (everything must be well documented!!!)
    # Team format: 
    # Year format: 2022-23
    # output format: "print"/"csv" #TODO add more output options (potentially dataframes, json, etc.)
    # verbose format: bool
    
    url = "https://usportshoops.ca/history/teamseason.php?Gender=MBB&Season=" + year + "&Team=" + team
    
    if verbose: print(url)

    table = get_tables(url) # scrape table

    if verbose: print(table)

    ## Extract info and stats from web page
    # TODO these static numbers should instead be replaced by some sort of element check
    # These numbers work for previous years data, won't work for current years
    info_table = pd.read_html(str(table[5]))[0] # Player info
    stats_table = pd.read_html(str(table[9]))[0] # Player Stats 
    # winloss = pd.read_html(str(table[5]))[0] # Win/Loss Record # TODO must double check this is right (not being used atm so no rush)

    if verbose:
        print(info_table)
        print(stats_table)

    team_data_preprocess = preprocess(info_table, stats_table) # Preprocess Data

    if verbose: print(team_data_preprocess)
    
    team_data_final = feature_extraction(team_data_preprocess) # Feature extraction

    if verbose: print(team_data_final)

    # Output
    if output == "prints":
        print(team_data_final)
    elif output == "csv":
        team_data_final.to_csv(team + "-" + str(date.today()) + ".csv")
        if verbose: print("Save complete at:", str(team + "-" + str(date.today()) + ".csv"))

if __name__ == "__main__":

    # Test using last years queens stats
    scrape_season("Queens", "2022-23", "print", True)

