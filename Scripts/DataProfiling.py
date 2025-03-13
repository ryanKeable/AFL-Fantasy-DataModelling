import pandas as pd
import os
import glob
from DataProfilingFunc import *
from DataProfilingData import *

importFilePath = "/Users/rkeable/Personal/Projects/AFL-Fantasy-DataModelling/Data/Import/"
exportFilePath = "/Users/rkeable/Personal/Projects/AFL-Fantasy-DataModelling/Data/Export/"
playerExportDir = "Players/"
teamExportDir = "Teams"
KeyDefLabel = "KeyDef"
RucksLabel = "Ruck"
MidsLabel = "Mid"
WingsLabel = "Trans"
DefsLabel = "Def"
playersExportDir = "Players"
playerStatsFlieName = "playerStats_22_to_24_AFL.csv"
fixtureFlieName = "Fixture_data_2025.csv"

teamFilter = "team.name"
opponentFilter = "opponent"
playerFilter = "playerName"

def CleanPreviousExports():
    # Get all files in the folder and its subdirectories
    files = glob.glob(os.path.join(exportFilePath, "**"), recursive=True)

    # Delete each file
    for file in files:
        if os.path.isfile(file):  # Ensure it's a file
            os.remove(file)

def Get2025Fixture() -> pd.DataFrame:
    fixture = pd.read_csv(importFilePath + fixtureFlieName)
    fixture.drop("compSeason.name", axis=1, inplace=True)
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

def WriteTablesToCSV(dataSet : pd.DataFrame, subDirs: list[str] = None) :
    
    fileName = dataSet.title    
    filePath = exportFilePath 

    if subDirs is not None : 
        for subDir in subDirs:
            filePath = os.path.join(filePath, subDir)

    if not os.path.exists(filePath) :
        DPrint(f"subDir {subDir} for {filePath} does not exist")
        return
    
    filePath = os.path.join(filePath, fileName+".csv")
    
    DPrint(f"write as {filePath}")

    dataSet.to_csv(filePath, index=True)



def GenerateTeamFixture(aflFixture : pd.DataFrame, teamName : str) -> pd.DataFrame :
        # Find the fixture where playerTeam is playing
    teamFixture = aflFixture[
        (aflFixture["home.team.name"] == teamName) | (aflFixture["away.team.name"] == teamName)
    ].copy()

    # Determine the playerTeam opponents
    teamFixture["opponents"] = teamFixture.apply(
        lambda row: row["away.team.name"] if row["home.team.name"] == teamName else row["home.team.name"], axis=1
    )

    return teamFixture

# We are not using player or team stats for scalars
# we get our profile's means and multiple it by our opoponent's scalars
# then 
def PredictScorePerOpponent(profile : pd.DataFrame, opponentProfile : pd.DataFrame) : 
    
    profileName = profile.index.item()  # get the team name and remove parentheses
    opponentName = opponentProfile.index.item()
    profile = pd.concat([profile, opponentProfile])
    
    profile.title = "Debug Dayne 02"
    WriteTablesToCSV(profile, [DefsLabel])


    DPrint(f"comparing {profileName} against {opponentName}")

    #compare means
    # Identify columns that contain 'Mean', "Scalr" or "FP"
    meanCols = [col for col in profile.columns if "Mean" in col]
    scalarCols = [col for col in profile.columns if "Scalar" in col]
    fpCols = [col for col in profile.columns if "FP" in col]

    # Extract relevant rows
    statMeans = profile.loc[profileName, meanCols]
    scalarCols = profile.loc[opponentName, scalarCols]
    calcFP = profile.loc[profileName, fpCols].to_frame()

    # Strip " W Mean" from playerStatMeans index
    statMeans.index = statMeans.index.str.replace(" W Mean", "")
    calcFP.index = calcFP.index.str.replace(" FP", "")
    scalarCols.index = scalarCols.index.str.replace(" Scalar", "")

    # convert scalar back to a percentage multiplier
    opponentStatScalars = InvertAverageDifferentialBasis(scalarCols)

    # Apply the adjustment formula
    adjustedStatMeans = statMeans * opponentStatScalars


    # predict fantasy scores against opponent 
    predictedFantasyPoints = {
        stat: adjustedStatMeans[stat] * PureFantasyPointWeightsLUT[stat]
        for stat in PureFantasyPointWeightsLUT.keys() if stat in adjustedStatMeans
    }

    predictedFantasyPointsAvg = sum(predictedFantasyPoints.values())
    predictedFantasyPoints["dreamTeamPoints"] = predictedFantasyPointsAvg
    
    averageFantasyPointsDF = calcFP.T    

    predictedFantasyPointsDF = pd.DataFrame(predictedFantasyPoints, index=[f"{profileName} PREDICTED"])
    combinedDF = pd.concat([averageFantasyPointsDF, predictedFantasyPointsDF])

    # Compute the Average Differential Basis for each column
    diffs = combinedDF.apply(lambda col: AverageDifferentialBasis(col.iloc[0], col.iloc[1]).round(2))

    # Convert it into a DataFrame with a proper index name
    diffsTable = pd.DataFrame(diffs).T
    diffsTable.index = [opponentName]

    # add the predicted sum
    diffsTable["dreamTeamPoints Predicted Sum"] = predictedFantasyPointsAvg.round(2)


    # Concatenate with the existing DataFrame
    combinedDF = pd.concat([combinedDF, diffsTable])
    
    return diffsTable


