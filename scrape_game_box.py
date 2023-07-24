
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
    
    team = pd.DataFrame(team)
    team.reset_index(drop=True, inplace=True)

    # team_name = team.iloc[0, 0][:team.iloc[0, 0].rfind(" ")] # Get team name, need to remove score
    team.drop(index=[0, 1], inplace=True) # Get rid of row once done
    
    # Replace header with first row
    team.columns = team.iloc[0]
    team = team.loc[1:]
    team = team.loc[:, team.columns!="|"] # Drop styling rows
    team.columns = ['Number', 'Player', 'drop1', 'Mins', '3 Pt', 'drop2', 'Field Goals', 'drop2', 'Free Throws', 'drop3',
                     'ORB', 'DRB', 'TRB', 'PF', 'A', 'To', 'Bl', 'St', 'Pts'] # Rename to naming convention in use
    
    team = team[team.columns.drop(list(team.filter(regex="drop*")))] # Drop columns specificed to be dropped
    
    def split_on_dash(col):
        return team[col].str.split("-", expand=True)

    # Split columns into two stats
    team[["3PM", "3PA"]] = split_on_dash("3 Pt")
    team[["FGM", "FGA"]] = split_on_dash("Field Goals")
    team[["FTM", "FTA"]] = split_on_dash("Free Throws")
    
    # Rename columns
    # team.rename(columns={"3 Pt.1" : "3P%", "Field Goals.1" : "FG%", "Free Throws.1" : "FT%", "Rebounds.1" : "TRB"}, inplace=True)

    # Fix datatypes
    team[['Mins', 'ORB', 'DRB', 'TRB', 'PF', 'A', 'To', 'Bl', 'St', 'Pts', '3PM', '3PA', 'FGM','FGA', 'FTM', 'FTA']] \
        = team[['Mins', 'ORB', 'DRB', 'TRB', 'PF', 'A', 'To', 'Bl', 'St', 'Pts', '3PM', '3PA', 'FGM','FGA', 'FTM', 'FTA']].astype("float64")
     
    # Create and shooting percentages
    for stat in ["3P%", "FG%", "FT%"]:
        team[stat] = team[stat[:-1] + "M"] / team[stat[:-1] + "A"]
        team.fillna(0, inplace=True)
    
    # Drop columns
    team.drop(["3 Pt", "Field Goals", "Free Throws"], axis=1, inplace=True)

    return team

def feature_extraction(df):
    
    # Calculate 2pt stats
    df["2PA"] = df["FGA"] - df["3PA"]
    df["2PM"] = df["FGM"] - df["3PM"]
    df["2P%"] = df["2PM"] / df["2PA"]

    # Calculate true shooting
    df["TS%"] = df["Pts"]/(2*(df["FGA"] + (0.44 * df["FTA"])))
    df.fillna(0, inplace=True) # Just in case a null value is created

    # Calculate box efficiency
    # Don't think this is useful
    # df["EFF"] = (df["Pts"] + df["TRB"] + df["A"] + df["St"] + df["Bl"] - (df["FGA"] - df["FGM"]) - (df["FTA"] - df["FGM"]) - df["To"]) / df["GP"]

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

    team1, team2 = split_table(stats_table) # Preprocess Data
    
    team1_clean = clean_team(team1)
    team2_clean = clean_team(team2)
    print(team1_clean.columns)
    team1_extracted = feature_extraction(team1_clean) # Feature extraction
    print(team1_extracted)

    # Output
    if output == "prints":
        print()
    elif output == "csv":
        #team_data_final.to_csv(team + "-" + str(date.today()) + ".csv")
        print

if __name__ == "__main__":

    # Test using last years queens stats
    scrape_game("M20221103QUELAU", "2022-23", "print")
