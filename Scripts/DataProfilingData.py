RelevantDataFields = [
        "Year", "round.roundNumber", "round.name", "team.name", "venue.name", "home.team.name", "away.team.name",
        "player.player.player.givenName", "player.player.player.surname", "dreamTeamPoints", "player.player.position", 
        "timeOnGroundPercentage", "goals", "behinds", "kicks", "handballs", "disposals", "marks", "bounces", "tackles",
        "contestedPossessions",  "uncontestedPossessions", "inside50s", "marksInside50", "contestedMarks", "hitouts", 
        "disposalEfficiency", "rebound50s", "goalAssists", "turnovers", "intercepts", "tacklesInside50", "shotsAtGoal",
        "metresGained", "clearances.centreClearances", "clearances.stoppageClearances", "extendedStats.kickEfficiency",
        "extendedStats.kickToHandballRatio", "extendedStats.marksOnLead", "extendedStats.interceptMarks", "extendedStats.hitoutsToAdvantage", 
        "extendedStats.groundBallGets", "extendedStats.scoreLaunches", "extendedStats.defHalfPressureActs", "extendedStats.centreBounceAttendances",
        "extendedStats.kickins", "extendedStats.kickinsPlayon","extendedStats.contestedPossessionRate", "extendedStats.kickToHandballRatio", "clearances.totalClearances"
        ]

MidfieldPositionTitles = ["R", "RR", "C"]
BackPositionTitles = ["BPL", "BPR", "HBFL", "HBFR"]
TransitionPositionTitles = ["HFFL", "HFFR", "W"]
RuckPositionTitle = ["RK"]

StatAbV = {
    "goals": "G",
    "behinds": "B",
    "kicks": "K",
    "handballs": "H",
    "marks": "M",
    "disposals": "D",
    "tackles": "T",
    "contestedPossessions": "CP",
    "uncontestedPossessions": "UP",
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

}

RelevantTeamStats = [
        "kicks","disposals", "tackles", 
        "contestedPossessions", "uncontestedPossessions", "clearances.totalClearances"
]

RelevantStoppageStats = [
        "kicks", "disposals", "tackles", "contestedPossessions", 
        "clearances.centreClearances", "clearances.stoppageClearances", 
        "extendedStats.groundBallGets", "extendedStats.centreBounceAttendances"
        ]

RelevantTransitionStats = [
        "uncontestedPossessions", "kicks", "handballs",
        "inside50s", "marksInside50", "rebound50s", "bounces",
        "metresGained", "extendedStats.kickEfficiency", 
        "extendedStats.marksOnLead", "extendedStats.scoreLaunches" 
        ]

RelevantMidfieldStats = [
        "uncontestedPossessions", "contestedPossessions", "goals", "kicks", "handballs", "disposals", "tackles", "inside50s", 
        "marksInside50", "clearances.totalClearances",
        "disposalEfficiency", "rebound50s", 
        "goalAssists", "tacklesInside50", "metresGained", 
        "extendedStats.groundBallGets", "extendedStats.scoreLaunches", 
        "extendedStats.centreBounceAttendances", 
        ]

RelevantHalfbackStats = [
        "uncontestedPossessions", "kicks", "disposals", "tackles", "bounces",
        "inside50s", "contestedMarks", "disposalEfficiency", "rebound50s", 
        "metresGained", "extendedStats.kickEfficiency", 
        "extendedStats.marksOnLead", "extendedStats.interceptMarks", 
        "extendedStats.scoreLaunches", "extendedStats.kickins", "extendedStats.kickinsPlayon", 
        ]

RelevantRuckStats = [
        "tackles", "contestedPossessions", "marksInside50", "contestedMarks", "hitouts", 
        "intercepts", "clearances.centreClearances", "clearances.stoppageClearances", "extendedStats.marksOnLead", 
        "extendedStats.interceptMarks", "extendedStats.hitoutsToAdvantage", "extendedStats.centreBounceAttendances"
        ]
