# Load required packages
library(fitzRoy)
library(dplyr)

# Fetch player data for season 2024
stats_data_2024 <- fetch_player_stats(2024)
  
# Save the dataset to a CSV file
write.csv(stats_data_2024, "/Users/rkeable/Personal/Projects/AFL-Fantasy-DataModelling/Data/player_stats_data_2024.csv", row.names = FALSE)

# Open the data in RStudio's View pane
View(stats_data_2024)


# Fetch fixture data for season 2025
# fixture_data_2025 <- fetch_fixture(season = 2025) %>%
#  select(compSeason.name, round.name, home.team.name, away.team.name, venue.name)
