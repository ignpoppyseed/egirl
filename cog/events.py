import asyncio, glob, json, math, os, random, time, dice
import aiohttp, discord, requests, topgg, pyttsx3, string, sqlite3
from io import BytesIO
from discord import Option, OptionChoice
from discord.ui import Button, View
from discord.ext import tasks, pages, commands
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont
from main import egirl_cogs, hyToken, topggToken, booksToken, weatherToken, egirlVersion, roleplay_api, reportManager, reportManagerName, loggingChannel

debugMode = False

reportLock = []

class cog_events(commands.Cog):
    def __init__(self, bot, *args, **kwargs):
        self.bot = bot
        self.bot.topggpy = topgg.DBLClient(self.bot, topggToken)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot: 
            return
        if message.mentions:
            if f'<@{self.bot.user.id}>' in message.content:
                egirlEmbed = discord.Embed(title='about egirl', url='https://cloverbrand.xyz/egirl/', color=0x202225)
                egirlEmbed.add_field(name=f'running egirl v{egirlVersion}', value=
                    f'**[invite !](https://cloverbrand.xyz/egirl/invite/)** | **[website !](https://cloverbrand.xyz)** | **[vote !](https://top.gg/bot/825415772075196427/vote)**\n\
                    egirl is constantly being updated!\n\
                    if you have an issue, contact the developer @ poppy#0001 or egirl@cloverbrand.xyz\n\
                    egirl\'s pronouns are she/her',inline=False)
                tip = [
                    '**tip:** egirl\'s profile picture changes every 10 minutes!',
                    '**tip:** some egirl commands can only be accessed by poppy, ask her to show you!',
                    '**tip:** invite egirl\'s best friend, catgirl @ https://bot.cloverbrand.xyz!',
                    '**tip:** schedule regular veterinary visits for your pets!',
                    '**fact:** trans rights are human rights!',
                    '**fact:** egirl\'s favorite color is \#202225'
                ]
                egirlEmbed.add_field(name=f'extra', value=f'{tip[random.randrange(0, len(tip))]}', inline=False)
                egirlEmbed.set_footer(text=f'requested by {message.author}', icon_url=f'{message.author.avatar.url}'),
                await message.reply(embed=egirlEmbed, mention_author=False)
        db = sqlite3.connect("database.sqlite")
        cursor = db.cursor()
        cursor.execute(f"SELECT goodbye_channel FROM data WHERE server_id = {message.guild.id}")
        result = cursor.fetchone()
        try:
            if result[0] is not None:
                if random.randrange(0, 20+1) == 5:
                    messageables = ['UwU', 'OwO', '>w<', '^w^']
                    await message.channel.send(messageables[random.randrange(0, len(messageables))], mention_author=False)
            else: return
        except Exception as e: return

    @commands.Cog.listener()
    async def on_member_join(self, member):
        db = sqlite3.connect("database.sqlite")
        cursor = db.cursor()
        cursor.execute(f"SELECT welcome_channel FROM data WHERE server_id = {member.guild.id}")
        result = cursor.fetchone()
        try:
            if result[0] is not None:
                welcomeChannel = int(result[0])
                # this section creates the image from the params
                img = Image.open('templates/welcomeTemplate.png')
                img = img.convert("RGBA")
                mask1 = Image.open('templates/profile_circle.jpg')
                async with aiohttp.ClientSession() as session:
                    async with session.get(str(member.avatar)) as resp:
                        profileAvatar = Image.open(BytesIO(await resp.read()))
                profileAvatar = profileAvatar.convert("RGBA")
                profileAvatar = profileAvatar.resize((120, 120), Image.Resampling.LANCZOS)
                welcFont = ImageFont.truetype('fonts/font.ttf', size=32)
                textLayer = Image.new('RGBA', img.size, (255, 255, 255, 0))
                templateWidth, templateHeight = img.size
                pfpWidth, pfpHeight = profileAvatar.size
                offset = ((templateWidth - pfpWidth) // 2, ((templateHeight - pfpHeight) // 2) - 30)
                img.paste(profileAvatar, offset, mask=mask1)
                draw = ImageDraw.Draw(textLayer)
                draw.text(((templateWidth / 2) + 3, (templateHeight / 2) + 63), f'{member.name}#{member.discriminator}', (0, 0, 0, 80), anchor="mm", font=welcFont)
                draw.text((templateWidth / 2, (templateHeight / 2) + 60), f'{member.name}#{member.discriminator}', (255, 255, 255), anchor="mm", font=welcFont)
                img = Image.alpha_composite(img, textLayer)
                img.save(f'welcome/{member.id}.png')
                #build the welcome embed
                welcomeEmbed = discord.Embed(title=f'', description=f'welcome {member.mention}!', color=0x202225)
                embedSendFile = discord.File(f'welcome/{member.id}.png', filename='welcome!.png')
                welcomeEmbed.set_image(url='attachment://welcome.png')
                # send the welcome embed
                channel = self.bot.get_channel(int(welcomeChannel))
                await channel.send(file=embedSendFile, embed=welcomeEmbed)
                # clean up
                os.remove(f'welcome/{member.id}.png')
            else: return
        except Exception as e: return

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        db = sqlite3.connect("database.sqlite")
        cursor = db.cursor()
        cursor.execute(f"SELECT goodbye_channel FROM data WHERE server_id = {member.guild.id}")
        result = cursor.fetchone()
        try:
            if result[0] is not None:
                goodbyeChannel = int(result[0])
                embed = discord.Embed(title=f'', description=f'**{member}** left! we\'ll miss you!', color=0x202225)
                embed.set_thumbnail(url=member.display_avatar.url)
                channel = self.bot.get_channel(int(goodbyeChannel))
                await channel.send(embed=embed)
            else: return
        except Exception as e: return

def setup(bot):
    bot.add_cog(cog_events(bot))
    print('cog.events loaded')
def teardown(bot):
    print('cog.events unloading')