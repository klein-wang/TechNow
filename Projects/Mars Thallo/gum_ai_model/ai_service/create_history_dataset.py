import pandas as pd
import numpy as np
import datetime
import os
import json


df_history = pd.read_csv('combined_data2.csv')

time_start = datetime.datetime(2024, 5, 28, 0, 0)
time_end = datetime.datetime(2024, 6, 27, 23, 59)

row_number = 0
t = time_start
while t <= time_end:

    while datetime.datetime.strptime(df_history['Date'][row_number], '%Y-%m-%d %H:%M:%S') < t:
        row_number += 1

    row_number -= 1

    initial_x = {
        'Item': df_history['Item'][row_number],
        'Sugar': df_history['Sugar'][row_number],
        'entry_type': int(df_history['entry_type'][row_number]),
        'batch': int(df_history['batch'][row_number]),
        'Weight': float(df_history['Weight'][row_number]),
        'big_roller_speed': float(df_history['大辊速度'][row_number]),
        '1_roller_speed': float(df_history['1号辊轮速度'][row_number]),
        '1_roller_gap': float(df_history['1号辊间隙'][row_number]),
        '2_roller_speed': float(df_history['2号辊轮速度'][row_number]),
        '2_roller_gap': float(df_history['2号辊间隙'][row_number]),
        '3_roller_speed': float(df_history['3号辊轮速度'][row_number]),
        '3_roller_gap': float(df_history['3号辊间隙'][row_number]),
        'forming_roller_speed': float(df_history['Forming Roller 辊轮速度'][row_number]),
        'forming_roller_gap': float(df_history['Forming Roller 定型辊间隙'][row_number]),
        '1_cooling_roller_temperature': float(df_history['1号冷辊入口温度'][row_number]),
        '2_cooling_roller_temperature': float(df_history['2号冷辊入口温度'][row_number]),
        'mapping_time': df_history['Date'][row_number]
    }

    file_path = '''History_Data/%s/%s/%s/%s/%s/initial_x.json''' % (
        str(t.year), str(t.month), str(t.day), str(t.hour), str(t.minute)
    )

    directory = os.path.dirname(file_path)

    # Check if the directory exists, if not, create it
    if not os.path.exists(directory):
        os.makedirs(directory)

    with open(file_path, 'w') as json_file:
        json.dump(initial_x, json_file, indent=4)

    t += datetime.timedelta(minutes=1)
