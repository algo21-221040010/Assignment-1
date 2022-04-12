# Assignment 2
## Brief Introduction
This is the repository for assignment 2, which follows the work of a research paper by ***Kaiyuan securities***. More information about this research paper can be found at 'research_paper' folder.

## What is Included
There are 3 folders in this repository
- 1. **'codes'** folder contains all of our code implementations, they are:
  - **'data_handle.py'** which helps to read in data and process data.
  - **'signal_handle.py'** which contains how to process signals and mark the signals in pictures which can be found in the 'data\result_data' folder.
  - **'Northway.py'** which calculates the factor ***Northway***, and the trading signal. 
  - **'main.py'** , run this file and you can get the trading signal of our strategy.
- 2. **'research_paper'** contains the pdf file of this paper.
- 3. **'data'** folder contains:
  - input data.
  - result pictures.
  
![trading signal](data\trading_signal.png)

## how to calculate *Northway Factor* ?
 $factor = Σ[( OI_t - OI_{t-1} ) *P_t]$ 
 (Summation of all underlying stock in the stock index)

## backtest result
### 1) IH
- parameter: (60,-50)
- backtest result
![策略净值图](data\Northway-Ver2(60,-50)_IH_all_strategy_netValue.png)


|      | annualized rate of return   | annualized volatility   | annualized rate of return of underlying asset   | excess rate of return  |   Sharpe |   Maximum DrawDown |   winning rate |   profit and coss ratio |   
|:-------|:-------------|:-------------|:---------------|:-------------|---------:|-----------:|-------:|---------:|---------------:|
| Total     | 14.23%       | 10.86%       | 14.66%         | -0.43%       |     1.31 |      -0.11 |   0.74 |    -1.45 |  

#### 2) IF
- parameter: (60,-50)
- backtest result
![策略净值图](data\Northway-Ver2(60,-50)_IF_all_strategy_netValue.png)

|      | annualized rate of return   | annualized volatility   | annualized rate of return of underlying asset   | excess rate of return  |   Sharpe |   Maximum DrawDown |   winning rate |   profit and coss ratio | 
|---:|:-------|:-------------|:-------------|:---------------|:-------------|---------:|-----------:|-------:|---------:|---------------:|
|  Total     | 12.41%       | 10.97%       | 17.81%         | -5.40%       |     1.13 |      -0.23 |   0.67 |    -1.86 |       

#### 3) IC
- parameter: (300, -40)
- backtest result
![策略净值图](data\Northway-Ver2(300,-40)_IC_all_strategy_netValue.png)

|      | annualized rate of return   | annualized volatility   | annualized rate of return of underlying asset   | excess rate of return  |   Sharpe |   Maximum DrawDown |   winning rate |   profit and coss ratio | 
|---:|:-------|:-------------|:-------------|:---------------|:-------------|---------:|-----------:|-------:|---------:|---------------:|
| Total     | 7.25%        | 16.90%       | 17.37%         | -10.13%      |     0.43 |      -0.36 |   0.61 |    -0.95 |       


## Analysis
It is clear that the Northway factor performs best at IH, then IF, and perform worst at IC.

That is mainly because majority of the northway funds flows to most liquid stocks. The SSE 50  consists of the 50 largest and most liquid A-share stocks listed on Shanghai Stock Exchange, the CSI 300 consists of the top 300 stocks in the Shanghai or Shenzhen Stock Exchanges, while the CSI 500 selects 500 Middle and small stocks after excluding both the CSI 300 Index constituents and the top 300 stocks in SSE, so the net inflow of northway assets works better for the first two.
