import asyncio
import datetime
import glob
import json
import math
import os
import random
import time
import topgg

import aiohttp
import discord
import requests
from io import BytesIO
from discord import Option, OptionChoice
from discord.ext import tasks
from discord.utils import get
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont

load_dotenv()
TOKEN = os.getenv('TOKEN')
hyToken = os.getenv('HYPIXEL_API_TOKEN')
topggToken = os.getenv('TOPGGTOKEN')

intents = discord.Intents.default()
intents.guilds = True
intents.members = True

bot = discord.AutoShardedBot(case_insensitive=True, command_prefix=";", intents=intents, activity=discord.Activity(type=discord.ActivityType.watching, name="connecting to api"), status=discord.Status.online)

bot.topggpy = topgg.DBLClient(bot, topggToken)

debugMode = False
egirlVersion = '1.17.1'
loggingChannel = 994443884878901378
reportManager = 402569003903483904

reportLock = []

@bot.event
async def on_ready():
    local_time = time.ctime()
    if debugMode == True:
        dbSay = '\n<<beta debugging is currently enabled by default!>>'
    elif debugMode == False:
        dbSay = '\n<<beta debugging is currently disabled by default! enable it with \'debug on\'>>'
    print(f'{bot.user} connected to the api successfully!\nBot ID: {bot.user.id}\nLocal time: {local_time}\negirl {egirlVersion}!\ndeveloped by poppy#0001!\nTotal Servers: {len(bot.guilds)}\nhttps://cloverbrand.xyz/egirl/{dbSay}')
    pfp_task.start()
    stat_task.start()
    topggStats.start()
    await bot.get_channel(loggingChannel).send(f'{bot.user} connected to the api successfully!\nBot ID: {bot.user.id}\nLocal time: {local_time}\negirl {egirlVersion}!\ndeveloped by poppy#0001!\nTotal Servers: {len(bot.guilds)}\nhttps://cloverbrand.xyz/egirl/{dbSay}')


def get_welcome_channel(guildID):
    with open('db.json', 'r') as f:
        welChannels = json.load(f)
    f.close()
    return welChannels[str(guildID)]

def get_goodbye_channel(guildID):
    with open('byedb.json', 'r') as f:
        byeChannels = json.load(f)
    f.close()
    return byeChannels[str(guildID)]

def get_uwu_state(guildID):
    with open('uwudb.json', 'r') as f:
        uwuState = json.load(f)
    f.close()
    return uwuState[str(guildID)]

@bot.event
async def on_message(message):
    if message.author == bot.user: 
        return
    try:
        if get_uwu_state(message.guild.id) == 'on':
            if random.randrange(0, 20+1) == 5:
                messageables = ['UwU', 'OwO', '>w<', '^w^']
                await message.channel.send(messageables[random.randrange(0, len(messageables))], mention_author=False)
    except: pass

@bot.event
async def on_member_join(member):
    try:
        welcomeChannel = get_welcome_channel(str(member.guild.id))
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
        channel = bot.get_channel(int(welcomeChannel))
        await channel.send(file=embedSendFile, embed=welcomeEmbed)
        # clean up
        os.remove(f'welcome/{member.id}.png')
    except:
        pass

@bot.event
async def on_member_remove(member):
    try:
        goodbyeChannel = get_goodbye_channel(str(member.guild.id))
        embed = discord.Embed(title=f'', description=f'**{member}** left! we\'ll miss you!', color=0x202225)
        embed.set_thumbnail(url=member.display_avatar.url)
        channel = bot.get_channel(int(goodbyeChannel))
        await channel.send(embed=embed)
    except:
        pass


@tasks.loop(minutes=10)
async def pfp_task():
    try:
        aviArray = glob.glob('./images/*.jpg')
        randAvi = random.randrange(0, len(aviArray))
        fileProfileImage = open(aviArray[randAvi], 'rb')
        pfp = fileProfileImage.read()
        await bot.user.edit(avatar=pfp)
    except discord.errors.HTTPException:
        print('bot avatar failed to update due to ratelimit. retrying in 10 minutes.')


@tasks.loop(seconds=0)
async def stat_task():
    await bot.change_presence(status=discord.Status.online, activity=discord.Game('minecraft'))
    await asyncio.sleep(30)
    await bot.change_presence(status=discord.Status.online, activity=discord.Game('really loud music'))
    await asyncio.sleep(30)
    await bot.change_presence(status=discord.Status.online, activity=discord.Game('with a pile of teeth'))
    await asyncio.sleep(30)
    await bot.change_presence(status=discord.Status.online, activity=discord.Game('with the /help command'))
    await asyncio.sleep(30)
    await bot.change_presence(status=discord.Status.online, activity=discord.Game('my favorite color is #202225'))
    await asyncio.sleep(30)
    await bot.change_presence(status=discord.Status.online, activity=discord.Game('#girlboss'))
    await asyncio.sleep(30)
    await bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.listening, name="to egirl asmr"))
    await asyncio.sleep(30)
    await bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.competing, name="egirl contests?"))
    await asyncio.sleep(30)
    await bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.listening, name="to girlboss podcasts"))
    await asyncio.sleep(30)

@tasks.loop(minutes=10)
async def wipeReportBan():
    global reportLock
    print(reportLock)
    reportLock = []

@tasks.loop(minutes=30)
async def topggStats():
    try:
        await bot.topggpy.post_guild_count()
        print(f"updated guild count: ({bot.topggpy.guild_count})")
    except Exception as e:
        print(f"encountered whoopsie when posting server count (top.gg)\nError: {e}")

@bot.slash_command(name="message", description="embed message")
async def _message(
    ctx,
    message: Option(str, 'set embed message', required=True),
    title: Option(str, 'set embed title (default: \"Message\")', required=False, default='Message'),
    titleurl: Option(str, 'set url for embed title', required=False, default=''),
    color: Option(str, 'set color for embed (default: #202225)', required=False, default='202225'),
    thumbnail: Option(str, 'set url of small image for embed, sometimes called the thumbnail', required=False, default=''), setimg: Option(str, 'set url of large image for embed', required=False, default=''),
):
    if ctx.author.guild_permissions.administrator:
        try:
            colorHex = int(hex(int(color.replace("#", ""), 16)), 0)
        except ValueError:
            await ctx.respond('Failed to embed message! That is not a valid hex code! ❌', ephemeral=True)
        message = message.replace('\\n', '\n')
        msgEmbed = discord.Embed(title=title, url=titleurl, description=message, color=colorHex)
        msgEmbed.set_footer(text=f'egirl', icon_url=bot.user.display_avatar.url)
        msgEmbed.set_thumbnail(url=thumbnail)
        msgEmbed.set_image(url=setimg)
        try:
            await ctx.channel.send(embed=msgEmbed)
            await ctx.respond('Message Sent ✅', ephemeral=True)
        except discord.errors.HTTPException:
            await ctx.respond('Failed to embed message! At least one image URL is not valid! ❌', ephemeral=True)
    else:
        await ctx.respond('You must be an administrator to embed messages! ❌', ephemeral=True)

