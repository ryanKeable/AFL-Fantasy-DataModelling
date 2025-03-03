import pandas as pd
from DataProfilingData import *

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
    playerData["playerNames"] = playerData["player.player.player.givenName"] + " " + playerData["player.player.player.surname"]
    playerData.drop(columns="player.player.player.givenName", inplace=True)
    playerData.drop(columns="player.player.player.surname", inplace=True)

    return playerData


def AggregatePlayerStatsPerTeam(playerStats: pd.DataFrame, filters: list[str], stats: str) -> pd.DataFrame :
    
    # Group by groupColumn and round, aggregating relevant stats
    statGroupings = filters + ["round.roundNumber", "Year"]

    aggregatedPoints = (
        playerStats.groupby(statGroupings, as_index=False)
        .agg(values=(stats, "sum"))
    )

    # Pivot the table: rows = teams, columns = rounds, values = dreamTeamPoints
    table = aggregatedPoints.pivot(
        index=filters[0], columns=["Year", "round.roundNumber"], values="values"
    ).fillna(0)  # Fill NaNs with 0 for rounds where teams didn't score

    return table

def teamStatsMeanPerYear(years : list[str], stats : pd.DataFrame) -> pd.DataFrame:
    avgTeamStatsPerYear = pd.DataFrame(columns=years)
    for year in years : 
        avgTeamStatsPerYear[year] = (
            stats.xs(key=year, level=0, axis=1)  # Select only columns for this year
            .replace(0.0, pd.NA)  # Replace 0 with NaN to ignore them in averaging
            .mean(axis=1, skipna=True)
            .astype(float)
            .round(2)
        )

    return avgTeamStatsPerYear


def CalcMeansAndDiff(avgTeamStatsPerYear: pd.DataFrame, label : str, trackTrend : bool = False, isFor : bool = False) -> pd.DataFrame :
    abv = StatAbV.get(label)
    if abv is not None:
        label = abv

    if isFor is True:
        label += "+"
    else :
        label += "-"

    avgTeamStatsPerYear[f"{label} Mean"] = avgTeamStatsPerYear.mean(axis=1).round(2)
    avgTeamStatsPerYear[f"{label} W Avg"] = avgTeamStatsPerYear.apply(WeightedAverageOfValues, axis=1)
    avgTeamStatsPerYear[f"{label} Trend"] = AverageDifferential(avgTeamStatsPerYear[f"{label} W Avg"], avgTeamStatsPerYear[f"{label} Mean"])

    leagueMean = avgTeamStatsPerYear[f"{label} W Avg"].mean(axis=0)
    avgTeamStatsPerYear[f"{label}"] = AverageDifferential(avgTeamStatsPerYear[f"{label} W Avg"], leagueMean)

    if trackTrend :
        return avgTeamStatsPerYear[[f"{label}", f"{label} Trend"]]
    else : 
        return avgTeamStatsPerYear[[f"{label}"]]


def AverageStatDiff(years : list[str], stats : pd.DataFrame, label : str, trackTrend : bool = False, isFor : bool = False) -> pd.DataFrame :

    avgTeamStatsPerYear = teamStatsMeanPerYear(years, stats)
    meansAndDiffs = CalcMeansAndDiff(avgTeamStatsPerYear, label, trackTrend, isFor)

    return meansAndDiffs


def GetMarkStats(playerStats : pd.DataFrame, combinedTeamStats : pd.DataFrame, years : list[str], teamFilter: str, pointsFor: bool) -> pd.DataFrame:
    '''Returns Mark and Uncontested Marks differentials to the league averages'''

    markStats = []
    marksFor = AggregatePlayerStatsPerTeam(playerStats, [teamFilter], "marks")
    marksForDiff = AverageStatDiff(years, marksFor, "marks", False, pointsFor)
    
    markStats.append(marksForDiff)

    contestedMarksFor = AggregatePlayerStatsPerTeam(playerStats, [teamFilter], "contestedMarks")
    uncontestedMarksFor = marksFor - contestedMarksFor
    uncontestedMarksForDiff = AverageStatDiff(years, uncontestedMarksFor, "UM", False, pointsFor)

    markStats.append(uncontestedMarksForDiff)

    combinedTeamStats = pd.concat([combinedTeamStats] + markStats, axis=1)
    
    return combinedTeamStats

def GetStatsRatioDiff(playerStats : pd.DataFrame, stats01: str, stats02: str, label: str, combinedTeamStats : pd.DataFrame, years : list[str], teamFilter: str, pointsFor: bool) -> pd.DataFrame:
    # gather marks

    accuracyStats = []
    goalsFor = AggregatePlayerStatsPerTeam(playerStats, [teamFilter], stats01)
    behindsFor = AggregatePlayerStatsPerTeam(playerStats, [teamFilter], stats02)
    totalShotsFor = goalsFor + behindsFor
    accuracyForPercentage = (goalsFor / totalShotsFor).round(2)
    accuracyForPercentaageDiff = AverageStatDiff(years, accuracyForPercentage, label, False, pointsFor)
    accuracyStats.append(accuracyForPercentaageDiff)

    combinedTeamStats = pd.concat([combinedTeamStats] + accuracyStats, axis=1)
    
    return combinedTeamStats


