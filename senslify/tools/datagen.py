import random

SENSOR_LOWER = 0
SENSOR_UPPER = 100

GROUP_LOWER = 0
GROUP_UPPER = 100

RTYPES = [
    (0, 0, 100), # TEMPERATURE
    (1, 0, 100), # HUMIDITY
    (2, 0, 5000), # VISIBLE LIGHT
    (3, 0, 10000), # INFRARED LIGHT
    (4, 0, 240)  # VOLTAGE
]

def gen_reading(sensorids=(SENSOR_LOWER, SENSOR_UPPER),
                groupids=(GROUP_LOWER, GROUP_UPPER),
                rtypes=RTYPES):
    pass

