import pandas as pd
import os
import glob
from DataProfilingFunc import *
from DataProfilingData import *

importFilePath = "/Users/rkeable/Personal/Projects/AFL-Fantasy-DataModelling/Data/Import/"
exportFilePath = "/Users/rkeable/Personal/Projects/AFL-Fantasy-DataModelling/Data/Export/"
playerStatsFlieName = "playerStats_22_to_24_AFL.csv"
fixtureFlieName = "Fixture_data_2025.csv"

teamFilter = "team.name"
opponentFilter = "opponent"

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

def DropLeageAveragesAndMean(table : pd.DataFrame) :  
    # clear mean noise    
    table = table.drop(columns=[col for col in table.columns if "mean" in col.lower()])
    if "League Average" in table.index : 
        table = table.drop(index="League Average")        
    
    return table

def WriteTablesToCSV(dataSets : list[pd.DataFrame]) :
    
    for table in dataSets :
        fileName = table.title     
        table.to_csv(exportFilePath + f"{fileName}.csv", index=True)


def GenerateTeamProfiles(processedStats) -> pd.DataFrame:

    generalTeamStatsFor = TeamStatDifferentials("GeneralTeamStatsFor", processedStats[:], RelevantTeamStats, teamFilter)
    generalTeamStatsAgainst = TeamStatDifferentials("GeneralTeamStatsAgainst", processedStats[:], RelevantTeamStats, opponentFilter)
    
    WriteTablesToCSV([generalTeamStatsFor, generalTeamStatsAgainst])



def GenerateRuckProfiles(processedStats : pd.DataFrame, fixture : pd.DataFrame) -> pd.DataFrame:

    writeableTables = []
    statsToProfile = RelevantTeamStats + RelevantRuckStats
    
    ruckStatsFor = TeamStatDifferentials("RuckStatsFor", processedStats[:], statsToProfile, teamFilter, RuckPositionTitle)
    writeableTables.append( ruckStatsFor )
    
    ruckStatsAgainst = TeamStatDifferentials("RuckStatsAgainst", processedStats[:], statsToProfile, opponentFilter, RuckPositionTitle)
    writeableTables.append( ruckStatsAgainst )
    
    ruckStatsForLeagueAvg = writeableTables[0].loc[["League Average"]].copy()
    Xerri = PlayerStatDifferentials(processedStats, ruckStatsForLeagueAvg, "Tristan Xerri", statsToProfile)

    roundOneFixture = fixture[fixture["round.name"] == "Round 2"]
    
    # Get Xerri's team name
    xerriTeam = Xerri["team.name"].iloc[0]

    # Find the fixture where North Melbourne is playing
    xerriFixture = roundOneFixture[
        (roundOneFixture["home.team.name"] == xerriTeam) | (roundOneFixture["away.team.name"] == xerriTeam)
    ].copy()

    # Determine the opponent
    xerriFixture["opponent"] = xerriFixture.apply(
        lambda row: row["away.team.name"] if row["home.team.name"] == xerriTeam else row["home.team.name"], axis=1
    )
    
    Xerri.drop("team.name", axis=1, inplace=True)

    opponentProfile = ruckStatsAgainst[ruckStatsAgainst.index == xerriFixture["opponent"].iloc[0]]
    opponentName = xerriFixture["opponent"].iloc[0]
    DPrint(opponentName, "opponentName")

    Xerri = pd.concat([Xerri, opponentProfile.loc[[opponentName]]])
    DPrint(Xerri)

    #compare means
    # Identify columns that contain 'Mean'
    # no we want to scale our player's mean based off the teams differentials
    mean_cols = [col for col in Xerri.columns if "Mean" in col]
    diff_cols = [col for col in Xerri.columns if not "Mean" in col and not "Trend" in col]

    # Extract relevant rows
    playerStatMeans = Xerri.loc["Tristan Xerri", mean_cols]
    
    # Strip " W Mean" from playerStatMeans index
    playerStatMeans.index = playerStatMeans.index.str.replace(" W Mean", "")

    opponentStatScalars = InvertAverageDifferentialBasis(Xerri.loc["Melbourne", diff_cols])

    # Apply the adjustment formula
    # because these have different index names they cannot be multiplied together in this method
    adjusted_xerri = playerStatMeans * opponentStatScalars



    # Remove " W Mean" from column names to match FantasyPointWeightsLUT keys
    adjusted_xerri.index = adjusted_xerri.index.str.replace(" W Mean", "")

    # Filter only the stats that exist in the FantasyPointWeightsLUT
    expectedFantasyPoints = {
        stat: adjusted_xerri[stat] * PureFantasyPointWeightsLUT[stat]
        for stat in PureFantasyPointWeightsLUT.keys() if stat in adjusted_xerri
    }



    fantasy_points_series = pd.Series(expectedFantasyPoints, name="Fantasy Points")
    total_sum = sum(expectedFantasyPoints.values())    # Add the total impact as a separate value
    fantasy_points_series["Total Fantasy Points"] = total_sum
    
    scoreRating = AverageDifferentialBasis(total_sum, playerStatMeans["dreamTeamPoints"])
    output = f"{scoreRating} against {opponentName}"

    # Display the results


    DPrint(expectedFantasyPoints, "expectedFantasyPoints")
    DPrint(fantasy_points_series, "fantasy_points_series")
    DPrint(output, "output")

    # concat generates a new data frame that clears our attribute >.<
    Xerri.title = "Xerri" 
    
    writeableTables.append(Xerri) 

    WriteTablesToCSV(writeableTables)

def GenerateScoresPerRoundForPlayer(playerName : str, fixture : pd.DataFrame, statsToCompare : pd.DataFrame)
    

CleanPreviousExports()
processedStats = ProcessPlayerStats()
fixture = Get2025Fixture()

GenerateTeamProfiles(processedStats)
GenerateRuckProfiles(processedStats, fixture)

DPrint("done!")






