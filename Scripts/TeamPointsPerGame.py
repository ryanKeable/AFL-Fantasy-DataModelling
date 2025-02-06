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
# Mask invalid values
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
# Mask invalid values
d_teamPointsAgainstPerGame = teamPointsAgainstPerGame.replace(0.0, "BYE").sort_values(by='Avg_PAPG', ascending=False)


print("")
print("teamPointsAgainstPerGame: ")
print("")
print(d_teamPointsAgainstPerGame)


# //
# 
# GET AVERAGE PFPG (Points For Per Game) PER VENUE
# 
# //



# Compute mean DreamTeamPoints per game per venue (instead of sum)
teamPointsPerGamePerVenue = (
    stats_data.groupby(["team.name", "venue.name", "round.roundNumber"], as_index=False)
    .agg(dreamTeamPoints=("dreamTeamPoints", "sum"))  # Mean per game, not sum
)

# Calculate the mean DreamTeamPoints per venue
teamPointsPerGamePerVenue = teamPointsPerGamePerVenue.groupby("venue.name")["dreamTeamPoints"].mean().round(2)

print("")
print("teamPointsPerGamePerVenue:")
print(teamPointsPerGamePerVenue)
print("")


# //
# 
# TEST CASE OF DIFFERENTIALS FOR ADELAIDE:
# 
# //


def AverageDifferentialsPerTeam(teamName) :
    gamesForTeam = pd.DataFrame(stats_data[stats_data["team.name"] == teamName])
    gamesForTeam = gamesForTeam.drop_duplicates(subset=["round.roundNumber", "team.name"])

    # Select relevant columns
    gamesForTeam = gamesForTeam.set_index("round.roundNumber")
    gamesForTeam = gamesForTeam[["team.name", "opponent", "venue.name"]]

    # Get Adelaide's points for season avg 
    PFPG_AVG = teamPointsForPerGame.loc[teamName]["Avg_PFPG"]
    gamesForTeam["PF_AVG"] = PFPG_AVG

    # Get Adelaide's points for per game
    gamesForTeam["PF"] = teamPointsForPerGame.loc[teamName]
    team_PFPG = gamesForTeam["PF"]

    # Calculate the for points differential (Adelaide's round points - Adelaide's PF season average)
    diffPF = (-1 * (1 - team_PFPG / PFPG_AVG) * 100).astype(float).round(2)  # Exclude "Avg_PPG" from calculation
    gamesForTeam["PF_diff"] = diffPF

    # Get Adelaide's opponents points against season avg
    adelaide_opponent_PFPG_AVG = teamPointsAgainstPerGame["Avg_PAPG"].reindex(gamesForTeam["opponent"])
    adelaide_opponent_PFPG_AVG.index = gamesForTeam.index
    gamesForTeam["Opp_PAPG"] = adelaide_opponent_PFPG_AVG

    # Calculate the for points differential (Adelaide's round points - Opponents's PA season average)
    diffPA = (-1 * (1 - team_PFPG / adelaide_opponent_PFPG_AVG) * 100).astype(float).round(2)  # Exclude "Avg_PPG" from calculation
    gamesForTeam["PA_diff"] = diffPA

    # Get venue averages for each corresponding round
    venueAvgPFPG = teamPointsPerGamePerVenue.reindex(gamesForTeam["venue.name"])

    # Convert to DataFrame and assign the correct index
    venueAvgPFPG = pd.DataFrame(venueAvgPFPG)
    venueAvgPFPG.index = gamesForTeam.index  # Set index to round.roundNumber

    diffPV = (-1 * (1 - team_PFPG / venueAvgPFPG["dreamTeamPoints"]) * 100).astype(float).round(2)  # Exclude "Avg_PPG" from calculation
    gamesForTeam["Venue_AVG"] = venueAvgPFPG["dreamTeamPoints"]
    gamesForTeam["PPV_diff"] = diffPV

    print("")
    print("TEAM: " + teamName)
    print(gamesForTeam)
    print("")

    return gamesForTeam
# Initialize empty DataFrame for final results
FinalTeamPFPA = pd.DataFrame()

# Loop through teams and append results
for team in stats_data["team.name"].drop_duplicates().sort_values():
    team_df = AverageDifferentialsPerTeam(team)
    FinalTeamPFPA = pd.concat([FinalTeamPFPA, team_df])  # Append instead of overwriting



#save to CSV:
FinalTeamPFPA.set_index("team.name")
FinalTeamPFPA.to_csv(filePath + "FinalTeamPFPA.csv", index=True)