def GetAverageAgainstOpponentAsScalar(profile : pd.DataFrame, opponent : str, allStats : pd.DataFrame, positionFilter: list[str], isPlayer : bool) -> tuple[float, float]:
    # compute average against opponent from all player stats 
    # compare against curr profile mean
    profileName = profile.index.item()  # get the team name and remove parentheses
    years = sorted(allStats["Year"].unique())
    
    posFilterDiv = len(positionFilter)
    if isPlayer is True : 
        posFilterDiv = 0
    
    fanstasyPointsPerRound = SumTeamStatByRoundAgainstOpp(allStats, profileName, opponent, positionFilter, isPlayer)
    fantasyStatProfile = GenerateStatMeansAndDiff(years, fanstasyPointsPerRound, posFilterDiv, label="dreamTeamPoints", weightedAvgBase=2)
    
    if fantasyStatProfile is None:
        return 0,0
    
    # clean out unused columns
    fantasyStatProfile.drop(index=["League Average"], inplace=True)
    fantasyStatProfile.drop(["dreamTeamPoints Scalar"], axis=1, inplace=True)
    
    # set opponent name as index label
    fantasyStatProfile["opponent"] = opponent
    fantasyStatProfile.set_index("opponent", inplace=True)  
    
    opponentAvg = fantasyStatProfile["dreamTeamPoints W Mean"].values[0]
    playerAvg = profile["dreamTeamPoints W Mean"].values[0]

    score = AverageDifferentialBasis(opponentAvg, playerAvg)
    return score, opponentAvg


def CompareProfileAgainstOpponents(fixture : pd.DataFrame, profileToCompare : pd.DataFrame, opponentProfiles : pd.DataFrame, allStats : pd.DataFrame, positionFilter: list[str], isPlayer : bool, exportDirs : list[str]) :
    
    profileID = profileToCompare.index.item()

    predictedScores = []
    for opponent in fixture["opponents"] :
        opponentProfile = opponentProfiles[opponentProfiles.index == opponent]
        
        predictedScore = PredictScorePerOpponent(profileToCompare[:], opponentProfile[:])
        averageScoreAgainst = GetAverageAgainstOpponentAsScalar(profileToCompare[:], opponent, allStats, positionFilter, isPlayer)

        predictedScore["L3Avg score"] = averageScoreAgainst[0]
        predictedScore["L3Avg value"] = averageScoreAgainst[1]

        predictedScores.append(predictedScore)
        

    predictedPlayerScoresDF = pd.concat(predictedScores)
    predictedPlayerScoresDF.insert(0, "round.name", fixture["round.name"].values)
    predictedPlayerScoresDF.title = exportDirs[0] + " " + profileID
    
    WriteTablesToCSV(predictedPlayerScoresDF, exportDirs)