@bot.slash_command(name="editmessage", description="edit embeded message")
async def _editmessage(
    ctx,
    channelid: Option(str, 'id channel message is in', required=True),
    messageid: Option(str, 'id of message to edit', required=True),
    message: Option(str, 'set embed message',
        required=False,
        default='&!q8gS@Vsj@M#5cky7E9E@MhCnx@8!'),
    title: Option(str, 'set embed title (default: \"Message\")',
        required=False,
        default='&!q8gS@Vsj@M#5cky7E9E@MhCnx@8!'),
    titleurl: Option(str, 'set url for embed title',
        required=False,
        default='&!q8gS@Vsj@M#5cky7E9E@MhCnx@8!'),
    color: Option(str, 'set color for embed (default: #202225)',
        required=False,
        default='&!q8gS@Vsj@M#5cky7E9E@MhCnx@8!'),
    thumbnail: Option( str, 'set url of small image for embed, sometimes called the thumbnail',
        required=False,
        default='&!q8gS@Vsj@M#5cky7E9E@MhCnx@8!'),
        setimg: Option(str, 'set url of large image for embed', required=False, default='&!q8gS@Vsj@M#5cky7E9E@MhCnx@8!'),
):
    if ctx.author.guild_permissions.administrator:
        try:
            channel = bot.get_channel(int(channelid))
            grabbedMessage = await channel.fetch_message(int(messageid))
        except ValueError:
            await ctx.respond('Please enter a valid channel and message ID! ❌', ephemeral=True)
            return
        try:
            embedDL = grabbedMessage.embeds[0].to_dict()
            if embedDL['footer']['text'] == 'egirl':
                await ctx.respond('Please select a message that contains an egirl embed! ❌', ephemeral=True)
                return
        except:
            await ctx.respond('Please select a message that contains an egirl embed! ❌', ephemeral=True)
            return
        embedDL = grabbedMessage.embeds[0].to_dict()
        if message == '&!q8gS@Vsj@M#5cky7E9E@MhCnx@8!':
            message = embedDL['description']
        if title == '&!q8gS@Vsj@M#5cky7E9E@MhCnx@8!':
            title = embedDL['title']
        if titleurl == '&!q8gS@Vsj@M#5cky7E9E@MhCnx@8!':
            try:
                titleurl = embedDL['url']
            except KeyError:
                titleurl = None
        if color == '&!q8gS@Vsj@M#5cky7E9E@MhCnx@8!':
            color1 = embedDL['color']
        if color != '&!q8gS@Vsj@M#5cky7E9E@MhCnx@8!':
            color1 = color
        if thumbnail == '&!q8gS@Vsj@M#5cky7E9E@MhCnx@8!':
            try:
                thumbnail = embedDL['thumbnail']['url']
            except KeyError:
                thumbnail = None
        if setimg == '&!q8gS@Vsj@M#5cky7E9E@MhCnx@8!':
            try:
                setimg = embedDL['image']['url']
            except KeyError:
                setimg = None
        try:
            if color == '&!q8gS@Vsj@M#5cky7E9E@MhCnx@8!':
                colorHex = color1
            else:
                color1 = str(color1)
                colorHex = int(hex(int(color1.replace("#", ""), 16)), 0)
        except ValueError:
            await ctx.respond('Failed to embed message! That is not a valid hex code! ❌', ephemeral=True)
        message = message.replace('\\n', '\n')
        msgEmbed = discord.Embed(title=title, url=titleurl, description=message, color=colorHex)
        msgEmbed.set_footer(text=f'egirl', icon_url=bot.user.display_avatar.url)
        if thumbnail != None:
            msgEmbed.set_thumbnail(url=thumbnail)
        if setimg != None:
            msgEmbed.set_image(url=setimg)
        try:
            await grabbedMessage.edit(embed=msgEmbed)
            await ctx.respond('Message Edited ✅', ephemeral=True)
        except discord.errors.HTTPException:
            await ctx.respond(
                'Failed to embed message! At least one image URL is not valid! ❌',
                ephemeral=True)
    else:
        await ctx.respond(
            'You must be an administrator to edit embeded messages! ❌',
            ephemeral=True)

@bot.slash_command(
    name="howcute",
    description="check someone's cuteness",
)
async def _howcute(ctx, user: Option(discord.Member, "choose who to check cuteness for", required=False)):
    if user == None: user = ctx.author
    cuteOpt = [
        '★★★★★★★★★★★\n11/10 Cuteness',
        '★★★★★★★★★★★★\n12/10 Cuteness',
        '★★★★★★★★★★★★★\n13/10 Cuteness',
        '★★★★★★★★★★★★★★\n14/10 Cuteness',
        '★★★★★★★★★★★★★★★\n15/10 Cuteness',
        '★★★★★★★★★★★★★★★★\n16/10 Cuteness',
        '★★★★★★★★★★★★★★★★★\n17/10 Cuteness',
        '★★★★★★★★★★★★★★★★★★\n18/10 Cuteness',
        '★★★★★★★★★★★★★★★★★★★\n19/10 Cuteness',
        '★★★★★★★★★★★★★★★★★★★★\n20/10 Cuteness',
    ]
    cuteR = random.randrange(0, len(cuteOpt))
    cuteEmbed = discord.Embed(title=f'How cute is {user}?', description=cuteOpt[cuteR], color=0x202225)
    cuteEmbed.set_thumbnail(url=user.display_avatar.url)
    cuteEmbed.set_footer(text=f'requested by {ctx.author}', icon_url=f'{ctx.author.avatar.url}'),
    await ctx.respond(embed=cuteEmbed)


@bot.slash_command(
    name="possum",
    description="random possum image",
)
async def _possum(ctx):
    embed = discord.Embed(title=f'<possum screaming>', description='', color=0x202225)
    embed.set_image(url=requests.get('https://api.cloverbrand.xyz/random').json()['url'])
    embed.set_footer(text=f'requested by {ctx.author}', icon_url=f'{ctx.author.avatar.url}'),
    await ctx.respond(embed=embed)


