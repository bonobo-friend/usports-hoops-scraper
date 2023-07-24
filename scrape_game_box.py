
# Import required libraries
import pandas as pd
import numpy as np
import bs4 as bs
import urllib.request
from datetime import date

def get_tables(url):

    source = urllib.request.urlopen(url).read()
    soup = bs.BeautifulSoup(source,'lxml')
    all_tables = soup.find_all('table')

    return all_tables

def split_table(data):
    # Gets combined table data and returns the two teams in the same format
    # TODO this whole function could probably be refactored more effectively
    
    data = pd.DataFrame(data)
    
    split_index = (data[0].str.contains("Totals")==True).idxmax() # Find first occurence of "Totals" which signifies the split between the two tables
    
    team1 = data.iloc[:split_index]
    team2 = data.iloc[split_index:]

    team2.drop(team2.tail(2).index, inplace=True)
    team2.drop(team2.head(2).index, inplace=True)

    return team1, team2

def clean_team(team):
    
    team_name = team1.iloc[0, 0][:team1.iloc[0, 0].rfind(" ")] # Get team name, need to remove score
    team.drop(index=0, inplace=True) # Get rid of row once done
    
    # Replace header with first row
    team1.columns = team1.iloc[0]
    team1 = team1[1:]
    team1 = team1.loc[:, team1.columns!="|"] # Drop styling rows
    team1.columns = ['Number', 'Player', 'drop1', 'Mins', '3 Pt', 'drop2', 'Field Goals', 'drop2', 'Free throws', 'drop3',
                     'ORB', 'DRB', 'TRB', 'PF', 'A', 'TO', 'Blk', 'Stl', 'Pts']
    
    team1 = team1[team1.columns.drop(list(team1.filter(regex="drop*")))] # Drop columns specificed to be dropped
    
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

def scrape_game(game_id, year, output):
    # TODO replace this with a proper function header (everything must be well documented!!!)
    # game_id: 
    # year: 
    # output format: "print"/"csv"/"dataframe" #TODO add more output options (potentially dataframes, json, etc.)
    
    url = "https://usportshoops.ca/history/show-game-report.php?Gender=MBB&Season=" + year + "&Gameid=" + game_id

    table = get_tables(url) # scrape table
    ## Extract info and stats from web page
    # TODO these static numbers should instead be replaced by some sort of element check, so it works for any year (currently only works for previous years)
    stats_table = pd.read_html(str(table[5]))[0] # Player Stats 
    # winloss = pd.read_html(str(table[5]))[0] # Win/Loss Record # TODO must double check this is right (not being used atm so no rush)
    print(stats_table)

    data_preprocess = preprocess(stats_table) # Preprocess Data
    
    team_data_final = feature_extraction(data_preprocess) # Feature extraction


    # Output
    if output == "prints":
        print(team_data_final)
    elif output == "csv":
        #team_data_final.to_csv(team + "-" + str(date.today()) + ".csv")
        print

if __name__ == "__main__":

    # Test using last years queens stats
    scrape_game("M20221103QUELAU", "2022-23", "print")

