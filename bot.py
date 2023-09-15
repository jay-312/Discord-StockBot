import discord
import config
from discord.ext import commands, tasks
import pandas_datareader.data as pdr

discord_token = config.API['DiscordToken']

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='$', intents=intents)

@bot.event
async def on_ready():
    print("bot is ready")

@bot.command(name='Chart', description ='Return Stock Performances over a period of time')
async def chart(ctx,quo):
    pass

bot.run(discord_token)