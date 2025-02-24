import pandas as pd

def GetPlayerFantasyPoints(stats) :
    # Select relevant columns and filter out finals
    playerData = stats[[
        "round.roundNumber", "round.name", "team.name", "venue.name", "home.team.name", "away.team.name",
        "player.player.player.givenName", "player.player.player.surname", "dreamTeamPoints", "teamStatus"
        ]]

    # remove finals 
    playerData = playerData[~playerData["round.name"].str.contains("final", case=False, na=False)]

    # Add opponents to playerData
    playerData["opponent"] = playerData.apply(
        lambda row: row["away.team.name"] if row["team.name"] in row["home.team.name"]
        else row["home.team.name"] if row["team.name"] in row["away.team.name"]
        else None,
        axis=1
    )

    return playerData

# //
# 
# GET AVERAGE PFPG (Points For Per Game) PER TEAM
# 
# //

def TeamPointsForPerRound(playerData) : 
    # Group by team and round, summing the dreamTeamPoints
    teamPointsForPerGame = (
        playerData.groupby(["team.name", "round.roundNumber"], as_index=False)
        .agg(dreamTeamPoints=("dreamTeamPoints", "sum"))
    )

    # Pivot the table: rows = teams, columns = rounds, values = dreamTeamPoints
    teamPointsForPerGame = teamPointsForPerGame.pivot(
        index="team.name", columns="round.roundNumber", values="dreamTeamPoints"
    ).fillna(0)  # Fill NaNs with 0 for rounds where teams didn't score

    # Calculate the average per team, excluding 0.0 values
    teamPointsForPerGame["Avg_PFPG"] = teamPointsForPerGame.replace(0.0, pd.NA).mean(axis=1, skipna=True).astype(float).round(2)
    # Mask invalid values

    return teamPointsForPerGame

# //
# 
# GET AVERAGE PAPG (Points Against Per Game) PER TEAM
# 
# //
def TeamPointsAgainstPerGame(playerData) : 

    # Group by team and round, summing the dreamTeamPoints
    teamPointsAgainstPerGame = (
        playerData.groupby(["opponent", "round.roundNumber"], as_index=False)
        .agg(dreamTeamPoints=("dreamTeamPoints", "sum"))
    )

    # Pivot the table: rows = teams, columns = rounds, values = dreamTeamPoints
    teamPointsAgainstPerGame = teamPointsAgainstPerGame.pivot(
        index="opponent", columns="round.roundNumber", values="dreamTeamPoints"
    ).fillna(0)  # Fill NaNs with 0 for rounds where teams didn't score

    # Calculate the average per team, excluding 0.0 values
    teamPointsAgainstPerGame["Avg_PAPG"] = teamPointsAgainstPerGame.replace(0.0, pd.NA).mean(axis=1, skipna=True).astype(float).round(2)

    return teamPointsAgainstPerGame


# //
# 
# GET AVERAGE PFPG (Points For Per Game) PER VENUE
# 
# //


def TeamPointsPerGamePerVenue(playerData) : 
    # Compute mean DreamTeamPoints per game per venue (instead of sum)
    teamPointsPerGamePerVenue = (
        playerData.groupby(["team.name", "venue.name", "round.roundNumber"], as_index=False)
        .agg(dreamTeamPoints=("dreamTeamPoints", "sum"))  # Mean per game, not sum
    )

    # Calculate the mean DreamTeamPoints per venue
    teamPointsPerGamePerVenue = teamPointsPerGamePerVenue.groupby("venue.name")["dreamTeamPoints"].mean().round(2)

    return teamPointsPerGamePerVenue


# //
# 
# CALC DIFFERENTIALS PER TEAM
# 
# //

def AverageDifferential(sample, avg) : 
    diff = (-1 * (1 - sample / avg) * 100).astype(float).round(2)  # Exclude "Avg_PPG" from calculation
    return diff


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

    print("")
    print("TEAM: " + teamName)
    print(gamesForTeam)
    print("")

    return gamesForTeam

def WeightedAverageOfValues(collection : list[float]) :
    numerator = 0
    denominator = 0
    for i, item in enumerate(collection):
        weight = i + 1
        item *= weight
        numerator += item
        denominator += weight

    return (numerator / denominator)
