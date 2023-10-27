# Discord Stock Bot

## Description

The Discord Stock Bot is a versatile Discord bot designed to provide real-time stock market data and news updates directly in your Discord server. With this bot, users can easily access stock prices, charts, company information, and the latest financial news, all within their Discord environment. The bot offers a seamless way to stay informed about financial markets without leaving your Discord server.

## Table of Contents
1. [Technical Documentation](#technical-documentation)
2. [Bot Features](#bot-features)
3. [User Documentation](#user-documentation)

## Technical Documentation

### Installation

1. Install Python 3.6 or above. [Download](https://www.python.org/) Python
2. Clone the repository to your local machine: `git clone https://github.com/jay-312/Discord-StockBot`
3. Install the required Python packages: `pip install -r requirements.txt`
4. Configure the bot token:
    - Create a Discord bot on the [Discord Developer Portal](https://discord.com/developers/applications).
    - Copy the bot token and update it in the config.py file:
      ```bash
      API = {
        'DiscordToken': 'your-bot-token-here'
      }
      ```
5. Add the bot to your discord server/guild
6. Run the bot: `python main.py`


## Bot Features

The Discord Stock Bot functions by integrating with Discord and connecting to financial data sources. Here's an overview of its functionality:

1. **Stock Price Command:** Users can request real-time stock price information for a specific stock symbol for companies listed on NSE or NASDAQ.

2. **Stock Chart Command:** Users can request stock price charts, displaying the stock's adjusted close price over a specified date range. By default, it shows a two-year historical chart.

3. **Stock News Command:** The bot scrapes financial news from Google Finance and provides users with the latest business news for a specific stock symbol.

4. **Scheduled News Updates:** The bot sends daily business news updates at 8 AM IST to channels that opt to receive these updates.


## User Documentation

### Commands

- **price -** Return the current stock price.
  - Params - stock_symbol exchange
  - example - `/price stock_name:reliance exchange:NSE`
- **chart -** Return Stock Performances over a period of time. For 2 years by Default.
  - Params - stock_symbol exchange [start_date] [end_date]
  - example - `/chart stock_name:aapl exchange:NASDAQ start_date:2022-01-01 end_date:2023-06-01`
- **info -** Return Information about the stock.
  - Params - stock_symbol exchange
  - example - `/info stock_name:hdfcbank exchange:NSE`
- **index -** Return Current Price and price change for NASDAQ and Nifty 50 and Nifty Bank.
  - Params - None
  - example - `/index`
- **stocknews -** Return the news of the specfic stock symbol (Source: Google Finance)
  - Params - stock_symbol exchange
  - example - `/stocknews stock_name:msft exchange:NASDAQ`
- **news -** Return the latest Business News at **8 AM IST Everyday** (Source: Google News) 
  - Params - [ON/OFF]
  - example - `/news status:ON`


