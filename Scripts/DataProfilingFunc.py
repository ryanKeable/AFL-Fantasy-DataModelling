import pandas as pd
import numpy as np
from DataProfilingData import *

def WeightedAverageOfValues(collection : list[float]) -> float:
    numerator = 0
    denominator = 0
    for i, item in enumerate(collection):
        weight = pow(i, 2)
        item *= weight
        numerator += item
        denominator += weight

    return (numerator / denominator)


# Function for weighted average
def WeightedAverageOfValues(collection: pd.Series) -> float:
    weights = range(1, len(collection) + 1)  # Weights: [1, 2, 3] for 3 years
    weighted_sum = sum(collection * weights)  # Multiply values by weights and sum
    total_weight = sum(weights)  # Sum of weights
    return round(weighted_sum / total_weight, 2)  # Compute weighted average


# Function for weighted average with exponential weighting
def ExpWeightedAverageOfValues(collection: pd.Series, base: float = 6) -> float:
    """
    Computes a weighted average where recent values (end of the series) have exponentially higher weights.
    
    Args:
        collection (pd.Series): The series of values.
        base (float): The base for the exponential weighting (default 1.5).
                      Higher values give more weight to recent entries.

    Returns:
        float: The exponentially weighted average.
    """

    #clear out any Nan values
    collection = collection.dropna()

    n = len(collection)
    weights = np.array([base ** i for i in range(n)])  # Exponential weights: [1, base, base^2, ...]
    
    weighted_sum = sum(collection * weights)  # Multiply values by weights and sum
    total_weight = sum(weights)  # Sum of weights
    
    return round(weighted_sum / total_weight, 2)  # Compute weighted average

def ProcessRelevantPlayerFantasyPoints(stats : pd.DataFrame) -> pd.DataFrame:
    # Select relevant columns and filter out finals
    playerData = stats[RelevantDataFields]

    # remove finals 
    playerData = playerData[~playerData["round.name"].str.contains("final", case=False, na=False)]

    # Add opponents to playerData
    playerData["opponent"] = playerData.apply(
        lambda row: row["away.team.name"] if row["home.team.name"] == row["team.name"] else row["home.team.name"], axis=1
    )

    # combine player names
    playerData["playerName"] = playerData["player.player.player.givenName"] + " " + playerData["player.player.player.surname"]
    playerData.drop(columns="player.player.player.givenName", inplace=True)
    playerData.drop(columns="player.player.player.surname", inplace=True)

    return playerData


def SumTeamStatByRound(playerStats: pd.DataFrame, groupFilter: str, stat: str) -> pd.DataFrame :
    
    # Group by groupColumn and round, aggregating relevant stats
    statGroupings = [groupFilter, "round.roundNumber", "Year"]

    aggregatedStats = (
        playerStats.groupby(statGroupings, as_index=False)
        .agg(values=(stat, "sum"))
    )

    # Pivot the table: rows = teams, columns = rounds, values = dreamTeamPoints
    table = aggregatedStats.pivot(
        index=statGroupings[0], columns=["Year", "round.roundNumber"], values="values"
    )

    return table

def SumTeamStatByRoundAgainstOpp(playerStats: pd.DataFrame, filter: str, opponent: str, positionFilter: list[str], isPlayer : bool) -> pd.DataFrame :
    
    
    if isPlayer:
        playerStats = playerStats[playerStats["playerName"] == filter] 
    else :        
        playerStats = playerStats[playerStats["team.name"] == filter] 

    # Filter for opponent
    playerStats = playerStats[playerStats["opponent"] == opponent] 
    
    # Filter for position
    playerStats = playerStats[playerStats["player.player.position"].isin(positionFilter)]

    # Group by groupColumn and round, aggregating relevant stats
    statGroupings = ["team.name", "round.roundNumber", "Year"]

    aggregatedStats = (
        playerStats.groupby(statGroupings, as_index=False)
        .agg(values=("dreamTeamPoints", "sum"))
    )

    # Pivot the table: rows = teams, columns = rounds, values = dreamTeamPoints
    table = aggregatedStats.pivot(
        index=statGroupings[0], columns=["Year", "round.roundNumber"], values="values"
    )

    return table


