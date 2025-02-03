import pandas as pd

# Load CSV file
file_path = "/Users/rkeable/Personal/Projects/AFL-Fantasy-DataModelling/Data/player_stats_data_2024.csv"
stats_data = pd.read_csv(file_path)

# Select relevant columns and filter out finals
stats_data = stats_data[
    ["round.roundNumber", "round.name", "teamId", "venue.name", "home.team.name", "away.team.name",
     "player.player.player.givenName", "player.player.player.surname", "dreamTeamPoints"]
]
stats_data = stats_data[~stats_data["round.name"].str.contains("final", case=False, na=False)]

# //
# 
# FUNCTIONS
# 
# //

# Find a team's opponent given a teamID
def find_teamName(row):
    if row.name % 2 == 0:
        return row["teamId"], row["home.team.name"]
    else:
        return row["teamId"], row["away.team.name"]

# Find a team's opponent given a teamID
def find_opponent(row, teamId):
    if row["teamId"] == teamId:
        if row["teamId"] in row["home.team.name"]:
            return row["away.team.name"]
        elif row["teamId"] in row["away.team.name"]:
            return row["home.team.name"]
    return None  # Return None if the teamId doesn't match

# Find a team's opponent given a teamID
def find_opponent_ADL(row, teamId):
    if row["teamId"] == teamId:
        if "Adelaide Crows" in row["home.team.name"]:
            return row["away.team.name"]
        elif "Adelaide Crows" in row["away.team.name"]:
            return row["home.team.name"]
    return None  # Return None if the teamId doesn't match

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

team_names = roundOne_data.apply(lambda row: find_teamName(row), axis=1)
team_names = team_names.reset_index(drop=True)
team_names_dict = dict(team_names.values.tolist())

# Replace Team ID with mapped Team Name
stats_data["teamId"] = stats_data["teamId"].replace(team_names_dict)

# Add opponents to stats_data
stats_data["opponent"] = stats_data.apply(
    lambda row: row["away.team.name"] if row["teamId"] in row["home.team.name"]
    else row["home.team.name"] if row["teamId"] in row["away.team.name"]
    else None,
    axis=1
)

# get total number of Rounds 
roundsPerSeason = len(set(stats_data["round.roundNumber"]))

print("")
print("Rounds per season: ", roundsPerSeason)
print("")

# //
# 
# GET AVERAGE PFPG (Points For Per Game) PER TEAM
# 
# //

# Group by team and round, summing the dreamTeamPoints
teamPointsForPerGame = (
    stats_data.groupby(["teamId", "round.roundNumber"], as_index=False)
    .agg(dreamTeamPoints=("dreamTeamPoints", "sum"))
)

# Pivot the table: rows = teams, columns = rounds, values = dreamTeamPoints
teamPointsForPerGame = teamPointsForPerGame.pivot(
    index="teamId", columns="round.roundNumber", values="dreamTeamPoints"
).fillna(0)  # Fill NaNs with 0 for rounds where teams didn't score

# Calculate the average per team, excluding 0.0 values
teamPointsForPerGame["Avg_PFPG"] = teamPointsForPerGame.replace(0.0, pd.NA).mean(axis=1, skipna=True).astype(float).round(2)
d_teamPointsForPerGame = teamPointsForPerGame.replace(0.0, "BYE").sort_values(by='Avg_PFPG', ascending=False)


print("")
print("teamPointsForPerGame: ")
print("")

print(d_teamPointsForPerGame)


# //
# 
# GET AVERAGE PAPG (Points Against Per Game) PER TEAM
# 
# //

# Group by team and round, summing the dreamTeamPoints
teamPointsAgainstPerGame = (
    stats_data.groupby(["opponent", "round.roundNumber"], as_index=False)
    .agg(dreamTeamPoints=("dreamTeamPoints", "sum"))
)

# Pivot the table: rows = teams, columns = rounds, values = dreamTeamPoints
teamPointsAgainstPerGame = teamPointsAgainstPerGame.pivot(
    index="opponent", columns="round.roundNumber", values="dreamTeamPoints"
).fillna(0)  # Fill NaNs with 0 for rounds where teams didn't score