def TeamStatDifferentials(playerStats : pd.DataFrame, relevantStats: list[str], pointsFor: bool, positionFilter: list[str] = None, calcGoalAccuracy: bool = False) -> pd.DataFrame:

    # Get unique years from the data
    years = sorted(playerStats["Year"].unique())

    teamTypeFilter = "team.name" if pointsFor else "opponent"

    # filter by positions
    if positionFilter is not None :
        playerStats = playerStats[playerStats["player.player.position"].isin(positionFilter)]

    # Get aggregated fantasy points for and against per team
    teamPointsForPerGame = AggregatePlayerStatsPerTeam(playerStats, [teamTypeFilter], "dreamTeamPoints")

    # Calculate the average per team per year, excluding 0.0 values
    combinedTeamStats = AverageStatDiff(years, teamPointsForPerGame, "FP", True, pointsFor)

    # Mark Stats
    combinedTeamStats = GetMarkStats(playerStats, combinedTeamStats, years, teamTypeFilter, pointsFor)
    combinedTeamStats = GetStatsRatioDiff(playerStats, "kicks", "handballs", "KR", combinedTeamStats, years, teamTypeFilter, pointsFor)
    
    if calcGoalAccuracy : 
        combinedTeamStats = GetStatsRatioDiff(playerStats, "goals", "behinds", "GR", combinedTeamStats, years, teamTypeFilter, pointsFor)

    relevantTeamStatDFs = []  # Create an empty list to store DataFrames
    # these need to be divided per round
    for stats in relevantStats:
        aggStatsFor = AggregatePlayerStatsPerTeam(playerStats, [teamTypeFilter], stats)
        statAvgFor = AverageStatDiff(years, aggStatsFor, stats, False, pointsFor)
        relevantTeamStatDFs.append(statAvgFor)

    # Now concatenate all DataFrames in the list
    combinedTeamStats = pd.concat([combinedTeamStats] + relevantTeamStatDFs, axis=1)


    print(f"\n{combinedTeamStats}")
    
    return combinedTeamStats



def AverageDifferential(sample : float, avg : float) -> float: 
    diff = (-1 * (1 - (sample / avg)) * 100).round(2) 
    return diff



def TeamPointsPerGamePerVenue(playerData) : 
    # Compute mean DreamTeamPoints per game per venue (instead of sum)
    teamPointsPerGamePerVenue = (
        playerData.groupby(["team.name", "venue.name", "round.roundNumber"], as_index=False)
        .agg(dreamTeamPoints=("dreamTeamPoints", "sum"))  # Mean per game, not sum
    )

    # Calculate the mean DreamTeamPoints per venue
    teamPointsPerGamePerVenue = teamPointsPerGamePerVenue.groupby("venue.name")["dreamTeamPoints"].mean().round(2)

    return teamPointsPerGamePerVenue



def AverageDifferentialsPerTeam(playerData, teamName, teamPointsForPerGame, teamPointsAgainstPerGame, teamPointsPerGamePerVenue) :
    gamesForTeam = pd.DataFrame(playerData[playerData["team.name"] == teamName])
    gamesForTeam = gamesForTeam.drop_duplicates(subset=["round.roundNumber", "team.name"])

    # Select relevant columns
    gamesForTeam = gamesForTeam.set_index("round.roundNumber")
    gamesForTeam = gamesForTeam[["team.name", "opponent", "venue.name"]]

    # Get team's points for season avg 
    PFPG_AVG = teamPointsForPerGame.loc[teamName]["Avg_PFPG"]
    gamesForTeam["PF_AVG"] = PFPG_AVG

    # Get team's points for per game
    gamesForTeam["PF"] = teamPointsForPerGame.loc[teamName]
    team_PFPG = gamesForTeam["PF"]

    # Calculate the for points differential (team's round points - team's PF season average)    
    diffPF = AverageDifferential(team_PFPG, PFPG_AVG)
    gamesForTeam["PF_diff"] = diffPF

    # Get team's opponents points against season avg
    adelaide_opponent_PFPG_AVG = teamPointsAgainstPerGame["Avg_PAPG"].reindex(gamesForTeam["opponent"])
    adelaide_opponent_PFPG_AVG.index = gamesForTeam.index
    gamesForTeam["Opp_PAPG"] = adelaide_opponent_PFPG_AVG

    # Calculate the for points differential (team's round points - Opponents's PA season average)
    diffPA = AverageDifferential(team_PFPG, adelaide_opponent_PFPG_AVG)
    gamesForTeam["PA_diff"] = diffPA

    # Get venue averages for each corresponding round
    venueAvgPFPG = teamPointsPerGamePerVenue.reindex(gamesForTeam["venue.name"])

    # Convert to DataFrame and assign the correct index
    venueAvgPFPG = pd.DataFrame(venueAvgPFPG)
    venueAvgPFPG.index = gamesForTeam.index  # Set index to round.roundNumber

    diffPV = AverageDifferential(team_PFPG, venueAvgPFPG["dreamTeamPoints"])

    gamesForTeam["Venue_AVG"] = venueAvgPFPG["dreamTeamPoints"]
    gamesForTeam["PPV_diff"] = diffPV

    return gamesForTeam

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
