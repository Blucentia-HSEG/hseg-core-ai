#!/usr/bin/env python3
from scripts.train_all_from_final_dataset import train_individual, load_data

df = load_data('data/hseg_final_dataset.csv')
metrics = train_individual(df)
print('Individual training metrics:', metrics)