@bot.slash_command(
    name="miner",
    description="grab skin related images of minecraft user",
)
async def _miner(ctx, username: Option(str, "target username", required=True), type: Option(str, "what to retrive (default: head)", required=True, default='helm', choices=[
OptionChoice(name="head", value="helm"),
OptionChoice(name="isometric", value="cube"),
OptionChoice(name="fullbody", value="armor/body"),
OptionChoice(name="skin", value="skin")
]), size: Option(int, "size of object (default: 64)", required=False, default='64')):
    if type == 'helm':
        titleName = 'Head'
    elif type == 'cube':
        titleName = 'Isometric Head'
    elif type == 'armor/body':
        titleName = 'Body'
    else:
        titleName = ''
    if type == 'skin':
        helmEmbed = discord.Embed(title=f'{username}\'s Skin', description='', color=0x202225)
        helmEmbed.set_image(url='https://minotar.net/skin/' + username + '.png')
        helmEmbed.set_footer(text=f'requested by {ctx.author}', icon_url=f'{ctx.author.avatar.url}'),
        await ctx.respond(embed=helmEmbed)
    else:
        helmEmbed = discord.Embed(title=f'{username}\'s {titleName}', description='', color=0x202225)
        helmEmbed.set_image(url='https://minotar.net/' + type + '/' + username + '/' + str(size) + '.png')
        helmEmbed.set_footer(text=f'requested by {ctx.author}', icon_url=f'{ctx.author.avatar.url}'),
        await ctx.respond(embed=helmEmbed)


@bot.slash_command(
    name="vs",
    description="stage a battle between two users!",
)
async def _vs(
        ctx,
        player1: Option(discord.Member, "player 1", required=True),
        player2: Option(discord.Member, "player 2", required=True),
):
    nameDotOne = str(player1.display_name)
    nameDotTwo = str(player2.display_name)
    currentBattles = [str(player1.display_name), str(player2.display_name)]
    currentBattlesID = [str(player1.id), str(player2.id)]
    winnerInt = random.randrange(0, 2)
    if winnerInt == 0:
        loserInt = 1
    elif winnerInt == 1:
        loserInt = 0
    ready = ['assumes their stance', 'readies their fists', 'draws their sword','loads their nerf gun']
    attack = ['lunges at', 'stabs', 'punches', 'slices', 'bonks']
    dpass = ['explodes', 'bleeds out', 'drowns', 'falls over', 'passes out', 'dies']
    battleText1 = f'\
        {nameDotOne} {ready[random.randrange(0, len(ready))]}.\n\
        {nameDotTwo} {ready[random.randrange(0, len(ready))]}.'

    battleText2 = f'\
        {nameDotOne} {attack[random.randrange(0, len(attack))]} {nameDotTwo}!\n\
        {nameDotTwo} {attack[random.randrange(0, len(attack))]} {nameDotOne}!'

    battleText3 = f'\
        {currentBattles[loserInt]} {dpass[random.randrange(0, len(dpass))]}!\n\
        <@{currentBattlesID[winnerInt]}> is the winner!'

    battleEmbed = discord.Embed(title=f'{nameDotOne} vs {nameDotTwo}', description=battleText1, color=0x202225)
    battleEmbed.add_field(name='\u200b', value=battleText2, inline=False)
    battleEmbed.add_field(name='\u200b', value=battleText3, inline=False)
    battleEmbed.set_footer(text=f'battle requested by {ctx.author}', icon_url=f'{ctx.author.avatar.url}')
    await ctx.respond(embed=battleEmbed)

@bot.slash_command(name='help', description='bot help')
async def _help(ctx):
    embed = discord.Embed(title="egirl's Help Menu",
    description= "**[invite !](https://cloverbrand.xyz/egirl/invite/)** | **[website !](https://cloverbrand.xyz)** | **[vote !](https://top.gg/bot/825415772075196427/vote)**",
    color = 0x202225)
    embed.add_field(name = "utility", value = "```\nmessage\neditmessage\nnuke\nkick\nban\npoll\nqotd```", inline = True)
    embed.add_field(name = "fun", value = "```\nrp\nsolorp\n8ball\nslaydetector\nhowcute\nvs\nrockpaperscissors\nhowboopable\ntod\n```", inline = True)
    embed.add_field(name = "egirl", value = "```\negirl\nhelp\ninvite\nreportissue\n```", inline = True)
    embed.add_field(name = "game info", value = "```\nminer\nhypixel\n```", inline = True)
    embed.add_field(name = "config", value = "```\nwelcome\ngoodbye\nuwumode\n```", inline = True)
    embed.add_field(name = "images", value = "```\npossum\ndog\ncat\n```", inline = True)
    embed.set_footer(text=f'requested by {ctx.author}', icon_url=f'{ctx.author.avatar.url}')
    await ctx.respond(embed=embed)

@bot.slash_command(name='egirl', description='bot info')
async def _egirl(ctx):
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
    egirlEmbed.set_footer(text=f'requested by {ctx.author}', icon_url=f'{ctx.author.avatar.url}'),
    egirlEmbed.set_thumbnail(url=bot.user.display_avatar.url)
    await ctx.respond(embed=egirlEmbed)


@bot.slash_command(name='invite', description='invite egirl to your server')
async def _invite(ctx):
    inviteEmbed = discord.Embed(title='invite egirl', url='https://discord.com/api/oauth2/authorize?client_id=825415772075196427&permissions=8&scope=bot%20applications.commands', description='invite egirl if you want to be cool', color=0x202225)
    inviteEmbed.set_footer(text=f'requested by {ctx.author}', icon_url=f'{ctx.author.avatar.url}'),
    await ctx.respond(embed=inviteEmbed)

@bot.slash_command(name='welcome', description='choose the channel to send welcomes in')
async def _welcome(ctx, action: Option(str, "add or remove", choices=[
    OptionChoice(name='set', value='add'), 
    OptionChoice(name='remove', value='rem')
    ], required=True), channelid: Option(discord.TextChannel, "channel ID", required=True)):
    if ctx.author.guild_permissions.administrator:
        if action == 'add':
            try:
                with open('db.json', 'r') as f:
                    welChannels = json.load(f)
                try:
                    if get_welcome_channel(ctx.guild.id) == str(channelid.id):
                        await ctx.respond(
                            f'nothing changed! <#{str(channelid.id)}> is still the welcome channel!'
                        )
                    elif get_welcome_channel(ctx.guild.id) != str(
                            channelid.id):
                        welChannels[str(ctx.guild.id)] = str(channelid.id)
                        with open('db.json', 'w+') as f:
                            json.dump(welChannels, f)
                        await ctx.respond(
                            f'<#{get_welcome_channel(ctx.guild.id)}> now set as the welcome channel!'
                        )
                except:
                    welChannels[str(ctx.guild.id)] = str(channelid.id)
                    with open('db.json', 'w+') as f:
                        json.dump(welChannels, f)
                    await ctx.respond(
                        f'<#{get_welcome_channel(ctx.guild.id)}> now set as the welcome channel!'
                    )
            except json.decoder.JSONDecodeError:
                await ctx.respond(f'error!')

        elif action == 'rem':
            with open('db.json', 'r') as f:
                welChannels = json.load(f)
            try:
                del welChannels[str(ctx.guild.id)]
                with open('db.json', 'w') as f:
                    json.dump(welChannels, f)
                await ctx.respond(f'welcome channel removed!')
            except:
                await ctx.respond(
                    f'no channel was removed because there was no welcome channel!'
                )
        elif action == 'rem':
            pass
    else:
        await ctx.respond('you must be an admin to run this command! ❌', ephemeral=True)

