# Communite optimization
## Description

Ever wondered **where's the best place to live** within a city?

This project won't give you a perfect answer, but it can tell you how you would **reduce commute and travel time** living at hypothetical addresses.

Enter addresses you would like to live at, places (work, gym, friends, cafes, ...) you regularly visit and a typical schedule to calculate your monthly travel using Azure Maps.

## Preparation
### Azure Maps
* You'll need an Azure subscription. It's really easy to create one and get enough free budget.
* Create an Azure Maps resource with a S1 plan (necessary for routing).
* Copy one of your Azure Maps secret keys (Shared Key Authentication) and add it as 'SECRETKEY' to your environment variables (e.g. SET SECRETKEY=YOURSECRETKEYHERE). Alternatively use an .env file if you use VS Code.

### Config
* Enter a few addresses in 'data/potential_addresses.json'.
* Enter your typical weekly schedule in 'data/typical_week.json'

### Some hints for typical_week.json
* Use exact locations, ideally the exact address incl. ZIP code and city.
* Some places like 'Starbucks' are ambiguous and should be flagged accordingly (see typical_week.json) so you find the nearest starbucks.
* If all addresses are important, set "take_all". The average travel time of all locations is considered. 
* Average the amount of trips over longer periods like months or years and then recalculate them per week.
* Only count the trips where you travel (e.g. when considering how often you meet friends).

## Comments and further improvements
I ignore the means of travel (e.g. you might not want to ride a bike during winter) and number of 'legs' (sections) per route (a 20 minute non-stop trip might be preferrable to 15 minute traveling with 2 stops).

I want to add a max. search radius for some searches.

I want to add more generic search (nearby cafes with 3+ stars).

There's a 'bug', that currently all trips are calculated for the January 6th 2020, 8pm UTC. I want to allow the user to set specific times.