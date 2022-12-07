import asyncio, glob, json, math, os, random, time, dice, aiohttp, discord, requests, topgg, pyttsx3, string, sqlite3
from io import BytesIO
from discord import Option, OptionChoice
from discord.ui import Button, View
from discord.ext import tasks, pages
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont

load_dotenv()
TOKEN = os.getenv('TOKEN')
hyToken = os.getenv('HYPIXEL_API_TOKEN')
topggToken = os.getenv('TOPGGTOKEN')
booksToken = os.getenv('GOOGLE_BOOKS')
weatherToken = os.getenv('OPENWEATHER')

intents = discord.Intents.all()

bot = discord.AutoShardedBot(case_insensitive=True, command_prefix=";", intents=intents, activity=discord.Activity(type=discord.ActivityType.watching, name="connecting to api,,,"), status=discord.Status.idle)

egirl_cogs = ['cog.all', 'cog.config', 'cog.events', 'cog.counting']

debugMode = False
egirlVersion = '1.22'
loggingChannel = 994443884878901378
reportManager = 402569003903483904
reportManagerName = 'poppy#0001'
roleplay_api = 'https://api.dbot.dev/images/'

reportLock = []

@bot.event
async def on_ready():
    global bootstart
    local_time = time.ctime()
    if debugMode == True:
        dbSay = '\n<<beta debugging is currently enabled by default!>>'
    elif debugMode == False:
        dbSay = '\n<<beta debugging is currently disabled by default! enable it with \'debug on\'>>'
    bootend = time.time()
    boottime = str(round(bootend-bootstart, 2))+' seconds'
    print(f'{bot.user} connected to the api successfully!\nBot ID: {bot.user.id}\nLocal time: {local_time}\nBoot time: {boottime}\negirl {egirlVersion}!\ndeveloped by poppy#0001!\nTotal Servers: {len(bot.guilds)}\nhttps://cloverbrand.xyz/egirl/{dbSay}')

bootstart = time.time()
if __name__ == '__main__':
    for ex in egirl_cogs:
        try: bot.load_extension(ex)
        except Exception as e: print(f'failed to load cog {ex}\nerror: {e}')
    bot.run(TOKEN)