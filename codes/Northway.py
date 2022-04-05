'''
参考研报：《开源量化评论30：北上资金：识别真正的强流入_金工研究团队_20210819》
'''
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from data_handle import *


# 计算因子 北向资金的增量
def get_factor(price_data,amount_data,oi_data,north_buy_sell,index_data,future_data,
             start_dt, end_dt):
    """ 求北向因子： factor = 对所有成分股 Σ[( OIt - OI(t-1) ) *Pt]
        其中OI为沪港通、深港通的单个股票交易量数据，P为股票收盘价

    Args:
        price_data (dataframe): 股票收盘价
        amount_data (dataframe): 成交额数据
        oi_data (dataframe): 北向交易量数据
        north_buy_sell (dataframe): _description_
        index_data (dataframe): 指数数据
        future_data (dataframe): 复权后的日度期货数据
        start_dt (str): 研究时间起点 eg: '20170101'
        end_dt (str): 研究时间终点 eg: '20170101'

    Returns:
        dataframe: 因子数据['date','factor']
    """
    # 数据时间截取 为 start_dt 和 end_dt 之间
    price_data = price_data[(price_data['date']<int(end_dt))&(price_data['date']>int(start_dt))]
    amount_data = amount_data[(amount_data['date']<int(end_dt))&(amount_data['date']>int(start_dt))]
    oi_data['TRADE_DT'] = oi_data['TRADE_DT'].apply(lambda x: int(x.split('/')[0]+x.split('/')[1].zfill(2)+x.split('/')[2].zfill(2)) )
    oi_data = oi_data[(oi_data['TRADE_DT']<int(end_dt))&(oi_data['TRADE_DT']>int(start_dt))]
    oi_data = oi_data.set_index('TRADE_DT')
    
    ## 将 价、量、额、成分股 数据整合在一起 ===>计算因子值
    price_data = price_data.set_index('date')
    price_data = price_data.stack()
    price_data.name = 'close'
    price_data = price_data.reset_index() #去掉所有索引

    amount_data = amount_data.set_index('date')
    amount_data = amount_data.stack()
    amount_data.name = 'amount'
    amount_data = amount_data.reset_index() #去掉所有索引

    oi_data = oi_data.stack()   
    oi_data.name = 'oi' #'delta_oi'         
    oi_data = oi_data.reset_index() #去掉所有索引
    oi_data.rename(columns={'TRADE_DT':'date'}, inplace=True)

    # 价量 整合
    data = pd.merge(oi_data, price_data, on=['date','level_1'], how='outer')
    # 和 额 整合
    data = pd.merge(data, amount_data, on=['date','level_1'], how='outer')
    data.rename(columns={'level_1':'code'}, inplace=True)
    
    # 再筛选 股指成分股
    index_data = index_data.set_index('20100104')
    index_data = index_data.stack()
    index_data.name = 'code'
    index_data = index_data.reset_index()
    index_data.drop(['level_1'],axis=1, inplace=True)
    index_data.rename(columns={'20100104':'date'}, inplace=True)
    index_data = index_data[(index_data['date']<int(end_dt))&(index_data['date']>int(start_dt))]
    index_data['is_in_index'] = 1
    data = pd.merge(data, index_data, on=['date','code'], how='right')
    
    ### 处理数据缺失问题
    # 港交所不交易导致的交易量缺失
    null_num = data[data.oi.isnull()]['date'].value_counts()
    null_day = list(null_num[null_num==50].index)
    data.drop( data[data.date.isin(null_day)].index , inplace=True)
    print(null_day)
    # 其他数据缺失：按前值填充
    print('='*8)
    print('按前值填充的缺失数据：', data[data.oi.isnull()] )
    data.fillna(method='ffill', inplace=True)

    ### 计算因子值：factor = 对所有成分股 Σ[(OIt - OI(t-1))*Pt] / Σ[amount(t)]
    #data['delta_oi'] = data['oi'].diff()
    data = data.set_index(['date','code','close','amount'])
    data = data.groupby(['code'])['oi'].diff()
    data.name = 'delta_oi'
    data = data.reset_index()
    # 第一天的dalta，以及新纳入股票的第一天的delta会是空值，此处以 0 填充
    data.fillna(0, inplace=True)
    
    # 按 date groupby
    grouped = data.groupby(['date'])
    factor_data = grouped.apply(lambda x: np.divide( np.multiply(x['delta_oi'],x['close']).sum(), x['amount'].sum()) )
    factor_data.name = 'factor'
    factor_data = factor_data.reset_index()
    
    data_factor = pd.merge(factor_data, future_data, on='date', how='left')
    # 加上北向的买入、卖出金额数据
    data_factor = pd.merge(data_factor, north_buy_sell[['date_time','buy','sell']], on='date_time', how='left')
    data_factor['inflow_tense'] = data_factor['factor']/(data_factor['buy']+data_factor['sell'])
    
    print(list(data_factor[(data_factor['inflow_tense'].isnull())]['date']))
    return data_factor


def get_trading_sig(data_factor,s1=60,s_1=-40): 
    """计算买卖信号

    Args:
        data_factor (dateframe): 因子数据（字段['factor']）
        s1 (int, optional): 因子阈值. Defaults to 60.
        s_1 (int, optional): 因子阈值. Defaults to -40.

    Returns:
        _type_: _description_
    """
    # 北向因子>0，买入；北向因子<0，卖出
    data_factor['pre_factor'] = data_factor['factor'].shift(1).fillna(0)
    # 买入信号=1，卖出信号=-1
    data_factor['sig'] = data_factor.apply(lambda x:1 if (x['factor']>s1 ) else( #and x['pre_factor']<s1
                                        -1 if (x['factor']<s_1 ) else 0), axis=1) #and x['pre_factor']>s_1

    data_factor.drop(['pre_factor'], axis=1, inplace=True)
    data_factor = adjust_trading_sig(data_factor)
    return data_factor


def get_trading_sig_M(data_factor,s1=10,s_1=-0,s2=0.03,s_2=-0.02):
    """计算买卖信号

    Args:
        data_factor (dateframe): 因子数据（字段['factor']）
        s1 (int, optional): 因子阈值. Defaults to 10.
        s_1 (int, optional): 因子阈值. Defaults to -0.
        s2 (float, optional): 因子阈值. Defaults to 0.03.
        s_2 (float, optional): 因子阈值. Defaults to -0.02.

    Returns:
        dateframe: 信号数据（字段['factor','sig']）
    """
    # 北向因子>0，买入；北向因子<0，卖出
    #data_factor['pre_inflow'] = data_factor['inflow_tense'].shift(1).fillna(0)
    #data_factor['pre_factor'] = data_factor['factor'].shift(1).fillna(0)
    # 买入信号=1，卖出信号=-1
    data_factor['sig'] = data_factor.apply(lambda x:1 if (x['factor']>s1 and x['inflow_tense']>s2)
                                        else(-1 if (x['factor']<s_1 and x['inflow_tense']<s_2) else 0), axis=1)
    #data_factor.drop(['pre_factor'], axis=1, inplace=True)
    data_factor = adjust_trading_sig(data_factor)
    return data_factor


if __name__ == '__main__':    
    # 定义策略中需要用到的参数
    start_dt = '20170101' 
    end_dt = '20210617'
    index_future_code = {'IC':'000905.SH','IF':'000300.SH','IH':'000016.SH'}
    future_code = 'IF'; index_code = index_future_code[future_code]

    s = 0 # 策略 阈值

    allocation = 10000000 # 策略初始资金一千万

    