@bot.slash_command(name='goodbye', description='choose the channel to send goodbyes in')
async def _goodbye(ctx, action: Option(str, "add or remove", choices=[
    OptionChoice(name='set', value='add'), 
    OptionChoice(name='remove', value='rem')
    ], required=True), channelid: Option(discord.TextChannel, "channel ID", required=True)):
    if ctx.author.guild_permissions.administrator:
        if action == 'add':
            try:
                with open('byedb.json', 'r') as f:
                    welChannels = json.load(f)
                try:
                    if get_goodbye_channel(ctx.guild.id) == str(channelid.id):
                        await ctx.respond(
                            f'nothing changed! <#{str(channelid.id)}> is still the goodbye channel!'
                        )
                    elif get_goodbye_channel(ctx.guild.id) != str(
                            channelid.id):
                        welChannels[str(ctx.guild.id)] = str(channelid.id)
                        with open('byedb.json', 'w+') as f:
                            json.dump(welChannels, f)
                        await ctx.respond(
                            f'<#{get_goodbye_channel(ctx.guild.id)}> now set as the goodbye channel!'
                        )
                except:
                    welChannels[str(ctx.guild.id)] = str(channelid.id)
                    with open('byedb.json', 'w+') as f:
                        json.dump(welChannels, f)
                    await ctx.respond(
                        f'<#{get_goodbye_channel(ctx.guild.id)}> now set as the goodbye channel!'
                    )
            except json.decoder.JSONDecodeError:
                await ctx.respond(f'error!')

        elif action == 'rem':
            with open('byedb.json', 'r') as f:
                welChannels = json.load(f)
            try:
                del welChannels[str(ctx.guild.id)]
                with open('byedb.json', 'w') as f:
                    json.dump(welChannels, f)
                await ctx.respond(f'goodbye channel removed!')
            except:
                await ctx.respond(
                    f'no channel was removed because there was no goodbye channel!'
                )
        elif action == 'rem':
            pass
    else:
        await ctx.respond('you must be an admin to run this command! ❌', ephemeral=True)

@bot.slash_command(name='uwumode', description='enable or disable uwumode')
async def _goodbye(ctx, state: Option(str, "on or off", choices=[
    OptionChoice(name='on', value='on'), 
    OptionChoice(name='off', value='off')
    ], required=True)):
    if ctx.author.guild_permissions.administrator:
        if state == 'on':
            try:
                with open('uwudb.json', 'r') as f:
                    welChannels = json.load(f)
                try:
                    if get_uwu_state(ctx.guild.id) == 'on':
                        await ctx.respond(
                            f'nothing changed! UwUmode is still enabled! UwU'
                        )
                    elif get_uwu_state(ctx.guild.id) != 'on':
                        welChannels[str(ctx.guild.id)] = 'on'
                        with open('uwudb.json', 'w+') as f:
                            json.dump(welChannels, f)
                        await ctx.respond(
                            f'UwUmode is now enabled! UwU'
                        )
                except:
                    welChannels[str(ctx.guild.id)] = 'on'
                    with open('uwudb.json', 'w+') as f:
                        json.dump(welChannels, f)
                    await ctx.respond(
                        f'UwUmode is now enabled! UwU'
                    )
            except json.decoder.JSONDecodeError:
                await ctx.respond(f'error!')

        elif state == 'off':
            with open('uwudb.json', 'r') as f:
                welChannels = json.load(f)
            try:
                del welChannels[str(ctx.guild.id)]
                with open('uwudb.json', 'w') as f:
                    json.dump(welChannels, f)
                await ctx.respond(f'UwUmode is now disabled! TwT')
            except:
                await ctx.respond(
                    f'UwUmode is still disabled! TwT'
                )
    else:
        await ctx.respond('you must be an admin to run this command! ❌', ephemeral=True)

@bot.slash_command(name='slaydetector',
                   description='check if someone is slaying')
async def _slaydetector(ctx, user: Option(discord.Member, "user to check for slaying", required=False)):
    if user == None: user = ctx.author
    slayOpt = [
        f'Yes, <@{user.id}> is slaying!', f'No, <@{user.id}> is not slaying :<'
    ]
    cuteEmbed = discord.Embed(title=f'Is {user.display_name} slaying?', description=slayOpt[random.randrange(0, len(slayOpt))], color=0x202225)
    cuteEmbed.set_thumbnail(url=user.display_avatar.url)
    cuteEmbed.set_footer(text=f'requested by {ctx.author}', icon_url=f'{ctx.author.avatar.url}'),
    await ctx.respond(embed=cuteEmbed)


@bot.slash_command(name='8ball',
                   description='ask a yes or no question, recieve an answer!')
async def _8ball(ctx, question: Option(str, "yes or no question", required=True)):
    opt = [
        'It is certain', 'Without a doubt', 'You may rely on it',
        'Yes definitely', 'It is decidedly so', 'As I see it, yes',
        'Most likely', 'Yes', 'Outlook good', 'Signs point to yes',
        'Reply hazy, try again', 'Better not tell you now', 'Ask again later',
        'Cannot predict now', 'Concentrate and ask again',
        'Don\'t count on it', 'Outlook not so good', 'My sources say no',
        'Very doubtful', 'My reply is no'
    ]
    if len(question) > 219:
        Embed = discord.Embed(
            title=f'question too long!',
            description=
            f'your question is {len(question)-219} characters too long',
            color=0x202225)
        Embed.set_footer(text=f'requested by {ctx.author}',
                         icon_url=f'{ctx.author.avatar.url}'),
        await ctx.respond(embed=Embed, ephemeral=True)
    else:
        Embed = discord.Embed(title=f'{ctx.author} asks: {question}?', description=f'egirl says: {opt[random.randrange(0, len(opt))]}', color=0x202225)
        Embed.set_footer(text=f'requested by {ctx.author}', icon_url=f'{ctx.author.avatar.url}'),
        await ctx.respond(embed=Embed)

