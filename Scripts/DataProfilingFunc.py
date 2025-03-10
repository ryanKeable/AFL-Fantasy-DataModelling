import pandas as pd
from DataProfilingData import *

def WeightedAverageOfValues(collection : list[float]) -> float:
    numerator = 0
    denominator = 0
    for i, item in enumerate(collection):
        weight = i + 1
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


def ProcessRelevantPlayerFantasyPoints(stats : pd.DataFrame) -> pd.DataFrame:
    # Select relevant columns and filter out finals
    playerData = stats[RelevantDataFields]

    # remove finals 
    playerData = playerData[~playerData["round.name"].str.contains("final", case=False, na=False)]

    # Add opponents to playerData
    playerData["opponent"] = playerData.apply(
        lambda row: row["away.team.name"] if row["team.name"] in row["home.team.name"]
        else row["home.team.name"] if row["team.name"] in row["away.team.name"]
        else None,
        axis=1
    )

    # combine player names
    playerData["playerName"] = playerData["player.player.player.givenName"] + " " + playerData["player.player.player.surname"]
    playerData.drop(columns="player.player.player.givenName", inplace=True)
    playerData.drop(columns="player.player.player.surname", inplace=True)

    return playerData


def SumTeamStatByRound(playerStats: pd.DataFrame, filter: str, stat: str) -> pd.DataFrame :
    
    # Group by groupColumn and round, aggregating relevant stats
    statGroupings = [filter, "round.roundNumber", "Year"]

    aggregatedStats = (
        playerStats.groupby(statGroupings, as_index=False)
        .agg(values=(stat, "sum"))
    )

    # Pivot the table: rows = teams, columns = rounds, values = dreamTeamPoints
    table = aggregatedStats.pivot(
        index=statGroupings[0], columns=["Year", "round.roundNumber"], values="values"
    )


    return table


def StatMeanPerYear(years : list[str], playerStats : pd.DataFrame) -> pd.DataFrame:

    valid_years = [year for year in years if year in playerStats.columns.get_level_values(0)]

    if not valid_years:
        raise ValueError("None of the specified years are present in the DataFrame.")

    avgTeamStatsPerYear = pd.DataFrame(columns=years)
    for year in valid_years : 
        avgTeamStatsPerYear[year] = (    
            playerStats.xs(key=year, level=0, axis=1)  # Select only columns for this year
            .mean(axis=1, skipna=True)
            .astype(float)
            .round(2)
        )

    return avgTeamStatsPerYear


def ComputeStatMeansAndDiff(meanStatPerYear: pd.DataFrame, label : str, reportTrend : bool, importedLeagueAverages : pd.DataFrame = None) -> pd.DataFrame :

    statData = pd.DataFrame(columns=[f"{label} W Mean", f"{label} Trend", f"{label}"])
    
    rawMean = meanStatPerYear.mean(axis=1, skipna=True).round(3)
        
    # Compute weighted mean
    statData[f"{label} W Mean"] = meanStatPerYear.apply(WeightedAverageOfValues, axis=1)
    
    # Compute league average
    if importedLeagueAverages is not None : 
        matching_columns = [col for col in importedLeagueAverages.columns if f"{label}+ W Mean" in col]

        if matching_columns:  # Check if there is at least one match
            leagueAverage = importedLeagueAverages[matching_columns[0]].values[0]  # Take the first match
        
    else : 
        leagueAverage = statData[f"{label} W Mean"].mean(axis=0).round(3)
    
    # Compute trend and differential
    statData[f"{label} Trend"] = AverageDifferential(statData[f"{label} W Mean"], rawMean)
    statData[f"{label}"] = AverageDifferential(statData[f"{label} W Mean"], leagueAverage)
    
    # Add league average row with a custom index
    statData.loc["League Average"] = {
        f"{label} W Mean": leagueAverage,
        f"{label} Trend": 0.0,
        f"{label}": 0.0
    }

    if reportTrend is False :
        statData.drop(columns=[f"{label} Trend"], inplace=True)    

    return statData
    

def GenerateStatMeansAndDiff(years : list[str], stats : pd.DataFrame, leagueAverages : pd.DataFrame = None, label : str = "", reportTrend : bool = False) -> pd.DataFrame:

    statMeanPerYear = StatMeanPerYear(years, stats[:])
    meansAndDiffs = ComputeStatMeansAndDiff(statMeanPerYear, label, reportTrend, leagueAverages)

    return meansAndDiffs


