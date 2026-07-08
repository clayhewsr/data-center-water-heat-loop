import random
import time

print("====================================")
print(" HEAT RECOVERY SIMULATOR ")
print("====================================")

while True:
    compute_load = random.randint(60, 98)
    heat_captured_kw = random.randint(450, 950)
    storage_level = random.randint(40, 100)
    heat_reuse_demand = random.choice(["LOW", "MEDIUM", "HIGH"])

    print()
    print(f"Compute Load        : {compute_load}%")
    print(f"Heat Captured       : {heat_captured_kw} kW")
    print(f"Thermal Storage     : {storage_level}%")
    print(f"Heat Reuse Demand   : {heat_reuse_demand}")

    if heat_captured_kw > 800 and storage_level > 85:
        print("Status              : READY FOR HEAT DELIVERY")
    elif heat_captured_kw > 600:
        print("Status              : HEAT RECOVERY ACTIVE")
    else:
        print("Status              : MONITORING")

    print("------------------------------------")
    time.sleep(2)
