import random
import time

print("====================================")
print(" PUMP CONTROLLER SIMULATOR ")
print("====================================")

while True:
    flow_rate = random.randint(320, 470)
    pressure = round(random.uniform(35.0, 62.0), 1)
    tank_level = random.randint(70, 100)

    if flow_rate < 360 or pressure < 40:
        pump_speed = "HIGH"
        status = "BOOSTING FLOW"
    elif flow_rate > 440 or pressure > 58:
        pump_speed = "LOW"
        status = "REDUCING FLOW"
    else:
        pump_speed = "NORMAL"
        status = "STABLE"

    print()
    print(f"Flow Rate     : {flow_rate} GPM")
    print(f"Pressure      : {pressure} PSI")
    print(f"Tank Level    : {tank_level}%")
    print(f"Pump Speed    : {pump_speed}")
    print(f"Status        : {status}")
    print("------------------------------------")

    time.sleep(2)
