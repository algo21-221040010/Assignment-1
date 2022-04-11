"""
导入数据 并 进行数据处理
"""
import numpy as np
import pandas as pd
import datetime


class GetData():
    def __init__(self, future='IC', time_frequency=240, index_data = False) -> None:
        self.future = future
        self.time_frequency = time_frequency
        self.read_data(index_data=index_data)

    def __str__(self) -> str:
        param_list = ['future', 'time_frequency']
        value = [(name, getattr(self, name)) for name in param_list]
        f_string = ''
        for i, (item, count) in enumerate(value):
            f_string += (f'#{i+1}: '
                         f'{item.title():<10s} = '
                         f'{count}\n')
        return f_string
    
    def read_data(self,index_data):
        self.future_data = pd.read_csv('data\IC_1_min.csv', header=0, index_col=0)
        self.factor_data = pd.read_csv('data\IC_info.csv', header=0, index_col=0)[['date', 'factor']]
        if index_data:
            self.index_data = pd.read_csv('data\..csv')

    @staticmethod
    def get_date_time(data, time_frequency=240):
        """获取 datetime类型数据

        Args:
            data (dataframe): 期权行情数据，含字段['date',('time')]
            daily (bool, optional): _description_. Defaults to False.

        Raises:
            TypeError: Unvaild value for "time_frequency"!

        Returns:
            datetime: 一列数据
        """        
        if time_frequency == 240: # 无 'time' 字段
            return data.apply(lambda x:datetime.datetime.strptime(str(int(x['date']))\
                    +' '+str(1500),'%Y%m%d %H%M'), axis=1) 
        elif time_frequency < 240:
            return data.apply(lambda x:datetime.datetime.strptime(str(int(x['date']))\
                    +' '+str(int(x['time']))[:-5],'%Y%m%d %H%M'), axis=1)
        else: 
            raise TypeError('Unvaild value for "time_frequency"!')
    
    # 获取 复权价格数据
    def get_refactor_price(self):
        """获取 复权后的期货数据

        Returns:
            dataframe: 复权后的期货数据 含字段['r_high', 'r_low', 'r_open', 'r_close']
        """        
        self.data = pd.merge(self.future_data, self.factor_data, on='date')
        # 复权
        col_list = ['high','low','open','close']
        for i in col_list:
            self.data['r_'+ i] = np.multiply(self.data[i], self.data['factor'])
        return self.data

    def run(self):
        self.future_data['date_time'] = self.get_date_time(self.future_data) # 计算因子需要
        option_data = self.get_refactor_price()
        return option_data



