import numpy as np
import pandas as pd
import gym
from gym.utils import seeding
from gym import error
from gym import logger
from gym import spaces
from gym_playground.utils.data_loader import DataLoader
import itertools

# Some constants
MSEC = 1000
MINUTE = 60 * MSEC

class BinanceEnv(gym.Env):



    def __init__(self):
        #super(BinanceEnv, self).__init__()
        
        # Custom Parameters
        self.data_path = "C:\\Users\\uranus\\kage-bushin\\data\\"
        self.exchange = "binance"
        self.pairs = ['BTC/USDT','BNB/BTC','ETH/BTC','IOTA/BTC','XMR/BTC']
        self.init_invest = {'BTC': 1, 'USDT': 1000}
        self.coins = ['BTC', 'BNB', 'ETH', 'IOTA', 'XMR']
        #data
        data_loader = DataLoader(self.data_path, self.exchange, self.pairs)
        self.data = data_loader.data
        self.n_step = len(self.data)
        self.n_pairs = len(self.pairs)

        #instance attributes
        self.cur_step = 0
        self.cur_timestamp = None
        self.currency_owned = {}
        self.currency_price = {}
        self.cash_in_hand = None

        #action space
        self.action_space = spaces.Discrete(3**self.n_pairs)

        #observation space: give estimates in order to sample and build scaler
        currency_max_price = 100000
        currency_range = [[0,100000]]
        price_range = [[0,currency_max_price]]
        cash_in_hand_range = [[0,1000000]]
        self.observation_space = spaces.MultiDiscrete(currency_range + price_range + cash_in_hand_range)

        # seed and start
        self._seed()
        self.reset()

        # Reward
        self.total_reward = 0.0

        # To log actions
        self.logger = logger
    
    def _seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]
    
    def reset(self):
        self.cur_timestamp = self.data['Timestamp'].min()
        self.cur_step = 0
        currency_owned = {}
        for coin in self.coins:
            if coin in self.init_invest:
                currency_owned[coin] = self.init_invest[coin]
            else:
                currency_owned[coin] = 0
        self.currency_owned = currency_owned
        self.currency_price = self._get_currency_price()
        self.cash_in_hand = self.init_invest['USDT']
        return self._get_obs()
    
    def _get_currency_price(self):
        state = self._get_state()
        prices = {}
        for pair in self.pairs:
            pair_state = state[state["Pair"] == pair.replace("/","")]
            if len(pair_state) > 0:
                price = float(pair_state["Close"])
                prices[pair.split("/")[0]] = price
            else:
                prices[pair.split("/")[0]] = 0
        return prices

    def _get_obs(self):
        obs = []
        obs.append(self.currency_owned)
        obs.append(self.currency_price)
        obs.append(self.cash_in_hand)
        return obs

    def _get_val(self):
        val = 0
        for k, v in self.currency_owned.items():
                if k == 'BTC':
                    val += self.currency_owned[k]
                else:
                    val += self.currency_price[k] * v
        return val

    def _trade(self, action):
        #all combo to sell(0), hold(1) or buy(2)
        action_combo = list(map(list, itertools.product([0,1,2], repeat=self.n_pairs)))
        action_vec = action_combo[action]

        #one pass to get sell/buy index
        sell_index = []
        buy_index = []

        for i, a in enumerate(action_vec):
            if a == 0:
                sell_index.append(i)
            elif a == 2:
                buy_index.append(i)
        
        #sell first, then buy
        if sell_index:
            for i in sell_index:
                self._sell(i)
        #TODO: #SECOND STAGE: learn how much to buy of each currency
        if buy_index:
            #allocate btc evenly
            if 0 in buy_index and len(buy_index) >= 2:
                btc_allocation = self.currency_owned['BTC'] / (len(buy_index) - 1)
            else:
                btc_allocation = self.currency_owned['BTC'] / len(buy_index)
            for i in buy_index:
                self._buy(i,btc_allocation)
    
    def _sell(self, i):
        if self.coins[i] == 'BTC':
            self.cash_in_hand = self.currency_price[self.coins[i]] * self.currency_owned[self.coins[i]]
        else:
            self.currency_owned['BTC'] = self.currency_owned[self.coins[i]] * self.currency_price[self.coins[i]]
        self.currency_owned[self.coins[i]] = 0
    
    def _buy(self, i, btc_allocation):
        #TODO: SET TO EXCHANGE MIN BUY
        if self.coins[i] == 'BTC' and self.cash_in_hand > 0 and self.currency_price[self.coins[i]] > 0:
            self.currency_owned[self.coins[i]] = self.cash_in_hand / self.currency_price[self.coins[i]]
            self.cash_in_hand = 0
        elif self.currency_owned['BTC'] > 0 and self.currency_price[self.coins[i]] > 0:
            self.currency_owned[self.coins[i]] = btc_allocation / self.currency_price[self.coins[i]]
            self.currency_owned['BTC'] -= btc_allocation
                 
    def _get_state(self):
            return self.data[self.data["Timestamp"] == self.cur_timestamp]
                
    def step(self, action):
        assert self.action_space.contains(action)
        prev_val = self._get_val()
        self.cur_step += 1
        self.cur_timestamp += MINUTE
        self.currency_price = self._get_currency_price()
        self._trade(action)
        cur_val = self._get_val()
        reward = cur_val - prev_val
        done = self.cur_step == self.n_step - 1
        info = {'cur_val': cur_val}
        
        return self._get_obs(), reward, done, info

        # self.timesteps += 1
        # self.total_reward += reward
        
        # message = "Timestep {}:==: Action: {} ; Reward: {}".format(
        #     self.timesteps, CryptoEnv.action_space.lookup[action], reward
        # )
        # self.logger.debug(message)
        
        # if self.current_timestamp < self.max_timestamp:
        #     self.current_timestamp += MINUTE
        #     return state, reward, False, {"Finished?":"No"}
        # else:
        #     return state, reward, True, {"Finished?":"Yes"}

