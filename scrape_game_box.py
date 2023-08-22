
# Import required libraries
import pandas as pd
import common_util

def split_table(data: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    # Gets combined table data and returns the two teams in the same format
    # TODO this whole function could probably be refactored more effectively
    
    data = pd.DataFrame(data)

    split_index = (data[0].str.contains("Totals")==True).idxmax() # Find first occurence of "Totals" which signifies the split between the two tables
    
    team1 = data.iloc[:split_index]
    team2 = data.iloc[split_index:]
    
    team2.drop(team2.tail(2).index, inplace=True)
    team2.drop(team2.head(2).index, inplace=True)

    return team1, team2

def clean_team(team: pd.DataFrame) -> pd.DataFrame:
    
    team.reset_index(drop=True, inplace=True)

    team_name_rough = team.iloc[0, 0]
    team_name = team_name_rough[:team_name_rough.rfind(" ")] # Get team name, need to remove score
    team.drop(index=[0, 1], inplace=True) # Get rid of row once done
    
    # Replace header with first row
    team.columns = team.iloc[0]
    team = team.loc[1:]
    team = team.loc[:, team.columns!="|"] # Drop styling rows
    team.columns = ['Number', 'Player', 'drop1', 'Mins', '3 Pt', 'drop2', 'Field Goals', 'drop2', 'Free Throws', 'drop3',
                     'ORB', 'DRB', 'TRB', 'PF', 'A', 'To', 'Bl', 'St', 'Pts'] # Rename to naming convention in use
    
    team = team[team.columns.drop(list(team.filter(regex="drop*")))] # Drop columns specificed to be dropped
    
    team = team[team["Player"].str.contains("team-")==False] # Drop any of the team-{team} rows that appear

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

    # Add team
    team["Team"] = team_name
    
    return team


def scrape_game(game_id : str, year: str, output: str):
    # TODO replace this with a proper function header (everything must be well documented!!!)
    # game_id: 
    # year: 
    # output format: "print"/"csv"/"dataframe" #TODO add more output options (potentially dataframes, json, etc.)
    url = "https://usportshoops.ca/history/show-game-report.php?Gender=MBB&Season=" + year + "&Gameid=" + game_id

    table = common_util.get_tables(url) # scrape table
    ## Extract info and stats from web page
    # TODO these static numbers should instead be replaced by some sort of element check, so it works for any year (currently only works for previous years)
    stats_table = pd.read_html(str(table[5]))[0] # Player Stats 
    date_table = pd.read_html(str(table[3]))[0] # Player Stats 
    
    date = pd.to_datetime(date_table.iloc[0, 1]) # Hardcoded but should work in every case
    
    team1, team2 = split_table(stats_table) # Preprocess Data
    
    # Account for one of the tables potentially being empty

    if not team1.empty and not team2.empty: # Go on without intervention

        team1_clean = clean_team(team1)
        team2_clean = clean_team(team2)
        
        team1_extracted = common_util.feature_extraction(team1_clean, calc_eff=False)
        team2_extracted = common_util.feature_extraction(team2_clean, calc_eff=False)
        
        data = pd.concat([team1_extracted, team2_extracted])
        
    elif team1.empty: # Missing team1

        team2_clean = clean_team(team2)
        
        team2_extracted = common_util.feature_extraction(team2_clean, calc_eff=False)
        
        data = team2_extracted

    elif team2.empty: # Missing team2

        team1_clean = clean_team(team1)
        
        team1_extracted = common_util.feature_extraction(team1_clean, calc_eff=False)
        
        data = team1_extracted

    data["Date"] = date

    # Output
    if output == "dataframe":
        return data
    if output == "print":
        print(data)    
    elif output == "csv":
        data.to_csv(game_id + "-" + year + ".csv")

if __name__ == "__main__":

    # Test using last years queens stats
    scrape_game("M20221103QUELAU", "2022-23", "print")

