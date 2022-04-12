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
    - result pictures such as picture of trading signal(see below).
  
![trading signal](data\trading_signal.png)

## How to Calculate *Northway Factor*
$factor = Σ[( OI_t - OI_{t-1} ) *P_t]$ 
 (Summation of all underlying stock in the stock index)

## Backtest Result
### 1) IH
- Parameter: (60,-50)
- Backtest Result

    Under this pair of parameter, the strategy performs quite well during 2017.01 - 2021.06. The average annualized rate of return is 14.23%, which excess the average annualized rate of return of the underlying stock index. Meanwhile, the annualized volatility is just 10.86%, with maximum drawdown at 0.11, which indicates the risk and volatility of this strategy is quite low.

![net value of strategy](data\Northway-Ver2(60,-50)_IH_all_strategy_netValue.png)

|      | Annualized Rate of Return   | Annualized Volatility   | Annualized Rate of Return of Underlying Asset   | Excess Rate of Return  |   Sharpe |   Maximum DrawDown |   Winning Rate |   Profit and Coss Ratio |    
|:-------|:-------------|:-------------|:---------------|:-------------|---------:|-----------:|-------:|---------:|---------------:|
| Total     | 14.23%       | 10.86%       | 14.66%         | -0.43%       |     1.31 |      -0.11 |   0.74 |    -1.45 |  

### 2) IF
- Parameter: (60,-50)
- Backtest Result

    Under this pair of parameter, the strategy performs well during 2017.01 - 2021.06. The average annualized rate of return is 12.41%, and the annualized volatility is just 10.97%.

![net value of strategy](data\Northway-Ver2(60,-50)_IF_all_strategy_netValue.png)

|      | Annualized Rate of Return   | Annualized Volatility   | Annualized Rate of Return of Underlying Asset   | Excess Rate of Return  |   Sharpe |   Maximum DrawDown |   Winning Rate |   Profit and Coss Ratio |  
|---:|:-------|:-------------|:-------------|:---------------|:-------------|---------:|-----------:|-------:|---------:|---------------:|
|  Total     | 12.41%       | 10.97%       | 17.81%         | -5.40%       |     1.13 |      -0.23 |   0.67 |    -1.86 |       

### 3) IC
- Parameter: (300, -40)
- Backtest Result

    under this pair of parameter, the average annualized rate of return is 7.25%, and the annualized volatility is 16.90%. 

![net value of strategy](data\Northway-Ver2(300,-40)_IC_all_strategy_netValue.png)

|      | Annualized Rate of Return   | Annualized Volatility   | Annualized Rate of Return of Underlying Asset   | Excess Rate of Return  |   Sharpe |   Maximum DrawDown |   Winning Rate |   Profit and Coss Ratio | 
|---:|:-------|:-------------|:-------------|:---------------|:-------------|---------:|-----------:|-------:|---------:|---------------:|
| Total     | 7.25%        | 16.90%       | 17.37%         | -10.13%      |     0.43 |      -0.36 |   0.61 |    -0.95 |       


## Analysis
It is clear that the Northway factor performs best at IH, then IF, and perform worst at IC.

This is mainly because majority of the northway funds flows to most liquid stocks. The SSE 50 consists of the 50 largest and most liquid A-share stocks, the CSI 300 consists of the top 300 stocks in the Shanghai or Shenzhen Stock Exchanges, while the CSI 500 selects 500 Middle and small stocks after excluding the CSI 300 Index constituents, so the net inflow of northway assets mainly contributes to the first two stock index, thus the northway factor works better for the first two.
