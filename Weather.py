from datetime import datetime
from logging import warning, error, info
import logging
import os
import requests, re #type: ignore
from typing import Any
import time, threading
from urllib.parse import quote #type: ignore

_ctr: int = 1
_weather_file_path: str = 'weather_data.txt'
_city_file_path: str ="city_data.txt"
_error_log: str = "error.log"
_city_ready = threading.Event() # Needed for the subthread
_city_status: int               # Needed for the subthread

def _fetch_weather(city: str) -> dict[str, Any] | None:
    """
    # Description:
    Fetches the weather data from openweathermap. 
    
    @param
    - api_key: str | None: Holds your API key, fetching it from your environment variables. Replace 'WEATHER_API' if your variable is declared with a different name.
    - url: str: API URL
    - response: Response: Holds the Response from the API request. Hopefully the desired weather data.
    """
    global _ctr

    api_key: str | None = os.getenv('WEATHER_API')
    if not api_key:
        raise ValueError(f"Unable to fetch API key! Aborting...")
    url: str = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric'
    try:
        info("Fetching weather data...")
        response = requests.get(url)
    except requests.exceptions.ConnectionError:
        with open(_error_log, "a") as el:
            el.write(f"ConnectionError occured on {datetime.now().strftime("%H:%M:%S")}.\n")

        warning("No connection, utilizing cache.")
        with open(_weather_file_path, "r") as f:
            data = f.readlines()
        with open(_weather_file_path, "w", encoding="utf‑16") as f:
            f.writelines(data)

        with open(_city_file_path, "r") as cf:
            city_line = cf.read().strip()
        with open(_city_file_path, "w", encoding="utf‑16") as cf:
            cf.write(city_line)

        info("Cached data rewritten.")
        return

    if response.status_code == 200:
        _ctr = 1
        info("Received response with data.")
        print(response.headers)
        return response.json()
    else:
        warning(f'Error fetching weather data: {response.status_code}. Attempt {_ctr}/3. Retrying...')
        _ctr += 1
        if _ctr <= 3:
            return _fetch_weather(city)
        else:
            _ctr = 1
            raise ConnectionError(f"Unable to fetch weather data. Retrying in 300 seconds.")

def _write_to_temp(file_path: str, content: str) -> None:
    """
    # Description:
    Atomic file writes to ensure no broken files are read by save_weather_data().
    """
    temp_file_path: str = file_path + ".tmp"
    with open(temp_file_path, "w", encoding='utf‑16') as temp_file:
        temp_file.write(content)
    os.replace(temp_file_path, file_path)


def save_weather_data(weather_data: dict[str, Any]) -> None:
    """
    Description: This function writes the given city and weather data to their designated files:
    - city_data.txt
    - weather_data.txt
    
    @params
    - weather_data: dict[str, Any]: Dictionary with the given weather data.
    """
    try:
        weather_content: str = "No weather data available.\n"
        city_content: str = ""

        if weather_data:
            weather = weather_data['weather'][0]['description']
            temperature = weather_data['main']['temp']
            humidity = weather_data['main']['humidity']
            wind_speed = weather_data['wind']['speed']
            city_name = weather_data['name']

            weather_content = (f"{weather}\n"
                               f"{temperature}°C\n"
                               f"{humidity}%\n"
                               f"{wind_speed}m/s\n")

            city_content = (f"{city_name}")

        info("Writing weather data and city data to file.")
        _write_to_temp(_weather_file_path, weather_content)
        _write_to_temp(_city_file_path, city_content)

    except IOError as e:
        error(f"Failed to write to file: {e}")

"""
---------------------------------------------------------------------------------
Do whatever you want with this pain of a code block. It was meant to create a subthread in which a one time console
should be created to dynamically get the city input. Obviously failed at that.
Console logic is not implemented yet. As of right now, it'll only make a subthread which then takes the city input.

Leave this commented out if no dynamic input is wanted. Instead change the city variable in main()


Total hours wasted to get a console window without crashing the whole process: 8
---------------------------------------------------------------------------------

def get_city() -> None:
    global _city_file_path, _city_ready, _city_status
    while True:
        try:
            city_input: str = input("City and country as 'City, CountryCode' or 'exit' to quit: ").strip()
        except KeyboardInterrupt:
            _city_status = 1
            _city_ready.set()
            warning("KeyboardInterrupt. Aborting...")
            return
        except EOFError:
            _city_status = 1
            _city_ready.set()
            return

        if not city_input:
            continue

        if city_input.lower() == 'exit':
            _city_status = 1
            _city_ready.set()
            return


        _write_to_temp(_city_file_path, city_input)
        _city_status = 0
        _city_ready.set()
        return


def city_thread() -> bool:
    # Creates the subthread to get the city input.

    _city_ready.clear()
    t = threading.Thread(target=get_city)
    t.start()
    return True
"""


def main():
    """
    Main loop, I suggest not messing with the error handling
    """

    update_interval: int = 300

    """
    Part of the subthread logic, leave commented out when not using the subthread.


    # Pattern for: "City, Countrycode". Countrycode in Alpha-2 or Alpha-3 style.
    pattern = re.compile(r'^\s*([A-Za-z\s]+)\s*, \s*([A-Za-z]{2, 3})\s*$')

    #city_thread()
    #_city_ready.wait()

    if _city_status == 1:
        with open(_error_log, "w") as f:
            f.write(f"Exception occured at {datetime.now().strftime("%H:%M:%S")} in city_sub_thread. Unable to get city. Exiting with status {_city_status}\n")
        sys.exit(1)
    with open(_city_file_path, "r", encoding="utf-16") as f:
        city: str = f.read().strip()


    validate = pattern.match(city)

    if not validate:
        warning("Invalid format. Format: 'City, Countrycode' e.g. 'London, GB'.")
        main()
    else:
        # city_name, cc = validate.groups()
        # encoded_city: str = quote(f"{city_name.strip()},{cc.upper()}") # Ensures proper encoding of the city data. Sort of part of the sub thread, works anyways.
    """

    city: str = "Berlin, DE" # Hardcoded, will change once I figure out how to properly do the dynamic input without terminating the whole process.

    while True:
        try:
            weather_data: dict[str, Any] | None = _fetch_weather(city)
            if weather_data:
                info(f"Saving data.")
                save_weather_data(weather_data)
            elif weather_data is None and os.path.getsize(_weather_file_path) > 0 and os.path.getsize(_city_file_path) > 0:
                warning(f"No weather data received due to connection error. Using cache.")
            else:
                raise Exception(f"No weatherdata received and cache is empty.")

        except ValueError as e:
            with open(_error_log, "a") as el:
                el.write(f"Value Error at {datetime.now().strftime("%H:%M:%S")}\nException: {e}.\n")
            break
        except Exception as e:
            error(f"Exception occured: {e}")
            with open(_error_log, "a") as el:
                el.write(f"Exception occured at {datetime.now().strftime("%H:%M:%S")} of Type: {e.__class__.__name__}\nException: {e}.\n")
        finally:
            info("Sleeping...")
            time.sleep(update_interval)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