def PredictScoresPerRoundPerPlayer(playerNames : list[str], aflFixture : pd.DataFrame, processedPlayerStats : pd.DataFrame, teamStatsAgainst : pd.DataFrame, allStats : pd.DataFrame, positionFilter: list[str], exportDirs : list[str]) : 
    
    for playerName in playerNames :
        DPrint(f"Generating predicted scores scales for {playerName}")

        playerStats = processedPlayerStats[processedPlayerStats.index == playerName] 

        if playerStats is None :
            DPrint(f"Player, {playerName} is not in the list of Player Stats")
            continue

        playerRow = allStats[allStats["playerName"] == playerName].iloc[0]
        playerTeam = playerRow["team.name"]


        # Generate the fixture where playerTeam is playing as a DF
        fixture = GenerateTeamFixture(aflFixture, playerTeam)

        CompareProfileAgainstOpponents(fixture, playerStats, teamStatsAgainst, allStats, positionFilter, True, exportDirs)


def PredictScoresPerRoundPerTeam(aflFixture : pd.DataFrame, teamStatsFor : pd.DataFrame, teamStatsAgainst : pd.DataFrame, allStats : pd.DataFrame, positionFilter: list[str], exportDirs : list[str]) : 
    
    # Remove League Average rows
    teamStatsFor.drop(index=["League Average"], inplace=True)
    teamStatsAgainst.drop(index=["League Average"], inplace=True)

    # iterate through all teams in the teamStatsFor
    for teamName in teamStatsFor.index:
        
        DPrint(f"Generating predicted {exportDirs[0]} scores scalars for {teamName}...")
        
        # get our teams profile in a DF format
        teamProfile = teamStatsFor.loc[teamStatsFor.index == teamName]

        # Generate the fixture where playerTeam is playing as a DF
        fixture = GenerateTeamFixture(aflFixture, teamName)
        
        # compare team to opponents in fixture
        CompareProfileAgainstOpponents(fixture, teamProfile, teamStatsAgainst, allStats, positionFilter, False, exportDirs)


def GenerateProfilesPerRole(label : str, processedStats : pd.DataFrame, fixture : pd.DataFrame, additionalStatsToProfile : list[str], positionsToProfile : list[str], playersToProfile:list[str] = None) -> pd.DataFrame:

    statsToProfile = RelevantTeamStats + additionalStatsToProfile
    
    statsFor = StatDifferentials(label+"StatsFor", processedStats[:], statsToProfile, teamFilter, positionsToProfile, True)    
    statsAgainst = StatDifferentials(label+"StatsAgainst", processedStats[:], statsToProfile, opponentFilter, positionsToProfile, True)
    playerStats = StatDifferentials(label+"PlayerStats", processedStats[:], statsToProfile, playerFilter, positionsToProfile)

    WriteTablesToCSV(statsFor, [label])
    WriteTablesToCSV(statsAgainst, [label])
    WriteTablesToCSV(playerStats, [label])
    
    PredictScoresPerRoundPerTeam(fixture, statsFor[:], statsAgainst[:], processedStats[:], positionsToProfile, [label])
    
    if playersToProfile is not None:
        PredictScoresPerRoundPerPlayer(playersToProfile, fixture, playerStats[:], statsAgainst[:], processedStats[:], positionsToProfile, [label, playerExportDir])


def GenerateTeamProfiles(processedStats) -> pd.DataFrame:

    generalTeamStatsFor = StatDifferentials("GeneralTeamStatsFor", processedStats[:], RelevantTeamStats, teamFilter)
    generalTeamStatsAgainst = StatDifferentials("GeneralTeamStatsAgainst", processedStats[:], RelevantTeamStats, opponentFilter)
    
    WriteTablesToCSV(generalTeamStatsFor)
    WriteTablesToCSV(generalTeamStatsAgainst)


CleanPreviousExports()
processedStats = ProcessPlayerStats()
fixture = Get2025Fixture()

processedStats.title = "processedStats"
WriteTablesToCSV(processedStats)

GenerateTeamProfiles(processedStats)

GenerateProfilesPerRole(MidsLabel, processedStats, fixture, RelevantMidfieldStats, MidsPositionTitles, MidsToProfile)
GenerateProfilesPerRole(DefsLabel, processedStats, fixture, RelevantHalfbackStats, DefsPositionTitles, DefsToProfile)
GenerateProfilesPerRole(RucksLabel, processedStats, fixture, RelevantRuckStats, RuckPositionTitle, RucksToProfile)
GenerateProfilesPerRole(WingsLabel, processedStats, fixture, RelevantTransitionStats, TransitionPositionTitles)
GenerateProfilesPerRole(KeyDefLabel, processedStats, fixture, RelevantHalfbackStats, KeyDefsPositionTitles)

DPrint("done!")






