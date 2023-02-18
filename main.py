import asyncio, glob, json, math, os, random, time, dice, aiohttp, discord, requests, topgg, pyttsx3, string, sqlite3, gtts
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
egirlVersion = '2.3.0'
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

'''@bot.event
async def on_connect():
    bot.topggpy = topgg.DBLClient(bot, topggToken)
    update_stats.start()

@tasks.loop(seconds=60)
async def update_stats():
    """This function runs every 30 minutes to automatically update your server count."""
    try:
        await bot.topggpy.post_guild_count()
        print(f"Posted server count ({bot.topggpy.guild_count})")
    except Exception as e:
        print(f"Failed to post server count\n{e.__class__.__name__}: {e}")'''


@bot.event
async def on_application_command_error(ctx, e):
    print(e)
    embed = discord.Embed(title=f'', description=f'**command error**: {e}', color=0x202225)
    embed.set_footer(text=f'{bot.user.name} • ©{reportManagerName}', icon_url=f'{bot.user.avatar.url}')
    await ctx.respond(embed=embed)

bootstart = time.time()
if __name__ == '__main__':
    for ex in egirl_cogs:
        try: bot.load_extension(ex)
        except Exception as e: print(f'failed to load cog {ex}\nerror: {e}')
    bot.run(TOKEN)