def StatMeanPerYear(years : list[str], playerStats : pd.DataFrame) -> pd.DataFrame:

    valid_years = [year for year in years if year in playerStats.columns.get_level_values(0)]

    if not valid_years:
        return None

    avgTeamStatsPerYear = pd.DataFrame(columns=years)
    for year in valid_years : 
        avgTeamStatsPerYear[year] = (    
            playerStats.xs(key=year, level=0, axis=1)  # Select only columns for this year
            .mean(axis=1, skipna=True)
            .astype(float)
            .round(2)
        )

    return avgTeamStatsPerYear


def ComputeMeanDiffAndFP(meanStatPerYear: pd.DataFrame, label : str, posFilterDiv: int, reportTrend : bool, weightedAvgBase: float = 6) -> pd.DataFrame :

    statData = pd.DataFrame()
    
    if posFilterDiv > 0 :
        meanStatPerYear = meanStatPerYear / posFilterDiv

    rawMean = meanStatPerYear.mean(axis=1, skipna=True).round(3)
        
    # Compute weighted mean
    statData[f"{label} W Mean"] = meanStatPerYear.apply(ExpWeightedAverageOfValues, axis=1, args=(weightedAvgBase,))
    
    leagueAverage = statData[f"{label} W Mean"].mean(axis=0).round(3)

    # Compute trend and differential
    statData[f"{label} Trend"] = AverageDifferentialBasis(statData[f"{label} W Mean"], rawMean)
    
    if label in PureFantasyPointWeightsLUT.keys() :
        statData[f"{label} FP"] = (statData[f"{label} W Mean"] * PureFantasyPointWeightsLUT[label]).round(2)
    
    statData[f"{label} Scalar"] = AverageDifferentialBasis(statData[f"{label} W Mean"], leagueAverage)
    
    # Add league average row with a custom index
    statData.loc["League Average"] = {
        f"{label} W Mean": leagueAverage,
        f"{label} Trend": 0.0,
        f"{label} Scalar": 0.0
    }

    if reportTrend is False :
        statData.drop(columns=[f"{label} Trend"], inplace=True)    



    return statData
    

def GenerateStatMeansAndDiff(years : list[str], stats : pd.DataFrame, posFilterDiv : int, label : str = "", reportTrend : bool = False, weightedAvgBase: float = 6) -> pd.DataFrame:

    statMeanPerYear = StatMeanPerYear(years, stats[:])

    if statMeanPerYear is None :
        return None
    
    meansAndDiffs = ComputeMeanDiffAndFP(statMeanPerYear, label, posFilterDiv, reportTrend, weightedAvgBase)

    return meansAndDiffs


def ComputeUncontestedMarks(rawPlayerStats : pd.DataFrame, years : list[str], filter: str, posFilterDiv, accumulationMethod) -> pd.DataFrame:
    '''Computes Uncontested Marks profile'''

    totalMarksPerYear = accumulationMethod(rawPlayerStats, filter, "marks")
    totalContestedMarksPerYear = accumulationMethod(rawPlayerStats, filter, "contestedMarks")
    totalUncontestedMarksPerYear = totalMarksPerYear - totalContestedMarksPerYear

    statProfile = GenerateStatMeansAndDiff(years, totalUncontestedMarksPerYear, posFilterDiv, label="uncontestedMarks")

    return statProfile


def GetLabel(statLabel : str) -> str:
    abv = StatAbV.get(statLabel)
    label = statLabel
    
    if abv is not None:
        label = abv
    
    return label


