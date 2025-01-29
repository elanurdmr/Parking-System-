int redPin = 9;    
int greenPin = 10;  
int bluePin = 11;   

void setup() {
  // LED pinleri çıkışı
  pinMode(redPin, OUTPUT);
  pinMode(greenPin, OUTPUT);
  pinMode(bluePin, OUTPUT);
  
  // Seri haberleşme
  Serial.begin(9600);
}

void loop() {
  if (Serial.available() > 0) {
    char received = Serial.read();  // Python'dan gelen veriyi okuma

    // Gelen veriye göre LED renklerini ayarlama
    if (received == 'G') {
      // Yeşil LED
      digitalWrite(redPin, HIGH);  // Kırmızı LED kapalı
      digitalWrite(greenPin, LOW); // Yeşil LED açık
      digitalWrite(bluePin, HIGH); // Mavi LED kapalı
    } else if (received == 'B') {
      // Mavi LED
      digitalWrite(redPin, HIGH);  // Kırmızı LED kapalı
      digitalWrite(greenPin, HIGH); // Yeşil LED kapalı
      digitalWrite(bluePin, LOW);  // Mavi LED açık
    } else if (received == 'R') {
      // Kırmızı LED
      digitalWrite(redPin, LOW);   // Kırmızı LED açık
      digitalWrite(greenPin, HIGH); // Yeşil LED kapalı
      digitalWrite(bluePin, HIGH); // Mavi LED kapalı
    } else if (received == 'O') {
      // LED kapalı
      digitalWrite(redPin, HIGH);  // Kırmızı LED kapalı
      digitalWrite(greenPin, HIGH); // Yeşil LED kapalı
      digitalWrite(bluePin, HIGH); // Mavi LED kapalı
    }
  }
}