def ComputeUncontestedMarks(rawPlayerStats : pd.DataFrame, years : list[str], teamTypeFilter: str,  acummulationMethod, labelSuffix: str = "") -> pd.DataFrame:
    '''Computes Uncontested Marks profile'''

    totalMarksPerYear = acummulationMethod(rawPlayerStats, teamTypeFilter, "marks")
    totalContestedMarksPerYear = acummulationMethod(rawPlayerStats, teamTypeFilter, "contestedMarks")
    totalUncontestedMarksPerYear = totalMarksPerYear - totalContestedMarksPerYear
    statProfile = GenerateStatMeansAndDiff(years, totalUncontestedMarksPerYear, label=GetLabel("uncontestedMarks", labelSuffix))

    return statProfile


def GetLabel(statLabel : str, suffix : str = "") -> str:
    abv = StatAbV.get(statLabel)
    label = statLabel
    
    if abv is not None:
        label = abv
    
    label += suffix

    return label


def TeamStatDifferentials(title : str, rawPlayerStats : pd.DataFrame, relevantStats: list[str], pointsFor: bool, positionFilter: list[str] = None) -> pd.DataFrame:

    # Get unique years from the data
    years = sorted(rawPlayerStats["Year"].unique())

    teamTypeFilter = "team.name" if pointsFor else "opponent"
    labelSuffix =  "+" if pointsFor else "-"

    # filter by positions
    if positionFilter is not None :
        rawPlayerStats = rawPlayerStats[rawPlayerStats["player.player.position"].isin(positionFilter)]

    fantasyPointsPerGame = SumTeamStatByRound(rawPlayerStats, teamTypeFilter, "dreamTeamPoints")
    fantasyStatProfile = GenerateStatMeansAndDiff(years, fantasyPointsPerGame, label=GetLabel("dreamTeamPoints", labelSuffix), reportTrend=True)
    
    # Create list to store DataFrames 
    statProfileTables = [fantasyStatProfile]  
    
    for stat in relevantStats:
        if stat == "uncontestedMarks" :
            statProfileTables.append(ComputeUncontestedMarks(rawPlayerStats, years, teamTypeFilter, SumTeamStatByRound, labelSuffix))
        else :
            aggStatsFor = SumTeamStatByRound(rawPlayerStats, teamTypeFilter, stat)
            statProfile = GenerateStatMeansAndDiff(years, aggStatsFor, label=GetLabel(stat, labelSuffix))
            statProfileTables.append(statProfile)

    # Now concatenate all DataFrames in the list
    combinedStatProfiles = pd.concat(statProfileTables, axis=1)

    combinedStatProfiles.title = title
    
    return combinedStatProfiles


# requires injecting the league average
def PlayerStatDifferentials(rawPlayerStats : pd.DataFrame, leagueAverages : pd.DataFrame, playerName : str, relevantStats: list[str]) -> pd.DataFrame:

    # Get unique years from the data
    years = sorted(rawPlayerStats["Year"].unique())

    rawPlayerStats = rawPlayerStats[rawPlayerStats["timeOnGroundPercentage"] >= 0.5] 
    rawPlayerStats = rawPlayerStats[rawPlayerStats["playerName"] == playerName] 
    
    if rawPlayerStats.empty:
        raise ValueError("The specified player is present in the DataFrame.")

    # Create list to store DataFrames 
    statProfileTables = []


    fantasyPointsPerGame = SumTeamStatByRound(rawPlayerStats, "playerName", "dreamTeamPoints")
    fantasyStatProfile = GenerateStatMeansAndDiff(years, fantasyPointsPerGame, leagueAverages, GetLabel("dreamTeamPoints"), True)    
    statProfileTables.append(fantasyStatProfile)  

    for stat in relevantStats:
        if stat == "uncontestedMarks" :
            statProfileTables.append(ComputeUncontestedMarks(rawPlayerStats, years, "playerName", SumTeamStatByRound))
        else :
            aggStatsFor = SumTeamStatByRound(rawPlayerStats, "playerName", stat)
            statProfile = GenerateStatMeansAndDiff(years, aggStatsFor, leagueAverages, GetLabel(stat))
            statProfileTables.append(statProfile)

    
    combinedStatProfiles = pd.concat(statProfileTables, axis=1)
    combinedStatProfiles["team.name"] = rawPlayerStats["team.name"].iloc[0]

    combinedStatProfiles.title = playerName
    
    return combinedStatProfiles




def AverageDifferential(sample : float, avg : float) -> float: 
    diff = (-1 * (1 - (sample / avg)) * 100).round(2) 
    return diff

def DPrint(value, label : str = None) :
    if label is not None :
        print(f"\n {label.upper()}")

    print(f"\n{value}")

