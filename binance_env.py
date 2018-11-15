import numpy as np
import pandas as pd
from abc import abstractmethod

from gym import error
from gym import logger

from gym.envs.playground.spaces.action import ActionSpace
from gym.envs.playground.spaces.observation import ObservationSpace
from gym.envs.playground.utils.data_loader import DataLoader

class BinanceEnv(gym.Env):
# Some constants
MSEC = 1000
MINUTE = 60 * MSEC

    def __init__(self):
        super(BinanceEnv, self).__init__()
        data_path = ""
        exchange = "binance"
        self.data = None
        self.action_space = ActionSpace()
        self.observation_space = ObservationSpace()
        self.buy, self.sell = 0
        self.timesteps = 0
        self.total_reward = 0.0
        self.logger = logger
        self.current_timestamp = None
        self.max_timestamp = None
        self.current_state = {}

    def _get_state(self):
        if(self.data):
            
            self.current_state = self.data[self.data["Timestamp"] == self.current_timestamp]

    def _load_data(self):
        if not self.generator: 
            data_loader = DataLoader(data_path,exchange)
            self.data = data_loader.data
            self.current_timestamp = self.data['Timestamp'].min()
            self.max_timestamp = self.data['Timestamp'].max()
    
    def reset(self):
        self.data = None
        self.action_space = ActionSpace()
        self.observation_space = ObservationSpace()
        self.buy, self.sell = 0
        self.timesteps = 0
        self.total_reward = 0.0
        self.logger = logger
        self.current_timestamp = None
        self.max_timestamp = None
        self.current_state = {}

    def step(self, action):
        state = self._get_new_state()
        reward = self._take_action(action)
        self.timesteps += 1
        self.total_reward += reward
        
        message = "Timestep {}:==: Action: {} ; Reward: {}".format(
            self.timesteps, CryptoEnv.action_space.lookup[action], reward
        )
        self.logger.debug(message)
        
        if self.current_timestamp < self.max_timestamp:
            self.current_timestamp += MINUTE
            return state, reward, False, {"Finished?":"No"}
        else:
            return state, reward, True, {"Finished?":"Yes"}

    def _get_next_state(self):
        self.data[self.data["Timestamp"] == self.current_timestamp + MINUTE]
    
    def _take_action(self, action):
        if this.action_space.lookup[action] is "Buy":
            self.buy += 1
        elif this.action_space.lookup[action] is "Sell":
            self.sell += 1
        return _simple_pnl_reward()
        #return _weighted_pnl_reward()
    def _simple_pnl_reward(self):
        reward = 1.0
        return reward

    def _weighted_pnl_reward(self):
        reward = 1*0.5
        return reward