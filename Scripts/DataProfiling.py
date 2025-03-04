import pandas as pd
import os
import glob
from DataProfilingFunc import *
from DataProfilingData import *

importFilePath = "/Users/rkeable/Personal/Projects/AFL-Fantasy-DataModelling/Data/Import/"
exportFilePath = "/Users/rkeable/Personal/Projects/AFL-Fantasy-DataModelling/Data/Export/"
playerStatsFlieName = "playerStats_22_to_24_AFL.csv"
fixtureFlieName = "Fixture_data_2025.csv"

def CleanPreviousExports():
    # Get all files in the folder
    files = glob.glob(os.path.join(exportFilePath, "*"))

    # Delete each file
    for file in files:
        if os.path.isfile(file):  # Ensure it's a file
            os.remove(file)

def Get2025Fixture() -> pd.DataFrame:
    fixture = pd.read_csv(importFilePath + fixtureFlieName)
    return fixture

# Process player stats
def ProcessPlayerStats() -> pd.DataFrame:
    rawStats = pd.read_csv(importFilePath + playerStatsFlieName)
    processedStats = ProcessRelevantPlayerFantasyPoints(rawStats)
    return processedStats



def WriteTablesToCSV(dataSets : list[pd.DataFrame]) :
    
    for table in dataSets :
        fileName = table.title

        # clear mean noise    
        table = table.drop(columns=[col for col in table.columns if "mean" in col.lower()])
        if "League Average" in table.index : 
            table = table.drop(index="League Average")        
        
        print(f"\n{fileName}")
        print(f"\n{table}")
        
        table.to_csv(exportFilePath + f"{fileName}.csv", index=True)

    

def GenerateTeamProfiles(processedStats) -> pd.DataFrame:

    generalTeamStatsFor = TeamStatDifferentials("GeneralTeamStatsFor", processedStats[:], RelevantTeamStats, True)
    generalTeamStatsAgainst = TeamStatDifferentials("GeneralTeamStatsAgainst", processedStats[:], RelevantTeamStats, True)
    
    WriteTablesToCSV([generalTeamStatsFor, generalTeamStatsAgainst])



def GenerateRuckProfiles(processedStats : pd.DataFrame, fixture : pd.DataFrame) -> pd.DataFrame:

    statsToProfile = RelevantTeamStats + RelevantRuckStats
    ruckStatsFor = TeamStatDifferentials("RuckStatsFor", processedStats[:], statsToProfile, True, RuckPositionTitle)
    ruckStatsAgainst = TeamStatDifferentials("RuckStatsAgainst", processedStats[:], statsToProfile, False, RuckPositionTitle)
    
    ruckStatsForLeagueAvg = ruckStatsFor.loc[["League Average"]].copy()
    Xerri = PlayerStatDifferentials(processedStats, ruckStatsForLeagueAvg, "Tristan Xerri", statsToProfile)

    roundOneFixture = fixture[fixture["round.name"] == "Round 1"]
    
    # Get Xerri's team name
    xerriTeam = Xerri["team.name"].iloc[0]

    # Find the fixture where North Melbourne is playing
    xerriFixture = roundOneFixture[
        (roundOneFixture["home.team.name"] == xerriTeam) | (roundOneFixture["away.team.name"] == xerriTeam)
    ]

    # Determine the opponent
    xerriFixture["opponent"] = xerriFixture.apply(
        lambda row: row["away.team.name"] if row["home.team.name"] == xerriTeam else row["home.team.name"], axis=1
    )
    
    Xerri.drop("team.name", axis=1, inplace=True)
    DPrint(Xerri)
    
    opponentProfile = ruckStatsAgainst[ruckStatsAgainst.index == xerriFixture["opponent"].iloc[0]]
    opponentProfile.title = "Western Bulldogs"
    DPrint(opponentProfile)

    Xerri.loc[xerriFixture["opponent"].iloc[0]] = opponentProfile
    

    WriteTablesToCSV([Xerri, opponentProfile])



CleanPreviousExports()
processedStats = ProcessPlayerStats()
fixture = Get2025Fixture()

# GenerateTeamProfiles(processedStats)
GenerateRuckProfiles(processedStats, fixture)




    # teamStatsAgainst = TeamStatDifferentials(processedStats[:], RelevantTeamStats, False, calcGoalAccuracy=True)
    # teamStatsAgainst.to_csv(filePath + "teamStatsAgainst.csv", index=True)
    
    # backStatsFor = TeamStatDifferentials(processedStats[:], RelevantHalfbackStats, True, BackPositionTitles)
    # backStatsFor.to_csv(filePath + "backStatsFor.csv", index=True)
    
    # backStatsAgainst = TeamStatDifferentials(processedStats[:], RelevantHalfbackStats, False, BackPositionTitles)
    # backStatsAgainst.to_csv(filePath + "backStatsAgainst.csv", index=True)

    # midStatsFor = TeamStatDifferentials(processedStats[:], RelevantMidfieldStats, True, MidfieldPositionTitles)
    # midStatsFor.to_csv(filePath + "midStatsFor.csv", index=True)

    # midStatsAgainst = TeamStatDifferentials(processedStats[:], RelevantMidfieldStats, False, MidfieldPositionTitles)
    # midStatsAgainst.to_csv(filePath + "midStatsAgainst.csv", index=True)
    
    # transitionStatsFor = TeamStatDifferentials(processedStats[:], RelevantTransitionStats, True, TransitionPositionTitles)
    # transitionStatsFor.to_csv(filePath + "transitionStatsFor.csv", index=True)

    # transitionStatsAgainst = TeamStatDifferentials(processedStats[:], RelevantTransitionStats, False, TransitionPositionTitles)
    # transitionStatsAgainst.to_csv(filePath + "transitionStatsAgainst.csv", index=True)

