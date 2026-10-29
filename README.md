# Delivery-Robot-ELEGOO-Smart-Robot-Car-V4.0-
Personal project, Dec 2025 – Oct 2026.
I used an ELEGOO 4WD smart car kit (Arduino Uno based) to test the vendor firmware on real hardware, characterize its ultrasonic sensor, and prototype a delivery mode.

---
## What is mine and what is not

Most of the firmware in firmware/ is ELEGOO's V4.0 code (see the headers in each file).
My addition is the delivery mode: the ApplicationFunctionSet_Delivery() function and the Delivery_mode entry in ApplicationFunctionSet_xxx0.cpp, plus its call in the main .ino.
Third-party libraries (FastLED, ArduinoJson, etc.) are not included. Get them from the ELEGOO kit download.

## 1. Firmware testing (January 2026)

I tested the firmware that came preloaded on the board and documented 6 defects, with video evidence:

- Left and right turns overshoot (close to 180° instead of about 90°).
- Obstacle avoidance checks left and right every few seconds and turns toward the clear side even when nothing blocks the path.
- The back-up routine when nearly surrounded by obstacles is inefficient.
- The IR remote signal is rarely received on the first button presses.
- The default speed is too fast for small spaces.
- The car does not drive straight in Forward mode (possibly loose screws).

## 2. Ultrasonic sensor characterization (October 2026)

tests/ultrasonic_characterization.py sends the car's own serial command {"N":21,"D1":2,"H":"1"} and logs the distance it returns. I placed a flat target (a book) at 8 known distances, measured with a ruler, and took 20 readings at each. Results are in results/.

| True (cm) | Mean (cm) | Std (cm) | Min–Max | Error (cm) |
|-----------|-----------|----------|---------|------------|
| 10        | 5.75      | 0.44     | 5-6     | -4.25      |
| 20        | 15.85     | 1.93     | 14-22   | -4.15      |
| 30        | 26.15     | 3.15     | 22-31   | -3.85      |
| 50        | 55.70     | 3.79     | 50-62   | +5.70      |
| 75        | 61.05     | 1.50     | 59-65   | -13.95     |
| 100       | 97.05     | 0.22     | 97-98   | -2.95      |
| 150       | 138.85    | 0.49     | 138-140 | -11.15     |
| 200       | 150.00    | 0.00     | 150-150 | -50.00     |

### Results

#### Findings

1. The sensor reads about 4 cm short at 10–30 cm.
2. At 100 and 150 cm it is very precise (σ ≤ 0.5 cm) but still biased.
3. At a true 200 cm, all 20 readings were exactly 150: the output appears to be clipped at 150 cm, not a real −50 cm error.
4. The results at 50 cm and 75 cm are irregular. I suspect my setup (target alignment, nearby objects) more than the sensor. I have not confirmed this.

#### Limitations: 
A single run, one target, distances placed by hand with a ruler.

**Next**: repeat with a fixed jig and a square target, check the sensor driver for a 150 cm limit, and calibrate the short-range offset.

The script was developed with help from an AI assistant (Claude). I ran it, collected the data, and analyzed the results.

## 3. Delivery mode (prototype)

A state machine (idle, move, avoid, arrived, return) that drives forward, avoids obstacles detected by the ultrasonic sensor, treats a fixed driving time as "arrival", then reverses.

**Status**: implemented, not yet validated on the robot. From reviewing the code, I expect these issues:

- The arrival timer is not reset when the mode is entered.
- The state is not reset after a run, so it may only work once per power cycle.
- The return is time-based, so it only approximates the way back.
  
#### Next steps
- Upload the code to the robot and test it.
- Fix the issues above.
- Replace timed turns with gyro-based (MPU6050) heading control.

### Hardware

ELEGOO Smart Robot Car V4.0 kit (4WD, Elegoo UNO, ultrasonic sensor on a servo, line-tracking sensors, MPU6050).