@bot.slash_command(
    name='rp',
    description='show your love or beat people up!'
)
async def _rp(ctx, 
    action: Option(str, 'choose gif', choices = [
        OptionChoice(name='punch', value='punch'), 
        OptionChoice(name='hug', value='hug'), 
        OptionChoice(name='poke', value='poke'),
        OptionChoice(name='tickle', value='tickle'),
        OptionChoice(name='lick', value='lick'),
        OptionChoice(name='kiss', value='kiss'),
        OptionChoice(name='nom', value='nom'),
        OptionChoice(name='pat', value='pat'),
        OptionChoice(name='slap', value='slap'),
        ], required=True), 
    user: Option(discord.Member, 'user to affect', required=True)):
    actionURL = action
    if action == 'punch':
        action = action + 'es'
    elif action == 'kiss':
        action = action + 'es'
    else: 
        action = action + 's'
    credEmbed = discord.Embed(title='', description=f'<@{ctx.author.id}> {action} <@{user.id}>!', color=0x202225)
    credEmbed.set_image(url=requests.get(f'https://api.dbot.dev/images/{actionURL}').json()['url'])
    credEmbed.set_footer(text = f'requested by {ctx.author}', icon_url=ctx.author.avatar.url)
    await ctx.respond(embed=credEmbed)

@bot.slash_command(
    name='solorp',
    description='fall asleep or look smug!'
)
async def _solorp(ctx, 
    action: Option(str, 'choose gif', choices = [
        OptionChoice(name='blush', value='blush'),
        OptionChoice(name='cry', value='cry'), 
        OptionChoice(name='pout', value='pout'),
        OptionChoice(name='sleep', value='sleep'),
        OptionChoice(name='smug', value='smug')
        ], required=True)):
    actionURL = action
    if action == 'blush':
        action = 'blushes'
    elif action == 'cry':
        action = 'cries'
    elif action == 'pout':
        action = 'pouts'
    elif action == 'sleep':
        action = 'goes to sleep'
    elif action == 'smug':
        action = 'acts smug'
    credEmbed = discord.Embed(title='', description=f'<@{ctx.author.id}> {action}', color=0x202225)
    credEmbed.set_image(url=requests.get(f'https://api.dbot.dev/images/{actionURL}').json()['url'])
    credEmbed.set_footer(text = f'requested by {ctx.author}', icon_url=ctx.author.avatar.url)
    await ctx.respond(embed=credEmbed)

@bot.slash_command(
    name='rockpaperscissors',
    description='play rock paper scisors against egirl'
)
async def _rockpaperscissors(ctx, choice: Option(str, 'choose gif', choices = [
    OptionChoice(name='rock 🪨', value='rock'), 
    OptionChoice(name='paper 📄', value='paper'), 
    OptionChoice(name='scissors ✂️', value='scissors')], required=True)):

    egirlChoice = random.randrange(0, 3)
    if egirlChoice == 0:
        egirlChoice = 'rock'
    elif egirlChoice == 1:
        egirlChoice = 'paper'
    elif egirlChoice == 2:
        egirlChoice = 'scissors'

    if choice == egirlChoice:
        playerState = 'tie'
    elif choice != egirlChoice:
        if choice == 'rock':
            if egirlChoice == 'paper':
                playerState = 'lose'
            elif egirlChoice == 'scissors':
                playerState = 'win'
        elif choice == 'paper':
            if egirlChoice == 'rock':
                playerState = 'win'
            elif egirlChoice == 'scissors':
                playerState = 'lose'
        elif choice == 'scissors':
            if egirlChoice == 'rock':
                playerState = 'lose'
            elif egirlChoice == 'paper':
                playerState = 'win'
    if choice == 'rock':
        choice += ' 🪨'
    elif choice == 'paper':
        choice += ' 📄'
    elif choice == 'scissors':
        choice += ' ✂️'
    
    if egirlChoice == 'rock':
        egirlChoice += ' 🪨'
    elif egirlChoice == 'paper':
        egirlChoice += ' 📄'
    elif egirlChoice == 'scissors':
        egirlChoice += ' ✂️'
    
    if playerState == 'lose':
        title = f'egirl wins!'
        body = f'egirl chose {egirlChoice}!\n{ctx.author} chose {choice}!'
    elif playerState == 'win':
        title = f'{ctx.author} wins!'
        body = f'egirl chose {egirlChoice}!\n{ctx.author} chose {choice}!'
    else:
        title = f'it\'s a tie!'
        body = f'both {ctx.author} and egirl chose {egirlChoice}!'
    embed = discord.Embed(title=title, description=body, color=0x202225)
    embed.set_thumbnail(url=f'{ctx.author.display_avatar}')
    embed.set_footer(text = f'challenged by {ctx.author}', icon_url=ctx.author.avatar.url)
    await ctx.respond(embed=embed)

@bot.slash_command(
    name="dog",
    description="random dog image",
)
async def _dog(ctx, breed: Option(str, 'specify breed', choices = [
    OptionChoice(name='corgi'),
    OptionChoice(name='retriever'),
    OptionChoice(name='husky'),
    OptionChoice(name='german shepherd', value='germanshepherd'),
    OptionChoice(name='hound'),
    OptionChoice(name='chihuahua'),
    OptionChoice(name='pug'),
    OptionChoice(name='poodle'),
    OptionChoice(name='terrier'),
    OptionChoice(name='mix'),
    OptionChoice(name='newfoundland'),
    OptionChoice(name='pitbull'),
    OptionChoice(name='pomeranian'),
    OptionChoice(name='rottweiler'),
    OptionChoice(name='dane'),
    OptionChoice(name='sheepdog'),
    OptionChoice(name='dachshund'),
    ], required=False)):

    embed = discord.Embed(title=f'woof!', description='', color=0x202225)

    if breed != None:
        embed.set_image(url=requests.get(f'https://dog.ceo/api/breed/{breed}/images/random/1').json()['message'][0])
    elif breed == None:
        embed.set_image(url=requests.get(f'https://dog.ceo/api/breeds/image/random/1').json()['message'][0])
    embed.set_footer(text=f'requested by {ctx.author}', icon_url=f'{ctx.author.avatar.url}'),
    await ctx.respond(embed=embed)

