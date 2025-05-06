# utils/data_loader.py
import pandas as pd

def load_basic_info(path):
    df = pd.read_csv(path)
    return df
