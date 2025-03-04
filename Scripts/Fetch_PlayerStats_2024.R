# Load required packages
library(fitzRoy)
library(dplyr)

# Fetch player data for seasons 2022-2024

print("Fetch Player Stats 2022-2024")
stats_data_2022 <- fetch_player_stats(2022) %>% mutate(Year = 2022)
stats_data_2023 <- fetch_player_stats(2023) %>% mutate(Year = 2023)
stats_data_2024 <- fetch_player_stats(2024) %>% mutate(Year = 2024)

# Combine all three years into one sheet with the year as a column 
print("Combine Player Stats 2022-2024")
playerStats_22_to_24_AFL <- bind_rows(stats_data_2022, stats_data_2023, stats_data_2024)


print("Write Data to CSVs")

# Save the dataset to a CSV file
write.csv(playerStats_22_to_24_AFL, "/Users/rkeable/Personal/Projects/AFL-Fantasy-DataModelling/Data/Import/playerStats_22_to_24_AFL.csv", row.names = FALSE)


# print("Fetch Player Stats from FootyWire and AFLTables for 2024")
# playerStats_fw_2024 <- fetch_player_stats_footywire(2024) %>% mutate(Year = 2024)
# playerStats_tables_2024 <- fetch_player_stats_afltables(2024) %>% mutate(Year = 2024)

# write.csv(playerStats_fw_2024, "/Users/rkeable/Personal/Projects/AFL-Fantasy-DataModelling/Data/PlayerStats_fw_2024.csv", row.names = FALSE)
# write.csv(playerStats_tables_2024, "/Users/rkeable/Personal/Projects/AFL-Fantasy-DataModelling/Data/PlayerStats_tables_2024.csv", row.names = FALSE)


# write.csv(fetch_results_footywire(2024), "/Users/rkeable/Personal/Projects/AFL-Fantasy-DataModelling/Data/Results_fw_2024.csv", row.names = FALSE)

# Open the data in RStudio's View pane
# View(stats_data_2024)

print("Fetch and write 2025 Fixture Data to csv")

# Fetch fixture data for season 2025
fixture_data_2025 <- fetch_fixture(season = 2025) %>%
select(compSeason.name, round.name, home.team.name, away.team.name, venue.name)
write.csv(fixture_data_2025, "/Users/rkeable/Personal/Projects/AFL-Fantasy-DataModelling/Data/Fixture_data_2025.csv", row.names = FALSE)
