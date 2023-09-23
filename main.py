import discord
from discord.ext import commands
from discord import app_commands
import config
import yfinance as yf
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
import requests

discord_token = config.API['DiscordToken']

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='.', intents=intents)

@bot.event
async def on_ready():
    print("bot is ready")
    # try:
    #     # print(ctx.guild.id)
    #     synced = await bot.tree.sync(guild=discord.Object(id=1151895074439966791))
    #     print(f"Synced {len(synced)} Command(s)")
    # except Exception as e:
    #     print(e)

@bot.command(name='sync')
async def sync(ctx):
    try:
        # print(ctx.guild.id)
        # bot.tree.copy_global_to(guild=ctx.guild)
        synced = await bot.tree.sync(guild=ctx.guild)
        await ctx.send(f"Synced {len(synced)} Command(s)")
    except Exception as e:
        print(e)

# Custom exception class for your Discord bot
class CustomError(commands.CommandError):
    def __init__(self, message):
        self.message = message

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

#chart command to Return Stock Performances
@bot.tree.command(name='chart',description='Return Stock Performances over a period of time. For 2 years by Default')
@app_commands.describe(stock_name = "Give the Stock symbol of the stock (example Stock symbol of HDFC Bank Limited -> HDFCBANK).",
                       exchange = "If Company is listed under NSE(Indian Market) or NASDAQ(NON-Indian Market)",
                       start_date = "The start date in the format 'YYYY-MM-DD' (default 2 years back from today).",
                       end_date = "The end date in the format 'YYYY-MM-DD'. Must be greater than startdate (default today)."
                       )
@app_commands.choices(exchange = [
            app_commands.Choice(name='NSE',value='nse'),
            app_commands.Choice(name='NASDAQ',value='nasdaq')
        ])
async def chart(interaction: discord.Integration, stock_name: str,exchange : app_commands.Choice[str], start_date: str = startDate, end_date: str = endDate):
    try:
        StockDisplay = stock_name.upper() #StockName to be displayed to user
        if not is_valid_date(start_date) or not is_valid_date(end_date):
            raise CustomError("Invalid date format. Use 'YYYY-MM-DD'.")
        
        #convert String date into Datetime format
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%Y-%m-%d")
        
        if end_date <= start_date:
            raise CustomError("End date must be greater than start date.")
        
        #add .NS to stockname for stocks listed under NSE
        stock_name =  f'{stock_name}.NS' if exchange.value == 'nse' else stock_name

        data = yf.download(stock_name,start=start_date,end=end_date)
        print(data.head())

        if data.empty:
            raise CustomError(f"No data available for {StockDisplay}. If its Non Indian Company try NASDAQ exchange")
        
        #To create and save a plot
        plt.figure(figsize=(12, 6))
        plt.plot(data.index, data['Adj Close'], label='Adjusted Close Price', color='blue')
        plt.title(f'{StockDisplay} Adjusted Close Price')
        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.legend()
        plt.grid(True)
        filename = 'output.png'
        plt.savefig(filename, format='png')
        await interaction.response.send_message(file=discord.File(filename))
        plt.close()

    except CustomError as e:
        await interaction.response.send_message(e)
    
#Price command to return the current stock price
@bot.tree.command(name='price',description="Return Current Stock Price.")
@app_commands.describe(stock_name = "Give the Stock symbol of the stock (example Stock symbol of HDFC Bank Limited -> HDFCBANK).",
                       exchange = "If Company is listed under NSE(Indian Market) or NASDAQ(NON-Indian Market)"
                       )
@app_commands.choices(exchange = [
            app_commands.Choice(name='NSE',value='nse'),
            app_commands.Choice(name='NASDAQ',value='nasdaq')
        ])
async def price(interaction: discord.Integration, stock_name: str,exchange : app_commands.Choice[str]):
    StockDisplay = stock_name.upper() #StockName to be displayed to user

    #add .NS to stockname for stocks listed under NSE
    stock_name =  f'{stock_name}.NS' if exchange.value == 'nse' else stock_name

    URL = "https://finance.yahoo.com/quote/" + stock_name
    #setting custom User-Agent header to mimic a web browser (getting 404 for scraping) 
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}
    page = requests.get(URL, headers=headers)
    soup = BeautifulSoup(page.text, "html.parser")
    try:
        current_price = soup.find_all("div", {"class":"My(6px) Pos(r) smartphone_Mt(6px) W(100%)"})[0].find_all("fin-streamer")[0]
        change = soup.find_all("div", {"class":"My(6px) Pos(r) smartphone_Mt(6px) W(100%)"})[0].find_all("fin-streamer")[1]
        await interaction.response.send_message(f"{StockDisplay}\t{current_price.text}\t{change.text}")

    except IndexError as e:
        await interaction.response.send_message('Data Not Found')

#info command to Return the Information of the given stock
@bot.tree.command(name='info',description="Return Information for the stock.")
@app_commands.describe(stock_name = "Give the Stock symbol of the stock (example Stock symbol of HDFC Bank Limited -> HDFCBANK).",
                       exchange = "If Company is listed under NSE(Indian Market) or NASDAQ(NON-Indian Market)"
                       )
