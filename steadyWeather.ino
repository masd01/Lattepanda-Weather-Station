#include <Wire.h>
#include <Adafruit_SSD1306.h>
#include <Adafruit_GFX.h>

// Ρυθμίσεις OLED
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_ADDR 0x3C  // Διεύθυνση I2C

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire);

// Δομή για τα δεδομένα από το Python
struct DisplayData {
  String time;
  String date;
  String temp;
  String humidity;
  String wind;
  String wind_arrow;
};

DisplayData receivedData;

void setup() {
  Serial.begin(9600);  // Σειριακή επικοινωνία με Python
  Wire.begin();        // I2C για OLED
  
  // Εκκίνηση οθόνης
  if (!display.begin(SSD1306_SWITCHCAPVCC, OLED_ADDR)) {
    Serial.println("SSD1306 initialization failed!");
    while (1);  // Ατέρμονα βρόχος αν αποτύχει
  }
  
  display.clearDisplay();
  display.setTextColor(SSD1306_WHITE);
  display.setTextSize(1);
  display.display();
  Serial.println("OLED Ready!");
}

// Αναδιάρθρωση δεδομένων από το Python (μορφή: "TIME|12:34|DATE|15 Apr|TEMP|25°C|...")
void parseData(String input) {
  int pos = 0;
  while ((pos = input.indexOf('|')) != -1) {
    String key = input.substring(0, pos);
    input = input.substring(pos + 1);
    
    pos = input.indexOf('|');
    if (pos == -1) pos = input.length();
    String value = input.substring(0, pos);
    
    if (key == "TIME") receivedData.time = value;
    else if (key == "DATE") receivedData.date = value;
    else if (key == "TEMP") receivedData.temp = value;
    else if (key == "HUM") receivedData.humidity = value;
    else if (key == "WIND") receivedData.wind = value;
    else if (key == "WIND_ARROW") receivedData.wind_arrow = value;
    
    if (pos != input.length()) input = input.substring(pos + 1);
  }
}

// Σχεδίαση στην OLED
void drawDisplay() {
  display.clearDisplay();
  
  // Χρόνος (μεγάλη γραμματοσειρά)
  display.setCursor(10, 0);
  display.setTextSize(2);
  display.println(receivedData.time);
  
  // Ημερομηνία
  //display.setTextSize(1);
  display.setCursor(0, 18);
  display.println(receivedData.date);
  
  // Θερμοκρασία & Υγρασία
  display.setCursor(0, 35);
  display.print(receivedData.temp);
  display.print(" ");
  display.setTextSize(1);
  display.print(receivedData.humidity);
  
  // Άνεμος
  display.setCursor(0, 50);
  display.print("Wind: ");
  display.print(receivedData.wind);
  display.print(" ");
  display.print(receivedData.wind_arrow);
  
  display.display();
}

void loop() {
  if (Serial.available()) {
    String data = Serial.readStringUntil('\n');
    parseData(data);
    drawDisplay();
  }
  delay(100);  // Μικρή καθυστέρηση για σταθερότητα
}