@bot.slash_command(
    name='hypixel',
    description='get general hypixel stats for a player'
)
async def _hypixel(ctx, player: Option(str, 'username or uuid of player', required=True)):
    try: 
        if requests.get(f'https://api.hypixel.net/key?key={hyToken}').json()['record']['queriesInPastMin'] > 110:
            await ctx.respond('egirl is currently beign ratelimited by the Hypixel API!! ❌')
        else: 
            if len(player) <= 16:
                try: 
                    uuid = requests.get(f'https://api.mojang.com/users/profiles/minecraft/{player}').json()['id']
                except: 
                    await ctx.respond('please choose a valid username or id! ❌', ephemeral = True)
                    return
            elif len(player) > 16:
                uuid = player
            
            request = requests.get(f'https://api.hypixel.net/player?uuid={uuid}&key={hyToken}')
            firstLogin = int(request.json()['player']['firstLogin'] / 1000)
            try:
                lastLogin = int(request.json()['player']['lastLogin'] / 1000)
                lastLogout = int(request.json()['player']['lastLogout'] / 1000)
                lastLoginStr = f'<t:{lastLogin}:D>'
                if lastLogin > lastLogout:
                    onlineStatus = 'Online 🟢'
                elif lastLogin < lastLogout:
                    onlineStatus = 'Offline 🔴'
            except:
                lastLoginStr = 'Unknown ❓'
                onlineStatus = 'Unknown ❓'
            networkLevel = int((math.sqrt((2 * request.json()['player']['networkExp']) + 30625) / 50) - 2.5)
            try:
                rank = request.json()['player']['newPackageRank']
            except: 
                rank = 'non'
            if rank == 'VIP':
                rank = '[VIP]'
            elif rank == 'VIP_PLUS':
                rank = '[VIP+]'
            elif rank == 'MVP':
                rank = '[MVP]'
            elif rank == 'MVP_PLUS':
                try: 
                    plusRequest = request.json()['player']['rankPlusColor']
                    if plusRequest == 'GOLD': plusColor = '<:gold_plus:1009339993325584394>'
                    elif plusRequest == 'GREEN': plusColor = '<:green_plus:1009339994319634512>'
                    elif plusRequest == 'YELLOW': plusColor = '<:yellow_plus:1009339983900975216>'
                    elif plusRequest == 'LIGHT_PURPLE': plusColor = '<:light_purple_plus:1009339995166867518>'
                    elif plusRequest == 'WHITE': plusColor = '<:white_plus:1009339997335326740>'
                    elif plusRequest == 'BLUE': plusColor = '<:blue_plus:1009339985683546149>'
                    elif plusRequest == 'DARK_GREEN': plusColor = '<:dark_green_plus:1009339990297292871>'
                    elif plusRequest == 'DARK_RED': plusColor = '<:dark_red_plus:1009339992151175220>'
                    elif plusRequest == 'DARK_AQUA': plusColor = '<:dark_aqua_plus:1009339987101237309>'
                    elif plusRequest == 'DARK_PURPLE': plusColor = '<:dark_purple_plus:1009339991261978684>'
                    elif plusRequest == 'DARK_GRAY': plusColor = '<:dark_gray_plus:1009339989269696512>'
                    elif plusRequest == 'BLACK': plusColor = '<:black_plus:1009339985079566447>'
                    elif plusRequest == 'DARK_BLUE': plusColor = '<:dark_blue_plus:1009339987843612744>'
                except: 
                    plusColor = '<:red_plus:1009339996379021312>'
                rank = f'[MVP {plusColor} ]'
            try:
                if request.json()['player']['monthlyPackageRank'] == 'SUPERSTAR':
                    try: 
                        plusRequest = request.json()['player']['rankPlusColor']
                        if plusRequest == 'GOLD': plusColor = '<:gold_plus:1009339993325584394>'
                        elif plusRequest == 'GREEN': plusColor = '<:green_plus:1009339994319634512>'
                        elif plusRequest == 'YELLOW': plusColor = '<:yellow_plus:1009339983900975216>'
                        elif plusRequest == 'LIGHT_PURPLE': plusColor = '<:light_purple_plus:1009339995166867518>'
                        elif plusRequest == 'WHITE': plusColor = '<:white_plus:1009339997335326740>'
                        elif plusRequest == 'BLUE': plusColor = '<:blue_plus:1009339985683546149>'
                        elif plusRequest == 'DARK_GREEN': plusColor = '<:dark_green_plus:1009339990297292871>'
                        elif plusRequest == 'DARK_RED': plusColor = '<:dark_red_plus:1009339992151175220>'
                        elif plusRequest == 'DARK_AQUA': plusColor = '<:dark_aqua_plus:1009339987101237309>'
                        elif plusRequest == 'DARK_PURPLE': plusColor = '<:dark_purple_plus:1009339991261978684>'
                        elif plusRequest == 'DARK_GRAY': plusColor = '<:dark_gray_plus:1009339989269696512>'
                        elif plusRequest == 'BLACK': plusColor = '<:black_plus:1009339985079566447>'
                        elif plusRequest == 'DARK_BLUE': plusColor = '<:dark_blue_plus:1009339987843612744>'
                    except: 
                        plusColor = '<:red_plus:1009339996379021312>'
                    rank = f'[MVP {plusColor} {plusColor} ]'
            except KeyError: 
                pass
            if rank == 'non':
                rank = ''
            if request.json()['success'] == True:
                embed = discord.Embed(title=rank + ' ' + request.json()['player']['displayname'] + '\'s Stats', description=f'\
                    **Current Status:** {onlineStatus}\n\
                    **First Login:** <t:{firstLogin}:D>\n\
                    **Last Login:** {lastLoginStr}\n\
                    **Network Level:** {networkLevel}', color=0x202225)
                embed.set_thumbnail(url=f'https://minotar.net/helm/{uuid}')
                await ctx.respond(embed=embed)
                
            else: 
                await ctx.respond('please choose a valid username or id! ❌', ephemeral = True)
    except: await ctx.respond('failed to reach Hypixel API! ❌')

@bot.slash_command(
    name="cat",
    description="random cat image",
)
async def _cat(ctx):
    embed = discord.Embed(title=f'meow!', description='', color=0x202225)
    embed.set_image(url=requests.get(f'https://api.thecatapi.com/v1/images/search').json()[0]['url'])
    embed.set_footer(text=f'requested by {ctx.author}', icon_url=f'{ctx.author.avatar.url}'),
    await ctx.respond(embed=embed)

@bot.slash_command(
    name="howboopable",
    description="check someone's cuteness",
)
async def _howboopable(ctx, user: Option(discord.Member, "choose who to check boopability for", required=False)):
    if user == None: user = ctx.author
    opt = [
        '☆☆☆☆☆☆☆☆☆☆\n0/10 Boopability',
        '★☆☆☆☆☆☆☆☆☆\n1/10 Boopability',
        '★★☆☆☆☆☆☆☆☆\n2/10 Boopability',
        '★★★☆☆☆☆☆☆☆\n3/10 Boopability',
        '★★★★☆☆☆☆☆☆\n4/10 Boopability',
        '★★★★★☆☆☆☆☆\n5/10 Boopability',
        '★★★★★★☆☆☆☆\n6/10 Boopability',
        '★★★★★★★☆☆☆\n7/10 Boopability',
        '★★★★★★★★☆☆\n8/10 Boopability',
        '★★★★★★★★★☆\n9/10 Boopability',
        '★★★★★★★★★★\n10/10 Boopability',
    ]
    R = random.randrange(0, len(opt))
    embed = discord.Embed(title=f'How boopable is {user}?', description=opt[R], color=0x202225)
    embed.set_thumbnail(url=user.display_avatar.url)
    embed.set_footer(text=f'requested by {ctx.author}', icon_url=f'{ctx.author.avatar.url}'),
    await ctx.respond(embed=embed)

