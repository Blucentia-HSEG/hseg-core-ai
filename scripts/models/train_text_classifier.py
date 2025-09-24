#!/usr/bin/env python3
from scripts.train_all_from_final_dataset import train_text, load_data

df = load_data('data/hseg_final_dataset.csv')
acc = train_text(df)
print('Text classifier accuracy:', acc)
