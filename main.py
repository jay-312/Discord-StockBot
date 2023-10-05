import discord
from discord.ext import commands,tasks
from discord import app_commands
import config
import yfinance as yf
from datetime import *
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin

discord_token = config.API['DiscordToken']

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='.', intents=intents)

@bot.event
async def on_ready():
    news_once_a_day.start()
    print("bot is ready")

@bot.command(name='sync')
async def sync(ctx):
    try:
        # print(ctx.guild.id)
        # bot.tree.copy_global_to(guild=ctx.guild)
        synced = await bot.tree.sync()
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

    except Exception as e:
        print(e)
        await interaction.response.send_message(f'Info on stock symbol {StockDisplay} is not available on {exchange.name} exchange. Try different exchange.')

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
    try:
        info = yf_symbol.info
        if 'longName' not in info:
            raise CustomError(f'Info on stock symbol {StockDisplay} is not available on {exchange.name} exchange. Try different exchange.')
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
    
    except Exception as e:
        print(e)
        await interaction.response.send_message(f'Info on stock symbol {StockDisplay} is not available on {exchange.name} exchange. Try different exchange.')

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

@bot.tree.command(name='stocknews',description='Return the news of the specfic stock symbol (Source: Google Finance)')
@app_commands.describe(stock_name = "Give the Stock symbol of the stock (example Stock symbol of HDFC Bank Limited -> HDFCBANK).",
                       exchange = "If Company is listed under NSE(Indian Market) or NASDAQ(NON-Indian Market)"
                       )
@app_commands.choices(exchange = [
            app_commands.Choice(name='NSE',value='nse'),
            app_commands.Choice(name='NASDAQ',value='nasdaq')
        ])
async def stocknews(interaction: discord.Integration, stock_name: str,exchange : app_commands.Choice[str]):
    StockDisplay = stock_name.upper() #StockName to be displayed to user
    URL = f"https://www.google.com/finance/quote/{StockDisplay}:{exchange.name}?hl=en"
    # setting custom User-Agent header to mimic a web browser (getting 404 for scraping) 
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}
    page = requests.get(URL, headers=headers)
    soup = BeautifulSoup(page.text, "html.parser")
    try:
        all_news = soup.find_all("div", {"class":"yWOrNb"})
        if all_news == []:
            raise CustomError(f"News for {StockDisplay} is not available on {exchange.name} exchange. Try different exchange")
        embeds = []
        all_news_scroll = all_news[0].find_all("div", {"class":"qQfHId"})
        for news in all_news_scroll:
            heading = news.find_all("div",{"class":"xr68cf"})[0].text
            if heading == 'Opinion':
                continue
            embed = discord.Embed(
            title = heading,
            colour = discord.Colour.blue()
            )
            links = news.find_all("a",{"class":"TxRU9d"})
            for link in links:
                href = link.get("href")
                source = link.find_all("div", {"class":"AYBNIb"})[0].text
                name = link.find_all("div", {"class":"F2KAFc"})[0].text
                update = link.find_all("div", {"class":"HzW5e"})[0].text
                embed.add_field(name=name, value=f"{href}\n{source}\n{update}\n ‎",inline=False)
                # embed.add_field(name = chr(173), value = chr(173))
            embeds.append(embed)
        # Some More News
        extra_news = all_news[0].find_all("div", {"class":"yY3Lee"})
        heading = all_news[0].find_all("div", {"class":"yV3rjd"})
        heading = heading[0].text if heading else "Some More News"
        embed = discord.Embed(
        title = heading,
        colour = discord.Colour.blue()
        )
        for news in extra_news:
            link = news.find_all("a")[0]
            href = link.get("href")
            source = link.find_all("div", {"class":"sfyJob"})[0].text
            name = link.find_all("div", {"class":"Yfwt5"})[0].text
            update = link.find_all("div", {"class":"Adak"})[0].text
            embed.add_field(name=name, value=f"{href}\n{source}\n{update}\n ‎",inline=False)
        embeds.append(embed)
        await interaction.response.send_message(content=f"News for {StockDisplay}",embeds=embeds)

    except Exception as e:
        print(e)
        await interaction.response.send_message(f'Info on stock symbol {StockDisplay} is not available on {exchange.name} exchange. Try different exchange.')

# write the guild and channel to file for back-up
def write_to_file(filename,text):
    file = open(filename,'a')
    file.write(f'{text}\n')
    file.close()

#remove the channel from the file if they turn off news update
def remove_from_file(filename,text):
    file = open(filename,'r')
    lines = file.readlines()
    file = open(filename,'w')
    for line in lines:
        # strip() is used to remove '\n' present at the end of each line
        if line.strip('\n') != text:
            file.write(line)
    file.close()

ist_timezone = timezone(timedelta(hours=5, minutes=30)) # create timezone IST (UTC + 5:30)
loop_time = time(hour=8,minute=00,tzinfo=ist_timezone)  # create time 8 AM IST
@tasks.loop(time=loop_time)
async def news_once_a_day():
    URL = 'https://news.google.com/topics/CAAqKggKIiRDQkFTRlFvSUwyMHZNRGx6TVdZU0JXVnVMVWRDR2dKSlRpZ0FQAQ?ceid=IN:en&oc=3'
    # setting custom User-Agent header to mimic a web browser (getting 404 for scraping) 
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}
    page = requests.get(URL, headers=headers)
    soup = BeautifulSoup(page.text, "html.parser")
    # await interaction.response.send_message("Today's Business News")
    all_news = soup.find_all("c-wiz", {"class":"PO9Zff Ccj79 kUVvS"})
    try:
        embed = discord.Embed(
        title = "Today's Business News",
        colour = discord.Colour.blue()
        )
        counter = 0
        while counter < 10:
            counter += 1
            news = all_news[counter]
            article = news.find_all("article")[0]
            href = article.find_all("a")[0].get('href')
            source = article.find_all("div", {"class":"vr1PYe"})[0].text
            name = article.find_all("h4")[0].text
            update = article.find_all("time", {"class":"hvbAAd"})[0].text
            baseUrl = 'https://news.google.com/'
            final_href = urljoin(baseUrl,href)
            embed.add_field(name=source, value=f"**[{name}]({final_href})**\n{update}\n ‎",inline=False)
        # Find the channels with news command status ON and send news on those channels
        file = open("daily_news_ids.txt",'r')
        lines = file.readlines()
        file.close()
        for line in lines:
            line = line.strip('\n').split('$')
            guild = bot.get_guild(int(line[0]))
            if guild:
                channel = guild.get_channel(int(line[1]))
                if channel:
                    await channel.send(embed=embed)
                else:
                    pass
            else:
                pass

    except Exception as e:
        print(e)

@bot.tree.command(name='news',description='Return the latest Business News at 8 AM IST (Source: Google News)')
@app_commands.describe(status = "Turn the news updates ON or OFF.")
@app_commands.choices(status = [
            app_commands.Choice(name='ON',value='ON'),
            app_commands.Choice(name='OFF',value='OFF')
        ])
async def news(interaction: discord.Integration, status : app_commands.Choice[str]):
    unique_id = f"{interaction.guild_id}${interaction.channel_id}"
    if status.value == 'ON':
        write_to_file("daily_news_ids.txt",unique_id)
    else :
        remove_from_file("daily_news_ids.txt",unique_id)
    
bot.run(discord_token)