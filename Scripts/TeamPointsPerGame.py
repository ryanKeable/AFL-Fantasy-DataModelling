import pandas as pd

# Load CSV file
filePath = "/Users/rkeable/Personal/Projects/AFL-Fantasy-DataModelling/Data/"
flieName = "player_stats_data_2024.csv"
stats_data = pd.read_csv(filePath + flieName)

# Select relevant columns and filter out finals
stats_data = stats_data[[
    "round.roundNumber", "round.name", "team.name", "venue.name", "home.team.name", "away.team.name",
    "player.player.player.givenName", "player.player.player.surname", "dreamTeamPoints", "teamStatus"
    ]]

# remove finals 
stats_data = stats_data[~stats_data["round.name"].str.contains("final", case=False, na=False)]

# //
# 
# FUNCTIONS
# 
# //

# Add opponents to stats_data
stats_data["opponent"] = stats_data.apply(
    lambda row: row["away.team.name"] if row["team.name"] in row["home.team.name"]
    else row["home.team.name"] if row["team.name"] in row["away.team.name"]
    else None,
    axis=1
)

# //
# 
# GET AVERAGE PFPG (Points For Per Game) PER TEAM
# 
# //

# Group by team and round, summing the dreamTeamPoints
teamPointsForPerGame = (
    stats_data.groupby(["team.name", "round.roundNumber"], as_index=False)
    .agg(dreamTeamPoints=("dreamTeamPoints", "sum"))
)

# Pivot the table: rows = teams, columns = rounds, values = dreamTeamPoints
teamPointsForPerGame = teamPointsForPerGame.pivot(
    index="team.name", columns="round.roundNumber", values="dreamTeamPoints"
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
# GET AVERAGE PFPG (Points For Per Game) PER VENUE
# 
# //


# Group by team and round, summing the dreamTeamPoint

teamPointsPerGamePerVenue = (
    stats_data.groupby(["team.name", "venue.name"], as_index=False)
    .agg(dreamTeamPoints=("dreamTeamPoints", "sum"))
)

# Pivot the table: rows = teams, columns = rounds, values = dreamTeamPoints
teamPointsPerGamePerVenue = teamPointsPerGamePerVenue.pivot(
    index="team.name", columns="venue.name", values="dreamTeamPoints"
).fillna(0)  # Fill NaNs with 0 for rounds where teams didn't score

teamPointsPerGamePerVenue["Avg_PPG"] = teamPointsPerGamePerVenue.replace(0.0, pd.NA).mean(axis=1, skipna=True).astype(float).round(2)
d_teamPointsPerGamePerVenue = teamPointsPerGamePerVenue.replace(0.0, "BYE").sort_values(by='Avg_PPG', ascending=False)

print(d_teamPointsPerGamePerVenue)

# //
# 
# TEST CASE OF DIFFERENTIALS FOR ADELAIDE:
# 
# //

# Filter to only keep rows where Adelaide played
adelaideGames = stats_data[stats_data["team.name"] == "Adelaide Crows"]
adelaideGames = adelaideGames.drop_duplicates(subset=["round.roundNumber", "team.name"])

# Select relevant columns
adelaideGames = adelaideGames.set_index("round.roundNumber")
adelaideGames = adelaideGames[["team.name", "opponent", "venue.name"]]

# Get Adelaide's points for season avg 
adelaide_PFPG_AVG = teamPointsForPerGame.loc["Adelaide Crows"]["Avg_PFPG"]
adelaideGames["PFPG_AVG"] = adelaide_PFPG_AVG

# Get Adelaide's points per venue


# Get Adelaide's points for per game
adelaideGames["PFPG"] = teamPointsForPerGame.loc["Adelaide Crows"]
adelaide_PFPG = adelaideGames["PFPG"]

# Calculate the for points differential (Adelaide's round points - Adelaide's PF season average)
diffAdelaidePF = (-1 * (1 - adelaide_PFPG / adelaide_PFPG_AVG) * 100).astype(float).round(2)  # Exclude "Avg_PPG" from calculation
adelaideGames["PFPG_diff"] = diffAdelaidePF

# Get Adelaide's opponents points against season avg
adelaide_opponent_PFPG_AVG = teamPointsAgainstPerGame["Avg_PAPG"].reindex(adelaideGames["opponent"])
adelaide_opponent_PFPG_AVG.index = adelaideGames.index
adelaideGames["Opp_PAPG"] = adelaide_opponent_PFPG_AVG

# Calculate the for points differential (Adelaide's round points - Opponents's PA season average)
diffAdelaidePA = (-1 * (1 - adelaide_PFPG / adelaide_opponent_PFPG_AVG) * 100).astype(float).round(2)  # Exclude "Avg_PPG" from calculation
adelaideGames["PAPG_diff"] = diffAdelaidePA

print("")
print(adelaideGames)

#save to CSV:
adelaideGames = adelaideGames.drop(columns=["team.name"])
adelaideGames.to_csv(filePath + "Adelaide_PFPA_Diff.csv", index=True)