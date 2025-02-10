import pandas as pd
from TeamPointsPerGameFunc import *

# Load CSV files
filePath = "/Users/rkeable/Personal/Projects/AFL-Fantasy-DataModelling/Data/"

flieNames = ["player_stats_data_2022.csv", "player_stats_data_2023.csv", "player_stats_data_2024.csv"]
playerStatsRaw = []
playerStats = []
teamPointsForPerGame = []
teamPointsAgainstPerGame = []
teamPointsPerGamePerVenue = []

for i, val in enumerate(flieNames):
    df = pd.read_csv(filePath + flieNames[i])
    playerStatsRaw.append(df)
    playerStats.append(GetPlayerFantasyPoints(playerStatsRaw[i]))
    teamPointsForPerGame.append(TeamPointsForPerGame(playerStats[i]))
    teamPointsAgainstPerGame.append(TeamPointsAgainstPerGame(playerStats[i]))
    teamPointsPerGamePerVenue.append(TeamPointsPerGamePerVenue(playerStats[i]))

print("")
print("teamPointsForPerGame: ")
print("")

print(teamPointsForPerGame[2].replace(0.0, "BYE").sort_values(by='Avg_PFPG', ascending=False))

print("")
print("teamPointsAgainstPerGame: ")
print("")
print(teamPointsAgainstPerGame[2].replace(0.0, "BYE").sort_values(by='Avg_PAPG', ascending=False))

print("")
print("teamPointsPerGamePerVenue:")
print(teamPointsPerGamePerVenue[2])
print("")

# Initialize empty DataFrame for final results
FinalTeamPFPA_2024 = pd.DataFrame()

# Loop through teams and append results
for team in playerStatsRaw[2]["team.name"].drop_duplicates().sort_values():
    team_df = AverageDifferentialsPerTeam(playerStats[2], team, teamPointsForPerGame[2], teamPointsAgainstPerGame[2], teamPointsPerGamePerVenue[2])
    FinalTeamPFPA_2024 = pd.concat([FinalTeamPFPA_2024, team_df])  # Append instead of overwriting


#save to CSV:
FinalTeamPFPA_2024.set_index("team.name")
FinalTeamPFPA_2024.to_csv(filePath + "FinalTeamPFPA_2024.csv", index=True)