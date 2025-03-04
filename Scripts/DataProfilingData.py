RelevantDataFields = [
        "Year", "round.roundNumber", "round.name", "team.name", "venue.name", "home.team.name", "away.team.name",
        "player.player.player.givenName", "player.player.player.surname", "dreamTeamPoints", "player.player.position", 
        "timeOnGroundPercentage", "goals", "behinds", "kicks", "handballs", "disposals", "marks", "bounces", "tackles",
        "contestedPossessions",  "uncontestedPossessions", "inside50s", "marksInside50", "contestedMarks", "hitouts", 
        "disposalEfficiency", "rebound50s", "goalAssists", "turnovers", "intercepts", "tacklesInside50", "shotsAtGoal",
        "metresGained", "clearances.centreClearances", "clearances.stoppageClearances", "extendedStats.kickEfficiency",
        "extendedStats.kickToHandballRatio", "extendedStats.marksOnLead", "extendedStats.interceptMarks", "extendedStats.hitoutsToAdvantage", 
        "extendedStats.groundBallGets", "extendedStats.scoreLaunches", "extendedStats.defHalfPressureActs", "extendedStats.centreBounceAttendances",
        "extendedStats.kickins", "extendedStats.kickinsPlayon","extendedStats.contestedPossessionRate", "extendedStats.kickToHandballRatio", "clearances.totalClearances",
        "freesFor", "freesAgainst"
        ]

MidfieldPositionTitles = ["R", "RR", "C"]
BackPositionTitles = ["BPL", "BPR", "HBFL", "HBFR"]
TransitionPositionTitles = ["HFFL", "HFFR", "W"]
RuckPositionTitle = ["RK"]

StatAbV = {
    "dreamTeamPoints" : "FP",
    "goals": "G",
    "behinds": "B",
    "kicks": "K",
    "handballs": "H",
    "marks": "M",
    "disposals": "D",
    "tackles": "T",
    "contestedPossessions": "CP",
    "uncontestedPossessions": "UP",
    "uncontestedMarks": "UM",
    "contestedMarks": "CM",
    "clearances.totalClearances": "CLR",
    "inside50s": "i50", 
    "disposalEfficiency" : "DE%", 
    "rebound50s" : "R50", 
    "metresGained" : "MTR", 
    "extendedStats.kickEfficiency" : "KE%",
    "extendedStats.marksOnLead" : "ML",
    "extendedStats.interceptMarks" : "IM", 
    "extendedStats.scoreLaunches" : "SL", 
    "extendedStats.kickins" : "KIN", 
    "extendedStats.kickinsPlayon" : "KIPO",
    "marksInside50" : "Mi50",
    "tacklesInside50" : "Ti50",
    "goalAssists" : "GA",
    "extendedStats.groundBallGets" : "GBG",
    "hitouts" : "HO", 
    "extendedStats.hitoutsToAdvantage" : "HtA",
    "freesAgainst" : "FA",
    "freesFor" : "FF",
    "intercepts" : "I"

}


RelevantTeamStats = [ 
        "uncontestedPossessions", "contestedPossessions",
        "marks", "contestedMarks", "uncontestedMarks",
        "kicks", "handballs", "disposals", 
        "tackles","clearances.totalClearances",
        "goals", "behinds", "freesFor", "freesAgainst"
]

RelevantTransitionStats = [
        "inside50s", "marksInside50", "rebound50s", "bounces",
        "metresGained", "extendedStats.kickEfficiency", 
        "extendedStats.marksOnLead", "extendedStats.scoreLaunches" 
        ]

RelevantMidfieldStats = [
        "inside50s", "marksInside50", 
        "disposalEfficiency", "rebound50s", 
        "goalAssists", "tacklesInside50", "metresGained", 
        "extendedStats.groundBallGets", "extendedStats.scoreLaunches", 
        "extendedStats.centreBounceAttendances",
        ]

RelevantHalfbackStats = [
        "bounces", "inside50s", "disposalEfficiency", "rebound50s", 
        "metresGained", "extendedStats.kickEfficiency", 
        "extendedStats.marksOnLead", "extendedStats.interceptMarks", 
        "extendedStats.scoreLaunches", "extendedStats.kickins", "extendedStats.kickinsPlayon", 
        ]

RelevantRuckStats = [
        "hitouts", "extendedStats.hitoutsToAdvantage",
        "intercepts", "extendedStats.interceptMarks", "marksInside50", "extendedStats.marksOnLead",
        ]


FantasyPointsLUT = {
    "contestedPossessions": 0,  # No direct fantasy points
    "marks": 3,  # Includes both contested & uncontested
    "contestedMarks": 0,  # No direct fantasy points
    "uncontestedMarks": 0,  # No direct fantasy points
    "kicks": 3,
    "handballs": 2,
    "tackles": 4,
    "clearances.totalClearances": 0,  # No direct fantasy points
    "goals": 6,
    "behinds": 1,
    "freesFor": 1,
    "freesAgainst": -3,
    "hitouts" : 1,
    "extendedStats.kickinsPlayon" : 3
}

FantasyProjectionWeights = {
    "uncontestedPossessions": 0,  
    "clearances.totalClearances": 0,
    "uncontestedMarks": 0,
    "extendedStats.kickinsPlayon" : 0,
    
}