@bot.slash_command(
    name="tod",
    description="truth or dare",
)
async def _tod(ctx, question: Option(str, 'choose between truth or dare', choices=[
    OptionChoice(name='truth'), 
    OptionChoice(name='dare'),
    OptionChoice(name='Surprise Me!', value='surprise_me')
    ], required=True),):

    truths = ['When was the last time you lied?',
    'When was the last time you cried?',
    'What\'s your biggest fear?',
    'What\'s your biggest fantasy?',
    'What\'s something you\'re glad your mum doesn\'t know about you?',
    'What\'s the worst thing you\'ve ever done?',
    'What\'s a secret you\'ve never told anyone?',
    'Do you have a hidden talent?',
    'Who was your first celebrity crush?',
    'Have you ever cheated in an exam?',
    'Have you ever broken the law?',
    'What\'s your biggest insecurity?',
    'What\'s the biggest mistake you\'ve ever made?',
    'What\'s the most disgusting thing you\'ve ever done?',
    'Who would you like to kiss right now?',
    'What\'s the worst thing anyone\'s ever done to you?',
    'What\'s your worst habit?',
    'What\'s the worst thing you\'ve ever said to anyone?',
    'What\'s the strangest dream you\'ve had?',
    'What\'s the worst date you\'ve been on?',
    'What\'s your biggest regret?',
    'What\'s the biggest misconception about you?',
    'Have you ever lied to get out of a bad date?',
    'What\'s the most trouble you\'ve been in? ',
    'What is a weird food that you love?',
    'What terrible movie or show is your guilty pleasure?',
    'What is the worst grade you received for a class in school/college?',
    'What is the biggest lie you\'ve ever told?',
    'Have you ever broken an expensive item?',
    'What is one thing you\'d change about your appearance if you could?',
    'If you suddenly had a million dollars, how would you spend it?',
    'Who is the best teacher you\'ve ever had and why?',
    'What is the worst food you\'ve ever tasted?',
    'What is the weirdest way you\'ve met someone you now consider a close friend?',
    'What is the most embarrassing thing you\'ve posted on social media?',
    'Have you ever revealed a friend\'s secret to someone else?',
    'If you could only eat one meal for the rest of your life, what would it be?',
    'What is your favorite book of all time?',
    'What is the last text message you sent your best friend?',
    'What is something you would do if you knew there were no consequences?',
    'What is the worst physical pain you\'ve ever been in?',
    'Personality-wise, are you more like your mom or your dad?',
    'When is the last time you apologized (and what did you do)?',
    'If your house caught on fire and you could only save three things (besides people), what would they be?',
    'If you could pick one other player to take with you to a deserted island, who would it be?',
    'Have you ever stolen anything?',
    'Have you ever been kicked out of a store, restaurant, bar, event, etc.?',
    'What is the weirdest thing you\'ve ever done in public?',
    'What is the last excuse you used to cancel plans?',
    'What is the biggest mistake you\'ve ever made at school or work?',
    'Which player would survive the longest in a horror/apocalypse movie, and who would be the first one to die?',
    'What is the dirtiest room/area of your house?',
    'Which of your family members annoys you the most?',
    'When is the last time you made someone else cry?',
    'What is the longest you\'ve ever gone without showering?',
    'If you could pick anyone in the world to be president, who would you choose?',
    'Do you pee in pools?',
    'If someone went through your closet, what is the weirdest thing they\'d find?',
    'Have you ever lied about your age?',
    'Besides your phone, what\'s the one item in your house you couldn\'t live without?',
    'What is the biggest fight you\'ve ever been in with a friend?']

    dares = ['Show the most embarrassing photo on your phone',
    'Show the last five people you texted and what the messages said',
    'Do 100 squats',
    'Say something dirty to the person on your left',
    'Yell out the first word that comes to your mind',
    'Empty out your wallet/purse and show everyone what\'s inside',
    'Try and make the group laugh as quickly as possible',
    'Try to put your whole fist in your mouth',
    'Tell everyone an embarrassing story about yourself',
    'Try to lick your elbow',
    'Read the last text message you sent out loud.',
    'Show the weirdest item you have in your purse/pockets.',
    'Speak in an Australian accent until your next turn.',
    'Narrate the game in a newscaster voice for three turns.',
    'Show the most embarrassing photo on your phone.',
    'Meow.',
    'Nya. ',
    'Talk like an anime girl until your next turn',
    'Show the group your internet search history.',
    'Let another player choose your status.',
    'Do an impression of another player until someone can figure out who it is.',
    'Act like a chicken until your next turn.',
    'Eat a packet of hot sauce or ketchup straight.',
    'Spin around 12 times and try to walk straight. ',
    'Pretend to be a squirrel until your next turn.',
    'Quack like a duck until your next turn.',
    'Sing the national anthem in a British accent.',
    'Talk in a surfer voice until your next turn',
    'Read out the last dirty text you sent',
    'Pretend to be a food item of your choice',
    'Show the group your screen time report',
    'Keep three ice cubes in your mouth until they melt',
    'Keep your eyes closed until it\'s your turn again',
    'Whisper a secret to the person on your left',
    'Scroll through your contacts until someone says stop. You either have to call or delete that person.',
    'Tell the group two truths and a lie, and they have to guess which one the lie is',
    'Smile as widely as you can and hold it for two minutes',
    'Sit on the floor for the rest of the evening',
    'Put on make-up without a mirror and leave it like that for the rest of the game',
    'Give a personalised insult to everyone in the room',
    'For the next 10 minutes, every time someone asks you something, respond with a bark',
    'Let the person next to you wax you wherever they want']

    if question == 'truth':
        qod = truths[random.randrange(0, len(truths))]
        qodB = 'Truth: '
    elif question == 'dare':
        qod = dares[random.randrange(0, len(dares))]     
        qodB = 'Dare: '   
    elif question == 'surprise_me': 
        rng = random.randrange(0, 1)
        if rng == 0: 
            qod = truths[random.randrange(0, len(truths))]
            qodB = 'Truth: '
        elif rng == 1:
            qod = dares[random.randrange(0, len(dares))]
            qodB = 'Dare: '  

    embed = discord.Embed(title=f'egirl\'s Truth or Dare', description=f'{qodB}{qod}', color=0x202225)
    embed.set_footer(text=f'requested by {ctx.author}', icon_url=f'{ctx.author.avatar.url}'),
    await ctx.respond(embed=embed)

