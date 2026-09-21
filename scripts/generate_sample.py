"""Synthetic historical readings; deterministic and deliberately not live."""
from pathlib import Path
import numpy as np
import pandas as pd

rng = np.random.default_rng(20260921)
frames = []
for number in range(1,4):
    n = 144
    wave = np.sin(np.linspace(0, 5*np.pi,n))
    frame = pd.DataFrame({"timestamp":pd.date_range("2026-09-01",periods=n,freq="10min",tz="UTC").astype(str),
        "turbine_id":f"WT-{number:03d}","wind_speed_mps":(10+2*wave).round(2),
        "rotor_speed_rpm":(14+2*wave).round(2),"generator_temp_c":(72+4*wave).round(2),
        "gearbox_temp_c":(78+4*wave).round(2),"oil_temp_c":(68+5*wave).round(2),
        "vibration_mm_s":(1.8+rng.uniform(0,.5,n)).round(2),
        "power_output_kw":(1600+200*wave).round(2),"blade_pitch_deg":(5+2*wave).round(2),
        "generator_rpm":(1450+100*wave).round(2)})
    if number == 2:
        frame.loc[96:, "gearbox_temp_c"] = np.linspace(85,96,n-96).round(2)
    if number == 3:
        frame.loc[108:, "generator_temp_c"] = np.linspace(82,112,n-108).round(2)
        frame.loc[128:, "vibration_mm_s"] = np.linspace(3,5.2,n-128).round(2)
    frames.append(frame)
target = Path(__file__).resolve().parents[1] / "data/turbine_sensor_samples.csv"
target.parent.mkdir(exist_ok=True)
pd.concat(frames,ignore_index=True).to_csv(target,index=False)
print(target)
