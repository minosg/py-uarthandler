/* Simple Serial Echo Code that reads string lines and echos
   back on the same uart. The target platform is Atmel arduino compatible
   microcontrollers */

String line;

void setup()
{
  /* start serial port at 115200 bps */
  Serial.begin(115200);
  /* Block untill serial is read (Leonardo compatible boards) */
  while (!Serial) {;}
}

void loop()
{
  // Check for incoming data
  if (Serial.available() > 0) {

    /* get incoming line: */
    line = Serial.readStringUntil('\n');
    Serial.print(line+"\n");
}
}


