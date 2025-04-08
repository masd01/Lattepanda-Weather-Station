#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET    -1  
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

String receivedData = "";  
String scrollText = "";
int scrollPos = 128; // Αρχική θέση εκτός οθόνης

void setup() {
    Serial.begin(9600);
    Wire.begin();
    
    if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) { 
        Serial.println(F("OLED initialization failed"));
        for (;;);
    }
    
    display.clearDisplay();
}

void loop() {
    if (Serial.available()) {
        receivedData = Serial.readStringUntil('\n'); 
        
        int splitIndex = receivedData.indexOf("|");
        if (splitIndex != -1) {
            String timeStr = receivedData.substring(0, splitIndex);
            scrollText = receivedData.substring(splitIndex + 1);

            display.fillRect(0, 0, SCREEN_WIDTH, 30, BLACK); // Καθαρισμός μόνο της πρώτης γραμμής

            display.setTextSize(2);  // μέγεθος για την ώρα
            display.setTextColor(WHITE);
            display.setCursor(15, 1);
            display.print(timeStr);
        }
    }

    display.fillRect(0, 30, SCREEN_WIDTH, 40, BLACK); // Καθαρισμός μόνο της δεύτερης γραμμής

    display.setTextSize(2);  // Μέγεθος για το κυλιόμενο κείμενο
    display.setCursor(scrollPos, 33);  // Ευθυγράμμιση για δεύτερη γραμμή
    display.print(scrollText);
    
    display.display();
    
    scrollPos -= 2;  
    if (scrollPos < -((int)scrollText.length() * 12)) {  
        scrollPos = 128;
    }

    delay(50); // Μικρότερο delay για πιο ομαλή ενημέρωση
}