import os
import time
import datetime
import pandas as pd
from gym import logger

class DataLoader:
    
    def __init__(self, data_path, exchange, pairs):
        self.data_path = data_path
        self.exchange = exchange
        self.pairs = pairs
        self.data = None
        self.np_array_data = None
        self._load_data()
    
    def _load_data(self):
        data_files = os.listdir(self.data_path)
        files_to_load = []

        for pair in self.pairs:
            for f in data_files:
                if (pair in f and self.exchange in f):
                    files_to_load.append(f)
        
        data_frames = {}
        for f in files_to_load:
            data_frames[f.replace("-1m.csv","")] = pd.read_csv(self.data_path+f)
            data_frames[f.replace('-1m.csv','')]["Pair"] = f.split("-")[1]

        result = pd.concat(data_frames)
        result = result.sort_values(by=['Timestamp'])
        result = result.reset_index()
        result = result.drop(['level_0','level_1'], axis=1)

        self.data = result