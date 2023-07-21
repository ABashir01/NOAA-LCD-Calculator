This is a small calculator with a functions and a GUI using PySimpleGUI that calculates certain results from NOAA LCD CSV files.

# "Avg + Std Dev Daylight Temp": 
This function takes an LCD dataset and a date and returns the average and sample standard deviation of the Fahrenheit dry-bulb temperature between the times of sunrise and sunset.

# Windchills for Temps Sub-40
This function takes an LCD dataset and a date and returns the wind chills rounded to the nearest integer for the times when the temperature is less than or equal to 40 degrees Fahrenheit.

# Most Similar Day
This function takes two LCD datasets and returns the most similar day calculated based on the following explanation:

similar_day was basically centered around my ideas around what constituted a good way to check similarity between two days.
For a given date, I collected significant amounts of data for multiple conditions in a dictionary of dictionary of lists, and used that information to find the absolute difference of average values of, for example, the dry bulb temperatures in F for the same day in the different data sets. I then took the absolute differences for the 7 conditions I was considering - average dry bulb temperature, average wet bulb temperature, average relative humidity,average station pressure, average altimeter setting, net U component of the wind vector, net V component of the wind vector - and plugged them into a weighted sum. The weights all add up to 1. In the weighting, I decided to heavily lean towards temperature, so I gave dry bulb temperature and wet bulb temperature 0.25 for their weights, summing up to half (0.5) of the weighting being used on temperature. I also ultimately decided against adding Dew Point Temperature as I was already considering both dry bulb and wet bulb temperatures, as well as humidity, all of which correlated with Dew Point Temperature pretty closely - adding it would not necessarily significantly affect the results. I chose to give humidity a 0.125 weight as I was considering it in the temperature category of conditions for its impact on how the temperature actually feels. I ended up giving station pressure and the altimeter setting pretty low weightings, clocking in at 0.075 and 0.05, as I did not believe that pressure that was not particularly significant would not have a notable effect on how similar two sites might feel. In their own category, I gave the net U vectors and net V vectors both a weighting of 0.125 because I wanted the net wind on an area to be seriously considered when judging if two places have similar conditions at the same time because the wind, especially at higher temperatures, is generally very noticeable and you would notice if it is trending towards blowing in one direction, so I decided to convert to vectors and use the components of these vectors.