# Calculate the average per team, excluding 0.0 values
teamPointsAgainstPerGame["Avg_PAPG"] = teamPointsAgainstPerGame.replace(0.0, pd.NA).mean(axis=1, skipna=True).astype(float).round(2)
d_teamPointsAgainstPerGame = teamPointsAgainstPerGame.replace(0.0, "BYE").sort_values(by='Avg_PAPG', ascending=False)
  # Mask invalid values


print("")
print("teamPointsAgainstPerGame: ")
print("")


print(d_teamPointsAgainstPerGame)

# //
# 
# TEST CASE OF DIFFERENTIALS FOR ADELAIDE:
# 
# //

# Get the PF and PA Averages from each table
Adelaide_PFPG = teamPointsForPerGame.loc["Adelaide Crows"]
Adelaide_PAPG = teamPointsAgainstPerGame.loc["Adelaide Crows"]

# Calculate the for points differential (Adelaide's round points - Adelaide's PF season average)
diffAdelaidePF = (-1 * (1 - Adelaide_PFPG[:-1] / Adelaide_PFPG.loc["Avg_PFPG"]) * 100).astype(float).round(2)  # Exclude "Avg_PPG" from calculation
diffAdelaidePF = diffAdelaidePF.replace(-100.0, "BYE")  # Mask invalid values

# Calculate the against points differential (Adelaide's points for per round - Opponents PA season average)
# this is not right as what we need is the differential of for opponent for each round against Adelaide compared to the opponents averagd
# round one we would need GCS diff from their points in round 1 compared to their season avg
diffAdelaidePA = (-1 * (1 - Adelaide_PFPG[:-1] / Adelaide_PAPG.loc["Avg_PAPG"]) * 100).astype(float).round(2)  # Exclude "Avg_PPG" from calculation
diffAdelaidePA = diffAdelaidePA.replace(-100.0, "BYE")  # Mask invalid values

# Convert to DataFrame for display
diffAdelaidePF = pd.DataFrame(diffAdelaidePF).T
diffAdelaidePA = pd.DataFrame(diffAdelaidePA).T

# Filter to only keep rows where Adelaide played
adelaideGames = stats_data[stats_data["teamId"] == "Adelaide Crows"]
adelaideGames = adelaideGames.drop_duplicates(subset=["round.roundNumber", "teamId"])

# Select relevant columns
adelaideGames = adelaideGames[["round.roundNumber", "teamId", "opponent"]]
adelaideGames = adelaideGames.rename(columns={"round.roundNumber": "roundNumber"})
adelaideGames = adelaideGames.reset_index(drop=True)


# perpare diffPF for merge
diffAdelaidePF = diffAdelaidePF.reset_index().melt(id_vars=["index"], var_name="roundNumber", value_name="diffAdelaidePF")
diffAdelaidePF = diffAdelaidePF.rename(columns={"index": "teamId"})
diffAdelaidePF = diffAdelaidePF[["teamId", "roundNumber", "diffAdelaidePF"]]

# perpare diffPA for merge
diffAdelaidePA = diffAdelaidePA.reset_index().melt(id_vars=["index"], var_name="roundNumber", value_name="diffAdelaidePA")
diffAdelaidePA = diffAdelaidePA.rename(columns={"index": "teamId"})
diffAdelaidePA = diffAdelaidePA[["teamId", "roundNumber", "diffAdelaidePA"]]

# Merge diffAdelaidePA and adelaide_games on teamId and roundNumber
merged_df = diffAdelaidePF.merge(adelaideGames, on=["teamId", "roundNumber"], how="left")



# Merge diffAdelaidePA as well 
merged_df = diffAdelaidePA.merge(merged_df, on=["teamId", "roundNumber"], how="left")

# Clean up table display
merged_df = merged_df.replace(pd.NA, "BYE")  # Mask invalid values
column_order = ["teamId", "diffAdelaidePF", "opponent", "diffAdelaidePA"]
merged_df = merged_df[column_order]

# Display the merged dataframe
print("")
print(merged_df)
print("")