@app_commands.choices(exchange = [
            app_commands.Choice(name='NSE',value='nse'),
            app_commands.Choice(name='NASDAQ',value='nasdaq')
        ])
async def info(interaction: discord.Integration, stock_name: str,exchange : app_commands.Choice[str]):
    StockDisplay = stock_name.upper() #StockName to be displayed to user

    #add .NS to stockname for stocks listed under NSE
    stock_name =  f'{stock_name}.NS' if exchange.value == 'nse' else stock_name
    
    yf_symbol = yf.Ticker(stock_name)
    embed = discord.Embed(
        title = f'{StockDisplay} Information',
        colour = discord.Colour.blue()
    )
    info = yf_symbol.info
    try:
        if 'longName' not in info:
            raise CustomError(f'Info on stock symbol {StockDisplay} is not available.')
        Name = info.get('longName', 'N/A')
        industryDisp = info.get('industryDisp', 'N/A')
        sectorDisp = info.get('sectorDisp', 'N/A')
        dayLow = info.get('dayLow', 'N/A')
        dayHigh = info.get('dayHigh', 'N/A')
        fiftyTwoWeekLow = info.get('fiftyTwoWeekLow', 'N/A')
        fiftyTwoWeekHigh = info.get('fiftyTwoWeekHigh', 'N/A')
        currency = info.get('currency', 'N/A')
        # exchange = info.get('exchange', 'N/A')
        phone = info.get('phone', 'N/A')
        website = info.get('website', 'N/A')
        # creating a Business Summary of len around 500
        longBusinessSummary = info.get('longBusinessSummary', 'N/A').split('. ')
        BusinessSummary = ''
        while len(BusinessSummary) < 600 and longBusinessSummary:
            BusinessSummary += f'{longBusinessSummary.pop(0)}. '
        # BusinessSummary = ". ".join(longBusinessSummary[:4]).rstrip() + "."
        # create a single address from the given json
        address_parts = []
        address_parts.append(info.get('address1', 'N/A'))
        address_parts.append(info.get('city', ''))
        address_parts.append(info.get('country', ''))
        address_parts.append(info.get('zip', ''))
        address = "\n".join(address_parts)

        embed.add_field(name="Name", value=Name, inline=True)
        embed.add_field(name="Symbol", value=StockDisplay, inline=True)
        embed.add_field(name="Industry", value=industryDisp, inline=True)
        embed.add_field(name="Sector", value=sectorDisp, inline=True)
        embed.add_field(name="Day Low", value=dayLow, inline=True)
        embed.add_field(name="Day High", value=dayHigh, inline=True)
        embed.add_field(name="52 Weeks Low", value=fiftyTwoWeekLow, inline=True)
        embed.add_field(name="52 Weeks High", value=fiftyTwoWeekHigh, inline=True)
        embed.add_field(name="Currency", value=currency, inline=True)
        # embed.add_field(name="exchange", value=exchange, inline=True)
        embed.add_field(name="Business Summary", value=BusinessSummary, inline=False)
        embed.add_field(name="Phone", value=phone, inline=True)
        embed.add_field(name="Address", value=address, inline=True)
        embed.add_field(name="Website", value=website, inline=True)
        await interaction.response.send_message(embed=embed)
    
    except CustomError as e:
        await interaction.response.send_message(e)

@bot.tree.command(name='index',description='Return Current Price and price change for NASDAQ and Nifty 50 and Nifty Bank')
async def index(interaction:discord.Integration):
    embed = discord.Embed(
        title = 'Indexes',
        colour = discord.Colour.blue()
    )
    embed.set_footer(text="Data from Yahoo Finance")
    await interaction.response.send_message("Searching for data...")
    three = [["NASDAQ", "^IXIC"], ["Nifty 50", "^NSEI"], ["Nifty Bank", "^NSEBANK"]]
    indexname = ""
    indexprice = ""
    indexchange = ""
    for i in range(3):
        URL = "https://finance.yahoo.com/quote/" + three[i][1]
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}
        page = requests.get(URL, headers=headers)
        soup = BeautifulSoup(page.text, "html.parser")
        try:
            current_price = soup.find_all("div", {"class":"My(6px) Pos(r) smartphone_Mt(6px) W(100%)"})[0].find_all("fin-streamer")[0]
            change = soup.find_all("div", {"class":"My(6px) Pos(r) smartphone_Mt(6px) W(100%)"})[0].find_all("fin-streamer")[1]
            indexname += three[i][0] + "\n"
            if i==0:
                indexprice += current_price.text + " (USD)\n"
            else:
                indexprice += current_price.text + " (INR)\n"
            indexchange += change.text + "\n"
        except:
            indexname += three[i][0] + "\n"
            indexprice += "No data found\n"
            indexchange += "No data found\n"

    embed.add_field(name="Index", value=indexname, inline=True)
    embed.add_field(name="Price", value=indexprice, inline=True)
    embed.add_field(name="Change", value=indexchange, inline=True)
        
    await interaction.edit_original_response(embed=embed)

bot.run(discord_token)