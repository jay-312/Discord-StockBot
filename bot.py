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
endDate = f'{endDate}'      #converting to string
startDate = f'{startDate}'

@bot.command(name='chart')
async def chart(ctx,stockName,startDate = startDate,endDate = endDate):
    """
    Return Stock Performances over a period of time.
    
    Arguments:
        stockName (str): Give the Stock symbol of the stock (example Stock symbol of apple -> aapl).
        startDate (date,optinal): The start date in the format 'YYYY-MM-DD' (default 2 years back from today).
        endDate (date,optinal): The end date in the format 'YYYY-MM-DD'. Must be greater than startdate (default today).

    usage = '$chart [stockName] [startDate] [endDate]'

    Example:
        $chart aapl
        $chart aapl 2021-02-01
        $chart aapl 2021-02-01 2022-02-01
    """

    if not is_valid_date(startDate) or not is_valid_date(endDate):
        raise commands.BadArgument("Invalid date format. Use 'YYYY-MM-DD'.")

    start_date = datetime.strptime(startDate, "%Y-%m-%d")
    end_date = datetime.strptime(endDate, "%Y-%m-%d")

    if end_date <= start_date:
        raise commands.BadArgument("End date must be greater than start date.")
    
    data = yf.download(stockName,start=start_date,end=end_date)
    print(data.head())

    if data.empty:
        raise commands.BadArgument(f"No data available for {stockName}.")
    
    
    await ctx.send(stockName)

@chart.error
async def chart_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Stock name is required. Use '$chart <stockName> [startDate] [endDate]'.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send(error)

bot.run(discord_token)