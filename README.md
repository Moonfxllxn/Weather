# Weather Script

Based on python, this script fetches the weather data of a given City and writes it to a file for later usage. 
This script will fetch new data every 5 Minutes. If it fails to fetch due to a connection error, it won't change the files.

To execute it, simply run the .exe file located in dist/Weather.exe. It should ask you to input the desired City and Country code in the format "City, COUNTRYCODE"
Any other format will fail.

# IMPORTANT
- You will need your own API key and set it in your environment variables.
- I did not test to see if this works on linux. I suggest utilizing this only on windows for now. 
