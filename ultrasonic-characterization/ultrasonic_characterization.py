"""
Owner: Maimouna Fall

Characterize the ELEGOO car's ultrasonic sensor (accuracy and precision).

How it works:
  - Sends the car's own serial command  {"N":21,"D1":2,"H":"1"}
    (N21 = ultrasonic module, D1=2 = "return the distance in cm").
  - The car replies with something like  {1_45}  -> 45 cm.
  - For each true distance (measured with a ruler) it takes SAMPLES readings,
    then saves a CSV and draws two plots.

Setup:
  pip install pyserial matplotlib
  Edit PORT below, flash the STOCK firmware (or your build), plug in the USB cable.
"""
import csv
import re
import statistics
import time

import serial  # pyserial
import serial.tools.list_ports

PORT = "COM3"  
BAUD = 9600
DISTANCES_CM = [10, 20, 30, 50, 75, 100, 150, 200]  # true distances, measured with a ruler
SAMPLES = 20      # readings per distance
DELAY_S = 0.1     # pause between readings
COMMAND = b'{"N":21,"D1":2,"H":"1"}'
REPLY = re.compile(rb"_(\d+)\}")


def ask(ser):
    """Send the distance command and return the raw bytes the car answered."""
    ser.reset_input_buffer()
    ser.write(COMMAND)
    return ser.read_until(b"}")


def read_distance(ser):
    """Ask the car for one distance reading (cm). Returns None if no valid reply."""
    match = REPLY.search(ask(ser))
    return int(match.group(1)) if match else None


def check_connection(ser):
    """Try a few times and show the raw reply, so problems are visible immediately."""
    for attempt in range(1, 4):
        raw = ask(ser)
        print(f"  attempt {attempt}: raw reply = {raw!r}")
        if REPLY.search(raw):
            return True
        time.sleep(1)
    return False


def collect(ser):
    rows = []
    for true_cm in DISTANCES_CM:
        input(f"Place a flat target at {true_cm} cm (ruler) and press Enter... ")
        readings = []
        for _ in range(SAMPLES):
            d = read_distance(ser)
            if d is not None:
                readings.append(d)
                print(f"    {d} cm", flush=True)
            else:
                print("    (no reply)", flush=True)
            time.sleep(DELAY_S)
        if len(readings) < 2:
            print("  no valid replies - check PORT, wiring, and the shield's upload switch")
            continue
        mean = statistics.mean(readings)
        rows.append({
            "true_cm": true_cm,
            "n": len(readings),
            "mean_cm": round(mean, 2),
            "std_cm": round(statistics.stdev(readings), 2),
            "min_cm": min(readings),
            "max_cm": max(readings),
            "error_cm": round(mean - true_cm, 2),
        })
        print(f"  mean {rows[-1]['mean_cm']} cm, std {rows[-1]['std_cm']} cm, "
              f"error {rows[-1]['error_cm']} cm")
    return rows


def save_csv(rows, path="ultrasonic_results.csv"):
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Saved {path}")


def plot(rows, path="ultrasonic_results.png"):
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not installed - skipping plots (pip install matplotlib)")
        return
    true = [r["true_cm"] for r in rows]
    mean = [r["mean_cm"] for r in rows]
    std = [r["std_cm"] for r in rows]
    err = [r["error_cm"] for r in rows]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
    ax1.errorbar(true, mean, yerr=std, fmt="o-", capsize=3, label="measured (mean ± std)")
    ax1.plot(true, true, "--", label="ideal")
    ax1.set_xlabel("True distance (cm)")
    ax1.set_ylabel("Sensor reading (cm)")
    ax1.legend()
    ax1.grid(True)

    ax2.bar([str(t) for t in true], err)
    ax2.axhline(0, color="black", linewidth=0.8)
    ax2.set_xlabel("True distance (cm)")
    ax2.set_ylabel("Error (cm)")
    ax2.grid(True, axis="y")

    fig.tight_layout()
    fig.savefig(path, dpi=150)
    print(f"Saved {path}")


def main():
    print("Serial ports found:")
    for port in serial.tools.list_ports.comports():
        print(f"  {port.device}: {port.description}")
    print(f"Using PORT = {PORT}\n")

    try:
        ser = serial.Serial(PORT, BAUD, timeout=1)
    except serial.SerialException as exc:
        print(f"Could not open {PORT}: {exc}")
        print("Check the port name above, and close the Arduino IDE / Serial Monitor.")
        return

    time.sleep(3)  # the Uno resets when the serial port is opened
    try:
        print("Checking the connection...")
        if not check_connection(ser):
            print("\nThe car did not answer. Check:")
            print("  1. PORT matches the list above (the one that appears when you plug in USB)")
            print("  2. Arduino IDE and its Serial Monitor are closed")
            print("  3. The switch on the shield is on 'Upload' (not 'Cam')")
            print("  4. The car's battery switch is ON (wheels lifted)")
            print("  5. Try the command by hand in the Arduino Serial Monitor (9600 baud)")
            return
        print("Connection OK.\n")
        rows = collect(ser)
    finally:
        ser.close()
    if rows:
        save_csv(rows)
        plot(rows)


if __name__ == "__main__":
    main()
