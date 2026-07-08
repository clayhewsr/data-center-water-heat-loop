import random
import time

print("=" * 45)
print(" DATA CENTER WATER & HEAT LOOP")
print(" SYSTEM CONTROLLER")
print("=" * 45)

while True:

    water_temp = round(random.uniform(17.5, 20.0), 1)
    return_temp = round(random.uniform(27.0, 31.5), 1)
    flow = random.randint(390, 450)

    heat = random.randint(500, 950)

    cpu = random.randint(35, 95)
    gpu = random.randint(40, 98)

    if cpu > 90 or gpu > 90:
        health = "YELLOW"
    else:
        health = "GREEN"

    print(f"\nWater Supply Temp : {water_temp} °C")
    print(f"Return Temp       : {return_temp} °C")
    print(f"Flow Rate         : {flow} GPM")
    print(f"Recovered Heat    : {heat} kW")
    print(f"CPU Load          : {cpu}%")
    print(f"GPU Load          : {gpu}%")
    print(f"System Health     : {health}")

    print("-" * 45)

    time.sleep(2)
