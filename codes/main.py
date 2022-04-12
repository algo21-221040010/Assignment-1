from data_handle import *
from signal_handle import *
from Northway import *

# 定义策略中需要用到的参数
start_dt = 20170101
end_dt = 20210617
future_code = 'IC'
s1 = 60; s_1 = -40 # 策略 阈值

allocation = 10000000 # 策略初始资金一千万

# 获取数据
# 获取 复权数据
d = GetData(future_code, time_frequency=240)
future_data = d.get_refactor_option_data()
index_data = d.get_index_data()
# 整合沪港通、深港通的所有成分股的 成交额、交易量、 股票收盘价数据
m = MergeSingleStocks(start_dt, end_dt)
data = m.get_index_component_info(index_data)
# 北向总体买卖数据
north_buy_sell = pd.read_excel('data/northway/northway_buy_sell.xlsx',header = 0)

# 获取 因子数据
data_factor = get_factor(data, north_buy_sell, future_data)
print(data_factor)

# 获取 买卖信号数据
data_sig = get_trading_sig(data_factor, s1,s_1)
# data_sig = get_trading_sig_M(data_factor)
print(data_sig)
draw_trade_sig(data_sig, time_freq=240, startdt=20120000, enddt=20220000)