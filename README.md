# Names and UNIs
Forrest Hofmann (fhh2112)
Jack Ricci (jr3663)

# PostgreSQL Database UNI
jr3663

# Web Application URL
http://35.231.129.174:8111/

## Change #1: Addition of Text Attribute
The text attribute addition made to the database schema was the addition of
a league_bio column in the leagues table. The league_bio is a paragraph
describing the motivation behind the fantasy league and which users 
should consider signing up for the league. The league_bio attribute has type
tsvector, so the values stored in the column are lexemes found in the inserted
biography paragraph. These lexemes allow for front-end enhancements to the 
application that might include an option for users to find relevant leagues 
based upon keywords. The keywords could then be utilized to form a tsquery
value for matching against the leagues table's store of league_bio values.

## Change #2: Addition of array Attribute
To give users insight into how many baseball seasons a player has played, 
the players table was given an extra attribute: years_played, which is an 
array of integer values corresponding to the years that the player had 
played in the major leagues. Providing users with an idea of which seasons 
a given player has been a professional for will allow users
# Interesting Pages
1) Batter and pitcher scouting pages -- these pages provide a list of all batters and pitchers from the 2017 MLB season, relevant statistics, prices, and options to claim such players. When a user is logged in and chooses to claim a player, we extract the user ID and player ID, respectively. Given the user ID and player ID, we must first check if the player is already on the user's roster using the owns and transactions table. If not, we must then check if the claim of the player keeps the user's roster under budget with respect to the maximum payrolls of the leagues that the user competes in using the users table and leagues table. If so, then we create a new transaction entry in the transactions table and update the user's payroll in the users table.

2) League transaction pages -- these pages provide a list of all claim and waive transactions completed by each team in the league. Each page takes as input the league name. We must first find all users who play in the league by querying the plays table. For each such user, we must get a list of all their claim and waive transaction details by querying the users table, the players table, and the transactions table.
