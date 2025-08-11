# Weather Script Ver. 1.0.2

Based on python, this script fetches the weather data of a given City and writes it to a textfile for later usage in other programs or scripts. 
This script will fetch new data every 5 Minutes. 
If it fails to fetch due to a connection error, it won't change the files.

To execute it, run py Weather.py in a terminal while being in the same directory as Weather.py. The .exe will not work for now.
(I did not manage to create dynamic city inputs yet)

# IMPORTANT
- Anything commented out should remain commented out and please read the comments.
- As of right now, you have to hardcore your city into the script. Default is 'Berlin, DE'
- You will need your own API key (https://openweathermap.org/api) and set it in your environment variables.
- I did not test to see if this works on linux. I suggest utilizing this only on windows for now. 
- This script can only be run directly in a terminal.

# Note
Dynamic inputs for the city variable won't work as of right now. Once again, this script needs to be run in the terminal. 
A SyntaxWarning is given in the output after executing the script. You can safely ignore this as any code related to it is commented out.
Any suggestions can be directed towards me via Discord.

I will update this and most likely switch to a GUI solution so I don't have to try and mess around with consoles.

(This is completly overengineered to not crash)

If errors occure, message me on Discord with your error.log / general contact:
<https://discord.com/users/752592909848674395>