@bot.slash_command(name='uwuifier', description='uwuify some text')
async def _uwuifier(ctx, text: Option(str, 'text to uwuify', required=True), send_as_user: Option(bool, 'send message as clone of user', required=False, default=True)):
    text1 = text.replace('l','w')
    text1 = text1.replace('L','W')
    text1 = text1.replace('r','w')
    text1 = text1.replace('R','W')
    text1 = text1.replace('th','d')
    text1 = text1.replace('Th','D')
    text1 = text1.replace('tH','D')
    embed = discord.Embed(title=f'egirl\'s UwUifier', description=f'\u200b', color=0x202225)
    embed.set_thumbnail(url=bot.user.avatar.url)
    embed.add_field(name=f'Old Text', value=f'{text}', inline=False)
    embed.add_field(name=f'UwUified Text', value=f'{text1}', inline=False)
    try:
        if send_as_user == True:
            await ctx.respond(embed=embed, ephemeral=True)
            webhook = await ctx.channel.create_webhook(name=ctx.author.name)
            await webhook.send(f'{text1}', username=ctx.author.nick, avatar_url=ctx.author.avatar.url)
            webhooks = await ctx.channel.webhooks()
            for webhook in webhooks:
                    await webhook.delete()
        if send_as_user == False:
            await ctx.respond(embed=embed, ephemeral=True)
    except: await ctx.respond('UwUification failed! Perhaps your message is too long?', ephemeral=True)

@bot.slash_command(name='nuke', description='hide or completely delete a channel')
async def _nuke(ctx, 
    channel: Option(discord.TextChannel, 'choose the channel to nuke', required=True), 
    archive: Option(bool, 'choose weather to archive or delete channel', required=False, default=True)):
    if ctx.author.guild_permissions.administrator:
        guild = ctx.guild
        if archive == True:
            perms = channel.overwrites_for(ctx.guild.default_role)
            newChannel = await guild.create_text_channel(name=channel.name, category=channel.category, position=channel.position, topic=channel.topic, slowmode_delay=channel.slowmode_delay, nsfw=channel.slowmode_delay, overwrites=channel.overwrites)
            perms.view_channel = False
            await channel.set_permissions(ctx.guild.default_role, overwrite=perms)
            nukeTime = str(time.time()).split('.')[0]
            embed = discord.Embed(title=f'', description=f'<#{channel.id}> archived by {ctx.author.mention} on <t:{nukeTime}:f>', color=0x202225)
            await channel.send(f'channel archived!', embed=embed)
            await ctx.respond(f'done!', ephemeral=True)
        if archive == False:
            perms = channel.overwrites_for(ctx.guild.default_role)
            newChannel = await guild.create_text_channel(name=channel.name, category=channel.category, position=channel.position, topic=channel.topic, slowmode_delay=channel.slowmode_delay, nsfw=channel.slowmode_delay, overwrites=channel.overwrites)
            await channel.delete()
            await ctx.respond(f'done!', ephemeral=True)
    else:
        await ctx.respond('You must be an administrator to nuke channels! ❌', ephemeral=True)

@bot.slash_command(name='kick', description='kick a member')
async def _kick(ctx, member: Option(discord.Member, 'choose member to kick', required=True), reason: Option(str, 'reason displayed in audit log', required=True)):
    if ctx.author.guild_permissions.administrator:
        try:
            await member.ban(reason=reason)
            await member.kick()
            await ctx.respond(f'**{member}** was kicked! ✅', ephemeral=True)
        except:
            await ctx.respond(f'Failed to kick **{member}**, is their role higher than egirl\'s? Are they in the server? ❌', ephemeral=True)
    else:
        await ctx.respond('You must be an administrator to kick members! ❌', ephemeral=True)

@bot.slash_command(name='ban', description='ban a member')
async def _ban(ctx, member: Option(discord.Member, 'choose member to ban', required=True), reason: Option(str, 'reason displayed in audit log', required=True)):
    if ctx.author.guild_permissions.administrator:
        try:
            await member.ban(reason=reason)
            await ctx.respond(f'**{member}** was banned! ✅', ephemeral=True)
        except:
            await ctx.respond(f'Failed to ban **{member}**, is their role higher than egirl\'s? Are they in the server? ❌', ephemeral=True)
    else:
        await ctx.respond('You must be an administrator to ban members! ❌', ephemeral=True)

@bot.slash_command(name='qotd', description='random qotd')
async def _qotd(ctx, role: Option(discord.Role, 'choose qotd role', required=False, default=None), channel: Option(discord.TextChannel, 'choose text channel to send qotd', required=False, default=None)):
    await ctx.response.send_message('thinking... 🕐', ephemeral=True)
    res = requests.get('https://chillihero.api.stdlib.com/qotd@0.1.3/question/').json()
    if role == None:
        mention = ''
    else:
        mention = role.mention
    embed = discord.Embed(title=f'egirl\'s Question of The Day', description=res, color=0x202225)
    embed.set_thumbnail(url='https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/twitter/322/question-mark_2753.png')
    if channel == None:
        await ctx.channel.send(mention, embed=embed)
        await ctx.edit(content='done! ✅')
    else:
        await channel.send(mention, embed=embed)
        await ctx.edit(content='done! ✅')

@bot.slash_command(name='poll', description='random qotd')
async def _poll(ctx, question: Option(str, 'poll question', required=True)):
    await ctx.response.send_message('thinking... 🕐', ephemeral=True)
    if question[len(question)-1:] == '?':
        pass
    else:
        question += '?'
    embed = discord.Embed(title=f'Poll', description=question, color=0x202225)
    embed.set_footer(text=f'asked by {ctx.author}', icon_url=f'{ctx.author.avatar.url}'),
    message = await ctx.channel.send(embed=embed)
    await message.add_reaction(":yes:1041920497216143420")
    await message.add_reaction(":no:1041920495542612101")
    await ctx.edit(content='sent! ✅')

@bot.slash_command(name='reportissue', description='report an issue with egirl')
async def _reportissue(ctx, title: Option(str, 'report title', required=True), report: Option(str, 'describe issue', required=True)):
    global reportLock
    if ctx.author.id in reportLock:
        await ctx.respond(f'You have reported an issue too recently, try again in a few minutes! ❌', ephemeral = True)
    else:
        if len(title) > 248:
            await ctx.respond(f'Report failed! Your title is {len(title)-248} characters too long! ❌', ephemeral = True)
        elif len(report) > 1024:
            await ctx.respond(f'Report failed! Your description is {len(report)-1024} characters too long! ❌', ephemeral = True)
        else: 
            manager = bot.get_user(reportManager)
            embed = discord.Embed(title=f'Report: {title}', description=report, color=0x202225)
            embed.set_author(name=f'Report filed by {ctx.author}', icon_url=f'{ctx.author.avatar.url}')
            await manager.send(embed=embed)
            await ctx.respond('Report sent! Thanks for helping improve egirl! ✅', ephemeral = True)
            await bot.get_channel(loggingChannel).send(f'<@{reportManager}>! report filed!')
            reportLock.append(ctx.author.id)

bot.run(TOKEN)