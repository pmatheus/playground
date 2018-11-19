from gym.envs.registration import register

register(
    id = 'Binance-v0',
    entry_point = 'gym_playground.envs:BinanceEnv',
)