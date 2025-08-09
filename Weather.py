from datetime import datetime
from logging import warning, error, info
import logging
import os
import requests, re
from typing import Any
import time
from urllib.parse import quote

ctr: int = 1
weather_file_path: str = 'F:\\ITG\\Python\\Weather\\weather_data.txt'
city_file_path: str ="F:\\ITG\\Python\\Weather\\city_data.txt"
error_log: str = "F:\\ITG\\Python\\Weather\\error.log"

def _fetch_weather(city: str) -> dict[str, Any] | None:
    global ctr

    api_key: str | None = os.getenv('WEATHER_API')
    if not api_key:
        raise ValueError(f"Unable to fetch API key! Aborting...")
    url: str = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric'
    try:
        info("Fetching weather data...")
        response = requests.get(url)
    except requests.exceptions.ConnectionError:
        with open(error_log, "a") as el:
            el.write(f"ConnectionError occured on {datetime.now().strftime("%H:%M:%S")}.\n")

        warning("No connection, utilizing cache.")
        with open(weather_file_path, "r") as f:
            data = f.readlines()
        with open(weather_file_path, "w", encoding="utf‑16") as f:
            f.writelines(data)

        with open(city_file_path, "r") as cf:
            city_line = cf.read().strip()
        with open(city_file_path, "w", encoding="utf‑16") as cf:
            cf.write(city_line)

        info("Cached data rewritten.")
        return

    if response.status_code == 200:
        ctr = 1
        info("Received response with data.")
        print(response.headers)
        return response.json()
    else:
        warning(f'Error fetching weather data: {response.status_code}. Attempt {ctr}/3. Retrying...')
        ctr += 1
        if ctr <= 3:
            return _fetch_weather(city)
        else:
            ctr = 1
            raise ConnectionError(f"Unable to fetch weather data. Retrying in 300 seconds.")

def _write_to_temp(file_path: str, content: str) -> None:
    temp_file_path: str = file_path + ".tmp"
    with open(temp_file_path, "w", encoding='utf‑16') as temp_file:
        temp_file.write(content)
    os.replace(temp_file_path, file_path)


def save_weather_data(weather_data: dict[str, Any]) -> None:
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
        _write_to_temp(weather_file_path, weather_content)
        _write_to_temp(city_file_path, city_content)

    except IOError as e:
        error(f"Failed to write to file: {e}")


def main():
    update_interval: int = 300
    pattern = re.compile(r'^\s*([A-Za-z\s]+)\s*, \s*([A-Za-z]{2})\s*$')

    city: str = input('City and Country in "City, Countrycode" format: ').strip()
    validate = pattern.match(city)
    if not validate:
        warning("Invalid format. Format: 'City, Countrycode' e.g. 'London, GB'.")
        main()

    else:
        city_name, cc = validate.groups()
        encoded_city: str = quote(f"{city_name.strip()},{cc.upper()}")

        while True:
            try:
                weather_data: dict[str, Any] | None = _fetch_weather(encoded_city)
                if weather_data:
                    info(f"Saving data.")
                    save_weather_data(weather_data)
                elif weather_data is None and os.path.getsize(weather_file_path) > 0 and os.path.getsize(city_file_path) > 0:
                    warning(f"No weather data received due to connection error. Using cache.")
                else:
                    raise Exception(f"No weatherdata received and cache is empty.")

            except ValueError as e:
                with open(error_log, "a") as el:
                    el.write(f"Value Error at {datetime.now().strftime("%H:%M:%S")}\nException: {e}.\n")
                break
            except Exception as e:
                error(f"Exception occured: {e}")
                with open(error_log, "a") as el:
                    el.write(f"Exception occured at {datetime.now().strftime("%H:%M:%S")} of Type: {e.__class__.__name__}\nException: {e}.\n")
            finally:
                info("Sleeping...")
                time.sleep(update_interval)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
























