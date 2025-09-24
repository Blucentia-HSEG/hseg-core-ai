#!/usr/bin/env python3
from scripts.train_all_from_final_dataset import train_organizational, load_data

df = load_data('data/hseg_final_dataset.csv')
res = train_organizational(df)
print('Organizational metrics (acc, rmse):', res)
