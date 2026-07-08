import random
import time

print("====================================")
print(" WATER LOOP SIMULATOR ")
print("====================================")

while True:
    flow = random.randint(380, 450)
    supply_temp = round(random.uniform(17.5, 20.5), 1)
    return_temp = round(random.uniform(25.0, 31.0), 1)
    tank = random.randint(82, 98)

    print()
    print(f"Flow Rate       : {flow} GPM")
    print(f"Supply Temp     : {supply_temp} °C")
    print(f"Return Temp     : {return_temp} °C")
    print(f"Tank Level      : {tank}%")

    if tank < 85:
        print("Status          : YELLOW")
    else:
        print("Status          : GREEN")

    print("------------------------------------")

    time.sleep(2)
