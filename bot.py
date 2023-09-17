import discord
import config
from discord.ext import commands, tasks
import yfinance as yf
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

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
        StockDisplay = stockName.split('.')[0].upper()
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
    Return Stock Performances over a period of time.
    
    Arguments:
        stockName (str): Give the Stock symbol of the stock (example Stock symbol of apple -> aapl).
        startDate (date,optinal): The start date in the format 'YYYY-MM-DD' (default 2 years back from today).
        endDate (date,optinal): The end date in the format 'YYYY-MM-DD'. Must be greater than startdate (default today).

    usage: 
        $chart [stockName] [startDate] [endDate]
        $chart-us [stockName] [startDate] [endDate] for Non Indian Companies

    Example:
        $chart-us aapl
        $chart reliance
        $chart reliance 2021-02-01
        $chart reliance 2021-02-01 2022-02-01
    """
    stockName = stockName = f'{stockName}.NS'
    await Stock_chart(ctx,stockName,startDate,endDate)

@bot.command(name='chart-us')
async def chart(ctx,stockName,startDate = startDate,endDate = endDate):
    """
    Return Stock Performances over a period of time. For Non-Indian Companies
    
    Arguments:
        stockName (str): Give the Stock symbol of the stock (example Stock symbol of apple -> aapl).
        startDate (date,optinal): The start date in the format 'YYYY-MM-DD' (default 2 years back from today).
        endDate (date,optinal): The end date in the format 'YYYY-MM-DD'. Must be greater than startdate (default today).

    usage: 
        $chart [stockName] [startDate] [endDate]
        $chart-us [stockName] [startDate] [endDate] for Non Indian Companies

    Example:
        $chart-us aapl
        $chart reliance
        $chart reliance 2021-02-01
        $chart reliance 2021-02-01 2022-02-01
    """
    await Stock_chart(ctx,stockName,startDate,endDate)


bot.run(discord_token)