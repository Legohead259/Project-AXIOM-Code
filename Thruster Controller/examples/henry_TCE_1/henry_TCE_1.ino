
#define PITCH_DIR_PIN 5
#define PITCH_STEP_PIN 9
#define PITCH_EN_PIN 13

#define YAW_DIR_PIN 6
#define YAW_STEP_PIN 7

#define ESC_POT_PIN A2
#define ESC_SPEED_PIN 9
#define ESC_IDLE 1500

#define ARM_PIN 2

#define THRESHOLD 128
bool armed = false;

void arm_isr() {
    armed = !armed;
}

void setup() {
    Serial.begin(115200);
   
    pinMode(PITCH_DIR_PIN, OUTPUT);
    pinMode(PITCH_STEP_PIN, OUTPUT);
  
    pinMode(YAW_DIR_PIN, OUTPUT);
    pinMode(YAW_STEP_PIN, OUTPUT);
    pinMode(ARM_PIN, INPUT_PULLUP);
    pinMode(ESC_POT_PIN, INPUT);
    pinMode(ESC_SPEED_PIN, OUTPUT);
    pinMode(PITCH_EN_PIN, OUTPUT);

    ESC.attach(ESC_SPEED_PIN);
    ESC.writeMicroseconds(ESC_IDLE); // send "stop" signal to ESC.

    attachInterrupt(digitalPinToInterrupt(ARM_PIN), arm_isr, FALLING);
}

void loop() {
//    digitalWrite(LED_BUILTIN, armed); // Use the built-in LED to indicate the vehicle's armed status. ON = ARMED, OFF = DISARMED

    // ===PITCH ACTUATOR CONTROL===   
    int pitch_value = analogRead(JOYSTICK_Y_PIN);
    if (pitch_value > JOYSTICK_IDLE + THRESHOLD && armed) { // Check if the Y-Axis is pushed up and vehicle armed
        moveActuator(PITCH_STEP_PIN, PITCH_DIR_PIN, true); // Extend the pitch actuator
    }
    else if (pitch_value <_______ - THRESHOLD && armed) { // Check if the Y-Axis is pushed down and vehicle armed
        moveActuator(PITCH_STEP_PIN, PITCH_DIR_PIN, false); // Retract the pitch actuator
    }
    Serial.print(pitch_value); Serial.print(", ");

    // ===YAW ACTUATOR CONTROL===
    int yaw_value = analogRead(_____);
    if (yaw_value > JOYSTICK_IDLE + THRESHOLD && armed) { // Check if the X-Axis is pushed left and vehicle armed
        moveActuator(YAW_STEP_PIN, YAW_DIR_PIN, true); // Extend the yaw actuator
    }
    else if (yaw_value < ______ - THRESHOLD && armed) { // Check if the X-Axis is pushed right and vehicle armed
        moveActuator(YAW_STEP_PIN, YAW_DIR_PIN, false); // Retract the yaw actuator
    }
    Serial.print(yaw_value); Serial.print(", ");
    
    // ===MOTOR CONTROL===
    int velocity_value = analogRead(ESC_POT_PIN);
    velocity_value = map(velocity_value, 0, 1023, 1100, 1900); // Convert velocity value from potentiometer to ESC speed
    if ((velocity_value < ESC_IDLE-THRESHOLD || velocity_value > ESC_IDLE+THRESHOLD) && armed) { // Check if velocity potentiometer is outside deadzone and armed
        ESC.writeMicroseconds(velocity_value); // Send PWM signal to ESC
    }
    else {
        ESC.writeMicroseconds(ESC_IDLE); // Send idle PWM signal to ESC
    }
    Serial.println(velocity_value);
}

void moveActuator(uint8_t step_pin, uint8_t dir_pin, bool ext) {
    digitalWrite(dir_pin, ext);
    digitalWrite(step_pin, HIGH);
    delay(2);
    digitalWrite(step_pin, LOW);
    delay(2);