# 转换数据 时间频率
def transfer_timeFreq(ori_data, time_freq, ic_multiplier=200):
    """转换数据 时间频率

    Args:
        ori_data (dataframe): 原始数据
        time_freq (int): 时间频率（单位：分钟）
        ic_multiplier (int, optional): ic乘数，1份IC合约是200点. Defaults to 200.

    Returns:
        dataframe: 转换时间频率后的数据
    """    
    if time_freq==1:
        return ori_data
    ori_data.reset_index(inplace=True)
    ori_data['flag_data'] = ori_data.groupby(['wind_id','date']).index.rank()-1
    ori_data['flag'] = ori_data['flag_data'].apply(lambda x:x//time_freq)
    grouped = ori_data.groupby(['date','flag'])
    # groupby来调整数据频率
    get_lastday = grouped[['wind_id','time','open']].nth(0)
    max_high = grouped['high'].max()
    min_low = grouped['low'].min()
    last_close = grouped['close','io'].nth(-1)
    get_sum = grouped[['all_volume','all_turnover']].sum()
    # 数据合并
    data_list = [get_lastday, max_high, min_low, last_close, get_sum]
    temp = pd.concat(data_list,axis=1)
    data_newfreq = temp.reset_index()
    data_newfreq['preclose'] = data_newfreq['close'].shift(-1)
    data_newfreq['average_price'] = np.divide(data_newfreq['all_turnover'],
        data_newfreq['all_volume'])/ic_multiplier

    #### 若交易量为 0 （数据缺失或触发了熔断），删除数据
    nan_vloume_date = list(set(data_newfreq[data_newfreq['all_volume']==0].date))
    data_newfreq.drop(data_newfreq[data_newfreq.date.isin(nan_vloume_date)].index , inplace=True)
    # 重设连续index
    data_newfreq.index = (range(data_newfreq.shape[0]))
    # 更新 datetime数据
    data_newfreq['date_time'] = GetData().get_date_time(data_newfreq)
    return data_newfreq

# 调整 sig 数据，假设不持有 空头    
def adjust_trading_sig(data):
    """_summary_

    Args:
        data (dateframe): 因子数据（字段['sig']）

    Raises:
        NameError: there is no signal!

    Returns:
        dateframe: 信号数据（字段['sig','pos']）
    """
    ### 调整多空头: 不考虑空头，保证【多头、空头交错】
    buy_idx = data[ data.sig==1 ].index.tolist()
    sell_idx = data[ data.sig==-1 ].index.tolist()
    if not (buy_idx and sell_idx): # 只要 buy、sell一个为空
        raise NameError('there is no signal!')
    buy_sell_idx = [buy_idx, sell_idx] # 列表嵌套列表

    sig_list = []      
    sig_list.append(buy_sell_idx[0][0])
    i,j = 0,1
    while i<len(buy_sell_idx[0]) and j< len(buy_sell_idx[1])+1:
        # sell_index和 buy相比，大于则纳入sig
        if len(sig_list)%2==1:
            if buy_sell_idx[1][i] > sig_list[-1]:
                sig_list.append(buy_sell_idx[1][i])
                i += 1
            elif buy_sell_idx[1][i] <= sig_list[-1]:
                del buy_sell_idx[1][i]
        # buy_index和 sell相比，大于则纳入sig
        elif len(sig_list)%2==0:
            if buy_sell_idx[0][j]>sig_list[-1]:
                sig_list.append(buy_sell_idx[0][j])
                j += 1
            elif buy_sell_idx[0][j]<=sig_list[-1]:
                del buy_sell_idx[0][j]
        else:
            print('\n','!'*80,'\nsth wrong!!!!!!')

    #print('before #'*8,len(buy_idx), len(sell_idx))
    # 若结果sell/buy有多，截取
    if len(buy_sell_idx[0])<len(buy_sell_idx[1]):
        buy_sell_idx[1] = buy_sell_idx[1][:len(buy_sell_idx[0])]
        print('减去了sell')
    elif len(buy_sell_idx[0])>len(buy_sell_idx[1]):        
        buy_sell_idx[0] = buy_sell_idx[0][:len(buy_sell_idx[1])]
        print('减去了buy')
    print('\n','#--'*8, len(buy_sell_idx[0]), len(buy_sell_idx[1]))
    #print(buy_sell_idx[0], buy_sell_idx[1])

    # 修正 sig 数据
    data['sig'] = 0
    data.loc[buy_sell_idx[0],'sig'] = 1
    data.loc[buy_sell_idx[1],'sig'] = -1
    ### 删除 跨假期交易
    drop_list = take_off_crossHoliday(data)
    print('删除第{}个位置的信号数据，因为这是跨期交易'.format(drop_list))
    k = 0
    for i in drop_list:
        del buy_sell_idx[0][i-k]
        del buy_sell_idx[1][i-k]
        k += 1
    
    # 修正 sig 数据
    data['sig'] = 0
    data.loc[buy_sell_idx[0],'sig'] = 1
    data.loc[buy_sell_idx[1],'sig'] = -1

    # 信号的第二天再真正交易(可能把最后一天的卖shift掉，导致买卖不对称)
    if data['sig'].iloc[-1]==-1 and data['sig'].iloc[-2]!=1:
        data['sig'].iloc[-2]=-1
        print('删了一个')
    elif data['sig'].iloc[-1]==-1 and data['sig'].iloc[-2]==1:
        data['sig'].iloc[-2]=0 # 因为不能同一天买卖，所以这次交易取消
        print('删了一对')
    data['sig'] = data['sig'].shift(1).fillna(0)

    # 求持仓数据
    data['pos'] = np.cumsum(data['sig'])
    return data

def take_off_crossHoliday(data):
    """删除在节假日前一天产生的信号，因为实际交易会延迟到下一交易日（假期后）

    Args:
        data (dateframe): 因子数据（字段['sig','date_time']）

    Returns:
        list: 删除的信号的 位置
    """
    buy_date = list(data[ data.sig==1 ].date_time)

    data = data.copy()
    data['sig'] = data['sig'].shift(1).fillna(0)
    shifted_buydt = list(data[ data.sig==1 ].date_time)
    if len(shifted_buydt)<len(buy_date):
        buy_date.pop()
    
    drop_list = []
    # 如果买入信号生成时刻，和 买入信号执行时刻（即下一期）之间隔有法定假期，则为跨假期交易
    for i in range(len(buy_date)):
        # buy_date 和 shifted_buydt 不在同一日，且二者之间至少间隔 1 天
        if (datetime.datetime.date(shifted_buydt[i])-datetime.datetime.date(buy_date[i])) > datetime.timedelta(days=1):
            drop_list.append(i)
            #print('删除第{}个于{}产生信号{}实际买入的交易，因为是跨假期交易'.format(i, datetime.datetime.date(buy_date[i]), datetime.datetime.date(shifted_buydt[i])) )
    return drop_list


if __name__ == '__main__': 
    d = GetData()
    data = d.run()
    print(data)