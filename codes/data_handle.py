"""
导入数据 并 进行数据处理
"""
import numpy as np
import pandas as pd
import datetime


class GetData():
    """获取 复权后的期货 & 指数数据"""
    def __init__(self, future='IC', time_frequency=240) -> None:
        index_future_code = {'IC':'000905.SH','IF':'000300.SH','IH':'000016.SH'}
        self.future = future
        self.index = index_future_code[future]
        self.time_frequency = time_frequency
        self.read_option_data()

    def __str__(self) -> str:
        param_list = ['future', 'time_frequency']
        value = [(name, getattr(self, name)) for name in param_list]
        f_string = ''
        for i, (item, count) in enumerate(value):
            f_string += (f'#{i+1}: '
                         f'{item.title():<10s} = '
                         f'{count}\n')
        return f_string
    
    def read_option_data(self):
        if self.time_frequency < 240:
            self.factor_data = pd.read_csv(f'data\{self.future}_info.csv', header=0, index_col=0)[['date', 'factor']]
            self.future_data = pd.read_csv(f'data\{self.future}_1_min.csv', header=0, index_col=0)
            self.future_data = transfer_timeFreq(self.future_data, self.time_frequency, ic_multiplier=200)
        elif self.time_frequency == 240:
            self.future_data = pd.read_csv(f'data\{self.future}_info.csv', header=0, index_col=0)
            pass # self.future_data = self.factor_data
        

    def get_index_data(self):
        self.index_data = pd.read_csv(f'data\{self.index}.csv', header = 0)
        self.index_data.rename(columns={'20100104':'date'}, inplace=True)
        return self.index_data

    @staticmethod
    def get_date_time(data, col='date', time_frequency=240):
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
            return data.apply(lambda x:datetime.datetime.strptime(str(int(x[col]))\
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
        if self.time_frequency < 240:
            self.data = pd.merge(self.future_data, self.factor_data, on='date')
        elif self.time_frequency == 240:
            self.data = self.future_data
        # 复权
        col_list = ['high','low','open','close']
        print(self.data.columns)
        for i in col_list:
            self.data['r_'+ i] = np.multiply(self.data[i], self.data['factor'])
        return self.data

    def get_refactor_option_data(self):
        self.future_data['date_time'] = self.get_date_time(self.future_data) # 计算因子需要
        option_data = self.get_refactor_price()
        return option_data

class MergeSingleStocks():
    """ 整合沪港通、深港通的所有成分股的 成交额、交易量、 股票收盘价数据"""
    def __init__(self, start_dt=20170101, end_dt=20210101) -> None:
        """
        Args:
            start_dt (int): 研究时间起点 eg: 20170101
            end_dt (int): 研究时间终点 eg: 20210101
        
        Attribute:
            price_data (dataframe): 股票收盘价
            amount_data (dataframe): 成交额数据
            oi_data (dataframe): 北向交易量数据
        """
        self.price_data = pd.read_csv('data/close.csv', header = 0)
        self.amount_data = pd.read_csv('data/amount.csv', header = 0)
        self.oi_data = pd.read_csv('data/northway/North_Quantity.csv', header = 0)
        self.oi_data.rename(columns={'TRADE_DT':'date'}, inplace=True)
        self.oi_data['date'] = self.oi_data['date'].apply(lambda x: int(x.split('/')[0]+x.split('/')[1].zfill(2)+x.split('/')[2].zfill(2)) )
        self.cut_period(start_dt, end_dt)
        self.start_dt = start_dt
        self.end_dt = end_dt
        
    def cut_period(self, start_dt, end_dt):
        # 数据时间截取 为 start_dt 和 end_dt 之间
        # return data[(data['date']<int(end_dt)) & (data['date']>int(start_dt))]
        self.price_data = self.price_data[(self.price_data['date']<int(end_dt)) & 
                                            (self.price_data['date']>int(start_dt))]
        self.amount_data = self.amount_data[(self.amount_data['date']<int(end_dt)) & 
                                            (self.amount_data['date']>int(start_dt))]
        self.oi_data = self.oi_data[(self.oi_data['date']<int(end_dt)) & (self.oi_data['date']>int(start_dt))]
    
    @staticmethod
    def stack_data(data, col_name, idx_name='date'):
        data = data.set_index(idx_name)
        data = data.stack()
        data.name = col_name
        data = data.reset_index() #去掉所有索引
        return data

    def merge_stock_info(self):
        ## 将 价、量、额、成分股 数据整合在一起 ===>计算因子值
        self.price_data = self.stack_data(self.price_data, col_name='close')
        self.amount_data = self.stack_data(self.amount_data, col_name='amount')
        self.oi_data = self.stack_data(self.oi_data, col_name='oi')

        # 价量 整合
        data = pd.merge(self.oi_data, self.price_data, on=['date','level_1'], how='outer')
        # 和 额 整合
        data = pd.merge(data, self.amount_data, on=['date','level_1'], how='outer')
        data.rename(columns={'level_1':'code'}, inplace=True)
        return data

    def find_index_conponent(self, data, index_data):
        # 再筛选 股指成分股
        index_data = self.stack_data(index_data, col_name='code')
        index_data.drop(['level_1'],axis=1, inplace=True)

        index_data = index_data[(index_data['date']<self.end_dt) & (index_data['date']>self.start_dt)]
        index_data['is_in_index'] = 1
        # merge 只留下是index成分股的股票消息
        data = pd.merge(data, index_data, on=['date','code'], how='right') 
        return data

    def fillna(self, data):
        """ 处理数据缺失问题 """
        # 港交所休息（而内地交易所正常交易）导致的交易量缺失
        null_num = data[data.oi.isnull()]['date'].value_counts()
        null_day = list(null_num[null_num==50].index)
        data.drop(data[data.date.isin(null_day)].index , inplace=True)
        print('港交所休息（而内地交易所正常交易）的日期：', null_day)
        # 其他数据缺失：按前值填充
        data.fillna(method='ffill', inplace=True)
        return data

    def get_index_component_info(self, index_data):
        data = self.merge_stock_info()
        data = self.find_index_conponent(data, index_data)
        data = self.fillna(data)
        
        return data
    

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


if __name__ == '__main__': 
    d = GetData(future='IC', time_frequency=240)
    index_data = d.get_index_data()

    start_dt = 20170101
    end_dt = 20210617
    m = MergeSingleStocks(start_dt, end_dt)
    data = m.get_index_component_info(index_data)
    print(data)