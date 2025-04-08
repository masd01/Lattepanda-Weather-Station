import python_weather
import asyncio
import os
import datetime
import serial
import time
import socket

# Σύνδεση με το Arduino
arduino_port = "COM5"  # Άλλαξε το COM αν χρειάζεται
baud_rate = 9600
ser = serial.Serial(arduino_port, baud_rate, timeout=1)
time.sleep(2)  # Περιμένουμε να σταθεροποιηθεί η σύνδεση

hostname = socket.gethostname() # Βρίσκουμε το hostname του υπολογιστή
my_ip = socket.gethostbyname(hostname) # Παίρνουμε την IP διεύθυνση
print("IP:", my_ip)

def get_weather_emoji(description):
    description = description.lower()
    if "clear" in description:
        return "Clear"#☀️" #"☀"
    elif "cloud" in description:
        return "Cloud"#☁️" #"☁"️
    elif "rain" in description:
        return "Rain"#🌧️" #"🌧"
    elif "thunderstorm" in description:
        return "Thunder"#⛈️" #"⛈"️
    elif "snow" in description:
        return "Snow"#❄️" #"❄"️
    elif "fog" in description or "mist" in description:
        return "Fog"#🌫️" #"🌫"️
    return "🌍" #"🌍"

async def get_weather():
    async with python_weather.Client(unit=python_weather.METRIC) as client:
        weather = await client.get('Athens, Greece')
        emoji = get_weather_emoji(weather.description)
        return f"{emoji} {weather.temperature}'C, {weather.humidity}% Hum, {weather.wind_speed}km/h {weather.wind_direction}" #, IP:{my_ip}"

async def send_data():
    while True:
        now = datetime.datetime.now()
        date_str = now.strftime("%A %d %b %Y")
        time_str = now.strftime("%H:%M:%S")

        weather_info = await get_weather()

        data_to_send = f"{time_str}|{date_str}, {weather_info}\n"
        ser.write(data_to_send.encode("utf-8"))

        # Συγχρονισμός ακριβώς ανά δευτερόλεπτο
        time.sleep(1 - (time.time() % 1))

if __name__ == "__main__":
    if os.name == "nt":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(send_data())