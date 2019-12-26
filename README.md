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
* Use exact locations, ideally street names.
* Some places like 'Starbucks' are ambiguous and should be flagged accordingly (see typical_week.json)
* If all addresses are important, set "take_all". The average travel time of all locations is considered. 

## Comments and improvements
I ignore the means of travel (e.g. you might not want to ride a bike during winter) and number of 'legs' (sections) per route (a 20 minute non-stop trip might be preferrable to 15 minute traveling with 2 stops).