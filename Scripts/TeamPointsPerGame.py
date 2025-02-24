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

    processedStats = GetPlayerFantasyPoints(df)  # Process fantasy points
    playerStats.append(processedStats)
    
    teamPointsForPerGame.append(TeamPointsForPerRound(processedStats))
    teamPointsAgainstPerGame.append(TeamPointsAgainstPerGame(processedStats))
    teamPointsPerGamePerVenue.append(TeamPointsPerGamePerVenue(processedStats))

    print(f"\n teamPointsForPerGame: ")
    print(f"\n {teamPointsForPerGame[i]}")

print(f"\nteamPointsForPerGame.index")
teamNames = teamPointsForPerGame[0].index.sort_values()
print(f"\n{teamNames}")

averageTeamPointsPerYear = pd.DataFrame(index=teamNames)

averageTeamPointsPerYear["2022"] = teamPointsForPerGame[0]["Avg_PFPG"]
averageTeamPointsPerYear["2023"] = teamPointsForPerGame[1]["Avg_PFPG"]
averageTeamPointsPerYear["2024"] = teamPointsForPerGame[2]["Avg_PFPG"]

weightedAverages = []
avgDifferentials = []
for team in averageTeamPointsPerYear.index : 
    weightedAverage = WeightedAverageOfValues(averageTeamPointsPerYear.loc[team]).__round__(2)
    weightedAverages.append(weightedAverage)
    avg2024 = averageTeamPointsPerYear.loc[team][2]
    
    print(f"\n team {team} avg2024 {avg2024}")

    avgDifferentials.append(AverageDifferential(avg2024, weightedAverage))

averageTeamPointsPerYear["wAVG"] = weightedAverages
averageTeamPointsPerYear["Diff"] = avgDifferentials
averageTeamPointsPerYear = averageTeamPointsPerYear.sort_values("Diff", ascending=False)
print(f"\n{averageTeamPointsPerYear}")

# # Initialize empty DataFrame for final results
# FinalTeamPFPA_2024 = pd.DataFrame()


# # Loop through teams, get differentials per team and concat results
# for team in playerStatsRaw[2]["team.name"].drop_duplicates().sort_values() : 
#     team_df = AverageDifferentialsPerTeam(playerStats[2], team, teamPointsForPerGame[2], teamPointsAgainstPerGame[2], teamPointsPerGamePerVenue[2])
#     FinalTeamPFPA_2024 = pd.concat([FinalTeamPFPA_2024, team_df])  # Append instead of overwriting


# #save to CSV:
# FinalTeamPFPA_2024.set_index("team.name")
# FinalTeamPFPA_2024.to_csv(filePath + "FinalTeamPFPA_2024.csv", index=True).round(2)