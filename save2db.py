#!/usr/bin/env python3
import icm20689
from time import sleep, monotonic
from argparse import ArgumentParser
import sqlite3

def main():
    with icm20689.ICM20689((1, 104)) as imu, sqlite3.connect(args.db) as db:
        imu.accel_sensitivity = getattr(icm20689, f"SENS_{args.asens}G")
        imu.gyro_sensitivity = getattr(icm20689, f"SENS_{args.gsens}DPS")

        db.execute("CREATE TABLE IF NOT EXISTS samples (ts FLOAT NOT NULL, ax FLOAT NOT NULL, ay FLOAT NOT NULL, az FLOAT NOT NULL, gx FLOAT NOT NULL, gy FLOAT NOT NULL, gz FLOAT NOT NULL)")

        print("Start")
        try:
            next_sample = monotonic()
            start = next_sample
            samples = 0
            next_display = monotonic() + 1

            while True:
                while monotonic() < next_sample:
                    pass

                db.execute("INSERT INTO samples (ts, ax, ay, az, gx, gy, gz) VALUES (?, ?, ?, ?, ?, ?, ?)", (monotonic(), *imu.acceleration, *imu.gyroscope))
                samples += 1
                next_sample += 1 / args.samplerate

                if monotonic() > next_display:
                    delta_t = monotonic() - start
                    print(f"samples={samples} time={delta_t}s rate={samples/delta_t}/s")
                    next_display += 3

        except KeyboardInterrupt:
            print(f"Interrupted by user: samples={samples} time={monotonic() - start}")

if __name__ == "__main__":
    p = ArgumentParser()
    p.add_argument('-r', '--samplerate', type=int, default=800, help="Samples per second to record")
    p.add_argument('-a', '--asens', type=int, choices=[2, 4, 8, 16], default=16, help="Accelerometer sensitivity")
    p.add_argument('-g', '--gsens', type=int, choices=[250, 500, 1000, 2000], default=2000, help="Gyroscope sensitivity")
    p.add_argument('db')
    args = p.parse_args()

    main()
