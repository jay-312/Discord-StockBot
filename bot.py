import discord
import config
from discord.ext import commands, tasks
import yfinance as yf
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
import requests

discord_token = config.API['DiscordToken']

intents = discord.Intents.default()
intents.message_content = True
help_command = commands.DefaultHelpCommand(show_parameter_descriptions=False)

bot = commands.Bot(command_prefix='$', intents=intents,help_command=help_command)

@bot.event
async def on_ready():
    print("bot is ready")

# Check if the date is in the form of YYYY-MM-DD
def is_valid_date(date_str):
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False
    
# Creating default values for startDate and endDate 
endDate = datetime.today().date()
startDate = endDate - timedelta(days=(365*2))
#converting Dates into String
endDate = f'{endDate}'      
startDate = f'{startDate}'

# Custom exception class for your Discord bot
class CustomError(commands.CommandError):
    def __init__(self, message):
        self.message = message

async def Stock_chart(ctx,stockName,startDate,endDate):    
    #check if the dates are in valid format or not
    try:
        StockDisplay = stockName.split('.')[0].upper() #StockName to be displayed to user
        print(StockDisplay)
        if not is_valid_date(startDate) or not is_valid_date(endDate):
            raise CustomError("Invalid date format. Use 'YYYY-MM-DD'.")
        
        #convert String date into Datetime format
        start_date = datetime.strptime(startDate, "%Y-%m-%d")
        end_date = datetime.strptime(endDate, "%Y-%m-%d")
        
        if end_date <= start_date:
            raise CustomError("End date must be greater than start date.")

        data = yf.download(stockName,start=start_date,end=end_date)
        print(data.head())

        if data.empty:
            raise CustomError(f"No data available for {StockDisplay}. If its Non Indian Company try $chart-us")
        
        #To create and save a plot
        plt.figure(figsize=(12, 6))
        plt.plot(data.index, data['Adj Close'], label='Adjusted Close Price', color='blue')
        plt.title(f'{StockDisplay} Adjusted Close Price')
        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.legend()
        plt.grid(True)
        filename = 'output.png"'
        plt.savefig(filename, format='png')
        await ctx.send(file=discord.File(filename))
        plt.close()

    except CustomError as e:
        await ctx.send(e)
    

@bot.command(name='chart')
async def chart(ctx,stockName,startDate = startDate,endDate = endDate):
    """
    Return Stock Performances over a period of time. For Companies listed under NSE
    
    Arguments:
        stockName (str): Give the Stock symbol of the stock (example Stock symbol of HDFC Bank Limited -> HDFCBANK).
        startDate (date,optinal): The start date in the format 'YYYY-MM-DD' (default 2 years back from today).
        endDate (date,optinal): The end date in the format 'YYYY-MM-DD'. Must be greater than startdate (default today).

    usage: 
        $chart [stockName] [startDate] [endDate]

    Example:
        $chart reliance
        $chart reliance 2021-02-01
        $chart reliance 2021-02-01 2022-02-01
    """
    stockName = stockName = f'{stockName}.NS'
    await Stock_chart(ctx,stockName,startDate,endDate)

@bot.command(name='chart-us')
async def chart(ctx,stockName,startDate = startDate,endDate = endDate):
    """
    Return Stock Performances over a period of time. For Companies listed under NASDAQ
    
    Arguments:
        stockName (str): Give the Stock symbol of the stock (example Stock symbol of apple -> aapl).
        startDate (date,optinal): The start date in the format 'YYYY-MM-DD' (default 2 years back from today).
        endDate (date,optinal): The end date in the format 'YYYY-MM-DD'. Must be greater than startdate (default today).

    usage: 
        $chart-us [stockName] [startDate] [endDate]

    Example:
        $chart-us aapl
        $chart-us aapl 2021-02-01
        $chart-us aapl 2021-02-01 2022-02-01
    """
    await Stock_chart(ctx,stockName,startDate,endDate)

#Return the current Stock Price for the given stock symbol
async def current_price(ctx,stockName):
    StockDisplay = stockName.split('.')[0].upper() #StockName to be displayed to user
    URL = "https://finance.yahoo.com/quote/" + stockName
    #setting custom User-Agent header to mimic a web browser (getting 404 for scraping) 
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}
    page = requests.get(URL, headers=headers)
    soup = BeautifulSoup(page.text, "html.parser")
    try:
        current_price = soup.find_all("div", {"class":"My(6px) Pos(r) smartphone_Mt(6px) W(100%)"})[0].find_all("fin-streamer")[0]
        change = soup.find_all("div", {"class":"My(6px) Pos(r) smartphone_Mt(6px) W(100%)"})[0].find_all("fin-streamer")[1]
        await ctx.send(StockDisplay + "\t" + current_price.text + "\t" + change.text)

    except IndexError as e:
        await ctx.send('Data Not Found')

@bot.command(name='price')
async def price_nse(ctx,stockName):
    """
    Return Current Stock Price. For Companies listed under NSE
    
    Arguments:
        stockName (str): Give the Stock symbol of the stock (example Stock symbol of HDFC Bank Limited -> HDFCBANK).

    usage: 
        $price [stockName]

    Example:
        $price reliance
        
    """
    stockName = stockName = f'{stockName}.NS'
    await current_price(ctx,stockName)

@bot.command(name='price-us')
async def price_nasdaq(ctx,stockName):
    """
    Return Current Stock Price. For Companies listed under NASDAQ
    
    Arguments:
        stockName (str): Give the Stock symbol of the stock (example Stock symbol of apple -> aapl).

    usage: 
        $price-us [stockName]

    Example:
        $price-us aapl
        
    """
    await current_price(ctx,stockName)

bot.run(discord_token)