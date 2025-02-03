import pandas as pd

# Load CSV file
file_path = "/Users/rkeable/Personal/Projects/AFL Data Scraping/RStudio/DataTables/stats_data_2024.csv"
stats_data = pd.read_csv(file_path)

# Select relevant columns and filter out finals
stats_data = stats_data[
    ["round.roundNumber", "round.name", "teamId", "venue.name", "home.team.name", "away.team.name",
     "player.player.player.givenName", "player.player.player.surname", "dreamTeamPoints"]
]
stats_data = stats_data[~stats_data["round.name"].str.contains("final", case=False, na=False)]

# # Map Team Name to Abv
# abv_mapping = {
#     "Adelaide": "ADL",
#     "Brisbane": "BNE",
#     "Carlton": "CAR",
#     "Collingwood": "COL",
#     "Essendon" : "ESS",
#     "Fremantle" :"FRE",
#     "Geelong" : "CAT",
#     "Gold Coast": "GCS",
#     "GWS" : "GWS",
#     "Hawthorn": "HAW",
#     "Melbourne": "MEL",
#     "North": "NTH",
#     "Port Adelaide": "PTA",
#     "Richmond": "RCH",
#     "St Kilda": "STK",
#     "Sydney": "SYD",
#     "Bulldogs": "DOG",
#     "West Coast": "WST"
# }

# //
# 
# GATHER AND MAP TEAM NAMES TO TEAM ID:
# 
# //

# # Replace team IDs with team names
roundOne_data = stats_data[stats_data["round.roundNumber"] == 1]

# # Drop duplicates to ensure one instance per round
roundOne_data = roundOne_data.drop_duplicates(subset=["round.roundNumber", "teamId"])
roundOne_data = roundOne_data[["teamId", "home.team.name", "away.team.name"]]

# Find a team's opponent given a teamID
def find_teamName(row):
    if row.name % 2 == 0:
        return row["teamId"], row["home.team.name"]
    else:
        return row["teamId"], row["away.team.name"]


team_names = roundOne_data.apply(lambda row: find_teamName(row), axis=1)
team_names = team_names.reset_index(drop=True)
team_names_dict = dict(team_names.values.tolist())

# Replace Team ID with mapped Team Name
stats_data["teamId"] = stats_data["teamId"].replace(team_names_dict)

# get total number of Rounds 
roundsPerSeason = len(set(stats_data["round.roundNumber"]))

print("")
print("Rounds per season: ", roundsPerSeason)
print("")


# //
# 
# GET AVERAGE PPG PER TEAM
# 
# //

# Group by team and round, summing the dreamTeamPoints
n_teamPointsPerGame = (
    stats_data.groupby(["teamId", "round.roundNumber"], as_index=False)
    .agg(dreamTeamPoints=("dreamTeamPoints", "sum"))
)

# Pivot the table: rows = teams, columns = rounds, values = dreamTeamPoints
n_teamPointsPerGame = n_teamPointsPerGame.pivot(
    index="teamId", columns="round.roundNumber", values="dreamTeamPoints"
).fillna(0)  # Fill NaNs with 0 for rounds where teams didn't score

# Calculate the average per team, excluding 0.0 values
n_teamPointsPerGame["Avg_PPG"] = n_teamPointsPerGame.replace(0.0, pd.NA).mean(axis=1, skipna=True).astype(float).round(2)

print("")
print(n_teamPointsPerGame)


# //
# 
# TEST CASE OF DIFFERENTIALS FOR ADELAIDE:
# 
# //

# Filter Adelaide's row
Adelaide_PointsPerGame = n_teamPointsPerGame.loc["Adelaide Crows"]

# Compute Adelaide's season average, ignoring 0 values
Adelaide_SeasonAvg = Adelaide_PointsPerGame[:-1]
Adelaide_SeasonAvg = Adelaide_SeasonAvg.replace(0.0, pd.NA).mean(skipna=True)  # Exclude "Avg_PPG" column

# Calculate the differential (Adelaide's round points - Adelaide's season average)
Adelaide_Diff = (-1 * (1 - Adelaide_PointsPerGame[:-1] / Adelaide_SeasonAvg) * 100).astype(float).round(2)  # Exclude "Avg_PPG" from calculation
Adelaide_Diff = Adelaide_Diff.replace(-100.0, "BYE")  # Mask invalid values

# Convert to DataFrame for display
Adelaide_Diff = pd.DataFrame(Adelaide_Diff).T

# Find a team's opponent given a teamID
def find_opponent(row, teamId):
    if row["teamId"] == teamId:
        if "Adelaide Crows" in row["home.team.name"]:
            return row["away.team.name"]
        elif "Adelaide Crows" in row["away.team.name"]:
            return row["home.team.name"]
    return None  # Return None if the teamId doesn't match

# Apply function to find opponents for Adelaide
stats_data["opponent"] = stats_data.apply(lambda row: find_opponent(row, "Adelaide Crows"), axis=1)

# Filter to only keep rows where Adelaide played
adelaide_games = stats_data[stats_data["teamId"] == "Adelaide Crows"]

# Drop duplicates to ensure one instance per round
adelaide_games = adelaide_games.drop_duplicates(subset=["round.roundNumber", "teamId"])

# Select relevant columns
adelaide_games = adelaide_games[["round.roundNumber", "teamId", "opponent"]]
adelaide_games = adelaide_games.rename(columns={"round.roundNumber": "roundNumber"})
adelaide_games = adelaide_games.reset_index(drop=True)

Adelaide_Diff = Adelaide_Diff.reset_index().melt(id_vars=["index"], var_name="roundNumber", value_name="Adelaide_Diff")
Adelaide_Diff = Adelaide_Diff.rename(columns={"index": "teamId"})
Adelaide_Diff = Adelaide_Diff[["teamId", "roundNumber", "Adelaide_Diff"]]

# Merge Adelaide_Diff and adelaide_games on teamId and roundNumber
merged_df = Adelaide_Diff.merge(adelaide_games, on=["teamId", "roundNumber"], how="left")

# Rearrange columns to place 'opponent' after 'teamId'
merged_df = merged_df[["teamId", "opponent", "Adelaide_Diff"]]
merged_df = merged_df.replace(pd.NA, "BYE")  # Mask invalid values

# Display the merged dataframe
print("")
print(merged_df)
print("")

# # Display the result
# print(Adelaide_Diff)
# print(adelaide_games)
# print("adelaide_games Columns:", adelaide_games.columns)
# print("Adelaide_Diff Columns:", Adelaide_Diff.columns)



# # Display the tPPG table
# n_teamPointsPerGame = n_teamPointsPerGame.replace(0.0, "BYE")  # Mask invalid values
# print(n_teamPointsPerGame)

