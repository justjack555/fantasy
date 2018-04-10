# fantasy
A web front end for a fantasy baseball application.

# Names and UNIs
Forrest Hofmann (fhh2112)
Jack Ricci (jr3663)

# PostgreSQL Database UNI
jr3663

# Web Application URL
http://35.231.129.174:8111/

# Description of Features
Our fantasy baseball application offers users a subset of the options that may be available to them in a real fantasy sports application. Note that we implemented all of the features we proposed in the original project proposal. 

Our application allows users to sign up for and log in to accounts. Users can view their team's roster and can claim and waive players to and from their team with respect to league payroll limits. Users can view the leagues they compete in and all global leagues. Each user can create, join, and compete in multiple leagues. League standings are determined by the league stat weights and player stats. A league log of claim and waive transactions completed by each team in the league is also available.

Minor modifications were made to the database schema. Names of tables were simplified and the types of some ID attributes were changed from integers to varchars.

# Interesting Pages
1) Batter and pitcher scouting pages -- these pages provide a list of all batters and pitchers from the 2017 MLB season, relevant statistics, prices, and options to claim such players. When a user is logged in and chooses to claim a player, we extract the user ID and player ID, respectively. Given the user ID and player ID, we must first check if the player is already on the user's roster using the owns and transactions table. If not, we must then check if the claim of the player keeps the user's roster under budget with respect to the maximum payrolls of the leagues that the user competes in using the users table and leagues table. If so, then we create a new transaction entry in the transactions table and update the user's payroll in the users table.

2) League transaction pages -- these pages provide a list of all claim and waive transactions completed by each team in the league. Each page takes as input the league name. We must first find all users who play in the league by querying the plays table. For each such user, we must get a list of all their claim and waive transaction details by querying the users table, the players table, and the transactions table.