def StatDifferentials(title : str, rawPlayerStats : pd.DataFrame, relevantStats: list[str], filter: str, positionFilter: list[str] = None, meanOfPos : bool = False) -> pd.DataFrame:

    # Get unique years from the data
    years = sorted(rawPlayerStats["Year"].unique())

    #filter for early injuries
    rawPlayerStats = rawPlayerStats[rawPlayerStats["timeOnGroundPercentage"] >= 0.25] 

    #filter for extreme lows
    rawPlayerStats = rawPlayerStats[rawPlayerStats["dreamTeamPoints"] >= 30] 
    
    # filter by positions
    if positionFilter is not None :
        rawPlayerStats = rawPlayerStats[rawPlayerStats["player.player.position"].isin(positionFilter)]

    posFilterDiv = 0
    if meanOfPos :
        posFilterDiv = len(positionFilter)


    # Create list to store DataFrames 
    statProfileTables = []  
    
    for stat in relevantStats:
        if stat == "uncontestedMarks" :
            statProfileTables.append(ComputeUncontestedMarks(rawPlayerStats, years, filter, posFilterDiv, SumTeamStatByRound))
        else :
            aggStatsFor = SumTeamStatByRound(rawPlayerStats, filter, stat)
            statProfile = GenerateStatMeansAndDiff(years, aggStatsFor, posFilterDiv, label=stat)
            statProfileTables.append(statProfile)

    # compute expected stat avg based on stat modelling
    fantasyPointsPerGame = SumTeamStatByRound(rawPlayerStats, filter, "dreamTeamPoints")
    fantasyStatProfile = GenerateStatMeansAndDiff(years, fantasyPointsPerGame, posFilterDiv, label="dreamTeamPoints", reportTrend=True)
    statProfileTables.append(fantasyStatProfile)


    # Now concatenate all DataFrames in the list
    combinedStatProfiles = pd.concat(statProfileTables, axis=1)

    averageFantasyPointsAvg = sum(CalcFantasyPointsFromMeansWithLUT(combinedStatProfiles).values())

    combinedStatProfiles["dreamTeamPoints FP"] = averageFantasyPointsAvg.round(2)

    # ReOrderColumns(combinedStatProfiles, "dreamTeamPoints FP", 1)
        
    combinedStatProfiles.title = title
    
    return combinedStatProfiles



def AverageDifferentialBasis(sample : float, avg : float) -> float: 
    diff = (-1 * (1 - (sample / avg)) * 100).round(2) 
    return diff


def InvertAverageDifferentialBasis(value : float) -> float: 
    output = value/100
    output += 1
    return output

def AverageDifferentialPercentage(sample : float, avg : float) -> float: 
    diff = (sample / avg).round(2) 
    return diff

def DPrint(value, label : str = None) :
    if label is not None :
        print(f"\n {label.upper()}")
    print(f"\n{value}")


def ReOrderColumns(dataSet : pd.DataFrame, columnName : str, order : int = 0) -> pd.DataFrame :
    # Reorder columns
    order = max(order, 0)

    if order > len(dataSet):
        DPrint(f"index {order} is greater than the amount of columns in the dataset, cannot reorder dataset")
        return dataSet
    
    column = dataSet[columnName]
    dataSet.drop(columnName, axis=1, inplace=True)
    dataSet.insert(order, columnName, column)


def CalcFantasyPointsFromMeansWithLUT(dataset: pd.DataFrame) -> dict[str, pd.Series] :
        #compare means
    # Identify columns that contain 'Mean'
    # no we want to scale our player's mean based off the teams differentials
    mean_cols = [col for col in dataset.columns if "W Mean" in col]
    
    # Extract relevant rows
    statMeans = dataset[mean_cols]
    
    # Strip " W Mean" from playerStatMeans index
    statMeans.columns = statMeans.columns.str.replace(" W Mean", "")
    # Compute expected fantasy points per stat
    calcFantasyPoints = {
        stat: statMeans[stat] * PureFantasyPointWeightsLUT[stat]
        for stat in PureFantasyPointWeightsLUT.keys() if stat in statMeans
    }

    return calcFantasyPoints