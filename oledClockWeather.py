import python_weather
import asyncio
import os
import datetime
import serial
import time
import socket

# Σύνδεση με το Arduino μέσω σειριακής επικοινωνίας
arduino_port = "COM5"  # Άλλαξε το COM αν χρειάζεται
baud_rate = 9600  # Ρυθμός μετάδοσης δεδομένων
ser = serial.Serial(arduino_port, baud_rate, timeout=1)  # Ανοίγουμε τη σειριακή θύρα
time.sleep(2)  # Περιμένουμε 2 δευτερόλεπτα για να σταθεροποιηθεί η σύνδεση

# Παίρνουμε το hostname και την IP του υπολογιστή
hostname = socket.gethostname()
my_ip = socket.gethostbyname(hostname)
print("IP:", my_ip)

# Συνάρτηση για την επιστροφή του κατάλληλου emoji ανάλογα με την περιγραφή του καιρού
def get_weather_emoji(description):
    description = description.lower()
    if "clear" in description:
        return "Clear"  # ☀️
    elif "cloud" in description:
        return "Cloud"  # ☁️
    elif "rain" in description:
        return "Rain"   # 🌧️
    elif "thunderstorm" in description:
        return "Thunder"  # ⛈️
    elif "snow" in description:
        return "Snow"   # ❄️
    elif "fog" in description or "mist" in description:
        return "Fog"    # 🌫️
    return "🌍"  # Επιστρέφουμε "🌍" αν δεν ταιριάζει καμία από τις παραπάνω περιγραφές

# Συνάρτηση για την λήψη των δεδομένων καιρού από το API
async def get_weather():
    try:
        # Σύνδεση με τον client του python_weather
        async with python_weather.Client(unit=python_weather.METRIC) as client:
            weather = await client.get('Athens, Greece')  # Λήψη καιρού για την Αθήνα, Ελλάδα
            emoji = get_weather_emoji(weather.description)  # Λήψη του emoji του καιρού
            # Επιστρέφουμε τις πληροφορίες με τη μορφή: "Emoji Θερμοκρασία, Υγρασία, Άνεμος"
            return f"{emoji} {weather.temperature}'C, {weather.humidity}% Hum, {weather.wind_speed}km/h {weather.wind_direction}"
    except Exception as e:
        # Αν υπάρχει σφάλμα, το εμφανίζουμε και επιστρέφουμε "Weather N/A"
        print("Σφάλμα κατά την ανάκτηση καιρού:", e)
        return "Weather N/A"

# Συνάρτηση για την αποστολή των δεδομένων στην σειριακή θύρα
async def send_data():
    weather_info = await get_weather()  # Αρχική λήψη καιρού
    last_weather_update = time.time()  # Αποθηκεύουμε τον χρόνο της τελευταίας ενημέρωσης του καιρού

    while True:
        now = datetime.datetime.now()  # Παίρνουμε την τρέχουσα ημερομηνία και ώρα
        date_str = now.strftime("%A %d %b %Y")  # Μορφή ημερομηνίας (π.χ. "Τρίτη 10 Απρ 2025")
        time_str = now.strftime("%H:%M:%S")  # Μορφή ώρας (π.χ. "14:25:30")

        # Αν έχουν περάσει 10 λεπτά (600 δευτερόλεπτα), ενημερώνουμε τον καιρό
        if time.time() - last_weather_update >= 600:
            weather_info = await get_weather()
            last_weather_update = time.time()  # Ενημερώνουμε τον χρόνο της τελευταίας ενημέρωσης

        # Δημιουργούμε τα δεδομένα που θα στείλουμε στον Arduino
        data_to_send = f"{time_str}|{date_str}, {weather_info}\n"
        ser.write(data_to_send.encode("utf-8"))  # Στέλνουμε τα δεδομένα στον Arduino

        # Περιμένουμε μέχρι το επόμενο δευτερόλεπτο για να ξεκινήσει το loop ξανά
        time.sleep(1 - (time.time() % 1))  # Ακριβής συγχρονισμός κάθε δευτερόλεπτο

# Εκκίνηση του προγράμματος
if __name__ == "__main__":
    if os.name == "nt":
        # Ορισμός του event loop σε Windows
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(send_data())  # Εκκίνηση της συνάρτησης αποστολής δεδομένων
