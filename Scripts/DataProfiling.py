import pandas as pd
from DataProfilingFunc import *
from DataProfilingData import *

# Load CSV files
filePath = "/Users/rkeable/Personal/Projects/AFL-Fantasy-DataModelling/Data/"

flieNames = ["player_stats_data_2022.csv", "player_stats_data_2023.csv", "player_stats_data_2024.csv"]
playerStatsFlieName = "PlayerStats_AFL.csv"
playerStatsRaw = []
playerStats = []
teamPointsForPerGame = []
teamPointsAgainstPerGame = []
teamPointsPerGamePerVenue = []

teamStatColumns = ["PointsPerGame", "PointsAgainstPerGame", "PointsPerVenue"]
teamStats = pd.DataFrame(columns=teamStatColumns)

def ReadPlayerStats()  -> pd.DataFrame:
    rawStats = pd.read_csv(filePath + playerStatsFlieName)
    processedStats = ProcessRelevantPlayerFantasyPoints(rawStats)

    teamStatsFor = TeamStatDifferentials(processedStats[:], RelevantTeamStats, True, calcGoalAccuracy=True)
    teamStatsFor.to_csv(filePath + "teamStatsFor.csv", index=True)
    
    teamStatsAgainst = TeamStatDifferentials(processedStats[:], RelevantTeamStats, False, calcGoalAccuracy=True)
    teamStatsAgainst.to_csv(filePath + "teamStatsAgainst.csv", index=True)
    
    backStatsFor = TeamStatDifferentials(processedStats[:], RelevantHalfbackStats, True, BackPositionTitles)
    backStatsFor.to_csv(filePath + "backStatsFor.csv", index=True)
    
    backStatsAgainst = TeamStatDifferentials(processedStats[:], RelevantHalfbackStats, False, BackPositionTitles)
    backStatsAgainst.to_csv(filePath + "backStatsAgainst.csv", index=True)

    midStatsFor = TeamStatDifferentials(processedStats[:], RelevantMidfieldStats, True, MidfieldPositionTitles)
    midStatsFor.to_csv(filePath + "midStatsFor.csv", index=True)

    midStatsAgainst = TeamStatDifferentials(processedStats[:], RelevantMidfieldStats, False, MidfieldPositionTitles)
    midStatsAgainst.to_csv(filePath + "midStatsAgainst.csv", index=True)
    
    transitionStatsFor = TeamStatDifferentials(processedStats[:], RelevantTransitionStats, True, TransitionPositionTitles)
    transitionStatsFor.to_csv(filePath + "transitionStatsFor.csv", index=True)

    transitionStatsAgainst = TeamStatDifferentials(processedStats[:], RelevantTransitionStats, True, TransitionPositionTitles)
    transitionStatsAgainst.to_csv(filePath + "transitionStatsAgainst.csv", index=True)


ReadPlayerStats()



# print(f"\nteamPointsForPerGame.index")
# teamNames = teamPointsForPerGame[0].index.sort_values()
# print(f"\n{teamNames}")

# averageTeamPointsPerYear = pd.DataFrame(index=teamNames)

# averageTeamPointsPerYear["2022"] = teamPointsForPerGame[0]["Avg_PFPG"]
# averageTeamPointsPerYear["2023"] = teamPointsForPerGame[1]["Avg_PFPG"]
# averageTeamPointsPerYear["2024"] = teamPointsForPerGame[2]["Avg_PFPG"]

# weightedAverages = []
# avgDifferentials = []
# for team in averageTeamPointsPerYear.index : 
#     weightedAverage = WeightedAverageOfValues(averageTeamPointsPerYear.loc[team]).__round__(2)
#     weightedAverages.append(weightedAverage)
#     avg2024 = averageTeamPointsPerYear.loc[team][2]
    
#     print(f"\n team {team} avg2024 {avg2024}")

#     avgDifferentials.append(AverageDifferential(avg2024, weightedAverage))

# averageTeamPointsPerYear["wAVG"] = weightedAverages
# averageTeamPointsPerYear["Diff"] = avgDifferentials
# averageTeamPointsPerYear = averageTeamPointsPerYear.sort_values("Diff", ascending=False)
# print(f"\n{averageTeamPointsPerYear}")

# # Initialize empty DataFrame for final results
# FinalTeamPFPA_2024 = pd.DataFrame()


# # Loop through teams, get differentials per team and concat results
# for team in playerStatsRaw[2]["team.name"].drop_duplicates().sort_values() : 
#     team_df = AverageDifferentialsPerTeam(playerStats[2], team, teamPointsForPerGame[2], teamPointsAgainstPerGame[2], teamPointsPerGamePerVenue[2])
#     FinalTeamPFPA_2024 = pd.concat([FinalTeamPFPA_2024, team_df])  # Append instead of overwriting


# #save to CSV:
# FinalTeamPFPA_2024.set_index("team.name")
# FinalTeamPFPA_2024.to_csv(filePath + "FinalTeamPFPA_2024.csv", index=True).round(2)