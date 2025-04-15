import serial
from datetime import datetime
import time
import asyncio
import python_weather
import sys
import socket

# Σειριακή σύνδεση με timeout
arduino = serial.Serial('COM5', 9600, timeout=1.5)
time.sleep(2)  # Περιμένουμε 2 δευτερόλεπτα για να σταθεροποιηθεί η σύνδεση

# Πaιrnoyme to hostname kai thn IP toy ypologist;h
hostname = socket.gethostname()
my_ip = socket.gethostbyname(hostname)
print("IP:", my_ip)

async def get_weather():
    try:
        async with python_weather.Client(unit=python_weather.METRIC) as client:
            weather = await asyncio.wait_for(client.get('Athens, Greece'), timeout=10.0)
            
            wind_dir = getattr(weather, 'wind_direction', None)
            wind_dir_str = getattr(wind_dir, 'name', None) if wind_dir else None
             
            return {
                "temp": f"{weather.temperature:}'C",
                "humidity": f"Hum:{weather.humidity}%",
                "wind": f"{weather.wind_speed}km/h",
                "wind_arrow": get_wind_arrow(wind_dir_str)
            }
            
    except Exception as e:
        print(f"[ERROR] Weather fetch: {str(e)}")
        return None

def get_wind_arrow(direction_str):
    if not direction_str:
        return "N/A"
    
    # Χάρτης για όλες τις πιθανές κατευθύνσεις
    direction_map = {
        'NORTH': 'N',
        'NORTH_NORTHEAST': 'NNE',
        'NORTHEAST': 'NE',
        'EAST_NORTHEAST': 'ENE',
        'EAST': 'E',
        'EAST_SOUTHEAST': 'ESE',
        'SOUTHEAST': 'SE',
        'SOUTH_SOUTHEAST': 'SSE',
        'SOUTH': 'S',
        'SOUTH_SOUTHWEST': 'SSW',
        'SOUTHWEST': 'SW',
        'WEST_SOUTHWEST': 'WSW',
        'WEST': 'W',
        'WEST_NORTHWEST': 'WNW',
        'NORTHWEST': 'NW',
        'NORTH_NORTHWEST': 'NNW'
    }
    
    # Επιστροφή βέλους ή συντομογραφίας
    arrow = direction_map.get(direction_str.upper())
    return arrow if arrow else direction_str.split('_')[0][0] + direction_str.split('_')[-1][0]

def send_to_arduino(data):
    try:
        packet = (
            f"TIME|{data['time']}|"
            f"DATE|{data['date']}|"
            f"TEMP|{data['temp']}|"
            f"HUM|{data['humidity']}|"
            f"WIND|{data['wind']}|"
            f"WIND_ARROW|{data['wind_arrow']}"
        )
        arduino.write(packet.encode() + b'\n')
    except Exception as e:
        print(f"Serial error: {e}", file=sys.stderr)

async def main():
    last_weather = 0
    weather_cache = {
        "temp": "N/A'C",
        "humidity": "N/A%",
        "wind": "N/Akm/h",
        "wind_arrow": "-"
    }

    while True:
        now = datetime.now()
        data = {
            "time": now.strftime("%H:%M:%S"),
            "date": now.strftime("%a %d/%m"),
            **weather_cache
        }

        # Ενημέρωση καιρού κάθε 10 λεπτά
        if time.time() - last_weather > 600:
            try:
                if (weather := await get_weather()):
                    weather_cache.update(weather)
                    last_weather = time.time()
            except Exception as e:
                print(f"Update failed: {e}", file=sys.stderr)

        send_to_arduino(data)
        await asyncio.sleep(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Πρόγραμμα τερματίστηκε χειροκίνητα")
    finally:
        arduino.close()
