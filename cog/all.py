import asyncio, glob, json, math, os, random, time, dice, gtts
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
ttsban = {}

class cog_all(commands.Cog):
    def __init__(self, bot, *args, **kwargs):
        self.bot = bot
        self.eliban = False

    @commands.Cog.listener()
    async def on_connect(self):
        try: 
            self.stat_task.start()
            print('started stat_task()')
        except Exception as e: print(f'error starting stat_task()\ne: {e}')
        try: 
            self.wipeReportBan.start()
            print('started wipeReportBan()')
        except Exception as e: print(f'error starting wipeReportBan()\ne: {e}')
        try: 
            self.pfp_task.start()
            print('started pfp_task()')
        except Exception as e: print(f'error starting pfp_task()\ne: {e}')
        try: 
            self.topggStats.start()
            print('started topggStats()')
        except Exception as e: print(f'error starting topggStats()\ne: {e}')
        #self.bot.topggpy = topgg.DBLClient(self.bot, topggToken, autopost=True, post_shard_count=False)

    @tasks.loop(minutes=30)
    async def pfp_task(self):
        try:
            aviArray = glob.glob('./images/*.jpg')
            randAvi = random.randrange(0, len(aviArray))
            fileProfileImage = open(aviArray[randAvi], 'rb')
            pfp = fileProfileImage.read()
            await self.bot.user.edit(avatar=pfp)
        except discord.errors.HTTPException:
            print('bot avatar failed to update due to ratelimit. retrying in 10 minutes.')


    @tasks.loop(seconds=0)
    async def stat_task(self):
        await self.bot.change_presence(status=discord.Status.online, activity=discord.Game('minecraft'))
        await asyncio.sleep(30)
        await self.bot.change_presence(status=discord.Status.online, activity=discord.Game('really loud music'))
        await asyncio.sleep(30)
        await self.bot.change_presence(status=discord.Status.online, activity=discord.Game('with a pile of teeth'))
        await asyncio.sleep(30)
        await self.bot.change_presence(status=discord.Status.online, activity=discord.Game('with the /help command'))
        await asyncio.sleep(30)
        await self.bot.change_presence(status=discord.Status.online, activity=discord.Game('my favorite color is #202225'))
        await asyncio.sleep(30)
        await self.bot.change_presence(status=discord.Status.online, activity=discord.Game('#girlboss'))
        await asyncio.sleep(30)
        await self.bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.listening, name="egirl asmr"))
        await asyncio.sleep(30)
        await self.bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.competing, name="egirl contests?"))
        await asyncio.sleep(30)
        await self.bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.listening, name="girlboss podcasts"))
        await asyncio.sleep(30)

    @tasks.loop(minutes=10)
    async def wipeReportBan(self):
        global reportLock
        reportLock = []

    @tasks.loop(minutes=30)
    async def topggStats(self):
        self.bot.topggpy = topgg.DBLClient(bot=self.bot, token=topggToken)
        try:
            await self.bot.topggpy.post_guild_count(guild_count=len(self.bot.guilds))
            print(f"updated guild count: ({self.bot.topggpy.guild_count})")
        except Exception as e:
            if e == 'Top.gg API token not provided': print('no topgg token')
            else: print(f"encountered whoopsie when posting server count (top.gg)\nerror: {e}")
        await self.bot.topggpy.close()

    @commands.slash_command(name="message", description="embed message")
    async def _message(
        self, ctx,
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
            msgEmbed.set_footer(text=f'egirl embed', icon_url=self.bot.user.display_avatar.url)
            msgEmbed.set_thumbnail(url=thumbnail)
            msgEmbed.set_image(url=setimg)
            try:
                await ctx.channel.send(embed=msgEmbed)
                await ctx.respond('Message Sent ✅', ephemeral=True)
            except discord.errors.HTTPException:
                await ctx.respond('Failed to embed message! At least one image URL is not valid! ❌', ephemeral=True)
        else:
            await ctx.respond('You must be an administrator to embed messages! ❌', ephemeral=True)

    @commands.slash_command(name="editmessage", description="edit embeded message")
    async def _editmessage(
        self, ctx,
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
                channel = self.bot.get_channel(int(channelid))
                grabbedMessage = await channel.fetch_message(int(messageid))
            except ValueError:
                await ctx.respond('Please enter a valid channel and message ID! ❌', ephemeral=True)
                return
            try:
                embedDL = grabbedMessage.embeds[0].to_dict()
                if embedDL['footer']['text'] != 'egirl embed':
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
            msgEmbed.set_footer(text=f'egirl', icon_url=self.bot.user.display_avatar.url)
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

    @commands.slash_command(
        name="howcute",
        description="check someone's cuteness",
    )
    async def _howcute(self, ctx, user: Option(discord.Member, "choose who to check cuteness for", required=False)):
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
        embed = discord.Embed(title=f'How cute is {user}?', description=cuteOpt[cuteR], color=0x202225)
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.set_footer(text=f'{self.bot.user.name} • ©{reportManagerName}', icon_url=f'{self.bot.user.avatar.url}')
        await ctx.respond(embed=embed)


    @commands.slash_command(
        name="possum",
        description="random possum image",
    )
    async def _possum(self, ctx):
        embed = discord.Embed(title=f'<possum screaming>', url='https://possum-cc.github.io/', description='', color=0x202225)
        embed.set_image(url=requests.get('https://ignpoppyseed.pythonanywhere.com/random').json()['url'])
        embed.set_footer(text=f'{self.bot.user.name} • ©{reportManagerName}', icon_url=f'{self.bot.user.avatar.url}')
        await ctx.respond(embed=embed)

    @commands.slash_command(
        name="miner",
        description="grab skin related images of minecraft user",
    )
    async def _miner(self, ctx, username: Option(str, "target username", required=True), type: Option(str, "what to retrive (default: head)", required=True, default='helm', choices=[
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
            embed = discord.Embed(title=f'{username}\'s Skin', description='', color=0x202225)
            embed.set_image(url='https://minotar.net/skin/' + username + '.png')
            embed.set_footer(text=f'{self.bot.user.name} • ©{reportManagerName}', icon_url=f'{self.bot.user.avatar.url}')
            await ctx.respond(embed=embed)
        else:
            embed = discord.Embed(title=f'{username}\'s {titleName}', description='', color=0x202225)
            embed.set_image(url='https://minotar.net/' + type + '/' + username + '/' + str(size) + '.png')
            embed.set_footer(text=f'{self.bot.user.name} • ©{reportManagerName}', icon_url=f'{self.bot.user.avatar.url}')
            await ctx.respond(embed=embed)

    @commands.slash_command(name="vs", description="stage a battle between two users!",)
    async def _vs(self, ctx, player1: Option(discord.Member, "player 1", required=True), player2: Option(discord.Member, "player 2", required=True),):
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

    @commands.slash_command(name='help', description='bot help')
    async def _help(self, ctx):
        embed = discord.Embed(title="egirl's Help Menu",
        description= "**[invite !](https://cloverbrand.xyz/egirl/invite/)** | **[website !](https://cloverbrand.xyz)** | **[vote !](https://top.gg/bot/825415772075196427/vote)**",
        color = 0x202225)
        embed.add_field(name = "utility", value = "```\n- message\n- editmessage\n- nuke\n- kick\n- ban\n- nick set\n- nick reset\n- poll\n- qotd\n- profile\n- passwordgenerator\n- texttospeech\n- lyrics```", inline = True)
        embed.add_field(name = "fun", value = "```\n- rp\n- 8ball\n- slaydetector\n- howcute\n- vs\n- rockpaperscissors\n- howboopable\n- wyr\n- nhie\n- tod\n- animatedstorytitle\n- jortsweather\n- ip-gen```", inline = True)
        embed.add_field(name = "other", value = "```\n- miner\n- hypixel\n- flip\n- roll expression\n- roll help\n- choose\n- formatting\n- gn-chat\n- gm-chat\n- emoji get\n- character-counter\n- word-counter```", inline = True)
        embed.add_field(name = "egirl", value = "```\n- egirl\n- help\n- invite\n- reportissue```", inline = True)
        embed.add_field(name = "config", value = "```\n- config welcome\n- config goodbye\n- config uwumode```", inline = True)
        embed.add_field(name = "images", value = "```\n- possum\n- dog\n- cat\n- imagegen clyde\n- imagegen tweet\n- imagegen ip-fortune-cookie```", inline = True)
        embed.set_footer(text=f'{self.bot.user.name} • ©{reportManagerName}', icon_url=f'{self.bot.user.avatar.url}')
        await ctx.respond(embed=embed)

    @commands.slash_command(name='egirl', description='bot info')
    async def _egirl(self, ctx):
        embed = discord.Embed(title='about egirl', url='https://cloverbrand.xyz/egirl/', color=0x202225)
        embed.add_field(name=f'running egirl v{egirlVersion}', value=
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
        embed.add_field(name=f'extra', value=f'{tip[random.randrange(0, len(tip))]}', inline=False)
        embed.set_footer(text=f'{self.bot.user.name} • ©{reportManagerName}', icon_url=f'{self.bot.user.avatar.url}')
        await ctx.respond(embed=embed)

    @commands.slash_command(name='invite', description='invite egirl to your server')
    async def _invite(self, ctx):
        embed = discord.Embed(title='invite egirl', url='https://discord.com/api/oauth2/authorize?client_id=825415772075196427&permissions=8&scope=bot%20applications.commands', description='invite egirl if you want to be cool', color=0x202225)
        embed.set_footer(text=f'{self.bot.user.name} • ©{reportManagerName}', icon_url=f'{self.bot.user.avatar.url}')
        await ctx.respond(embed=embed)

    @commands.slash_command(name='slaydetector', description='check if someone is slaying')
    async def _slaydetector(self, ctx, user: Option(discord.Member, "user to check for slaying", required=False)):
        if user == None: user = ctx.author
        slayOpt = [
            f'Yes, <@{user.id}> is slaying!', f'No, <@{user.id}> is not slaying :<'
        ]
        embed = discord.Embed(title=f'Is {user.display_name} slaying?', description=slayOpt[random.randrange(0, len(slayOpt))], color=0x202225)
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.set_footer(text=f'{self.bot.user.name} • ©{reportManagerName}', icon_url=f'{self.bot.user.avatar.url}')
        await ctx.respond(embed=embed)

    @commands.slash_command(name='8ball', description='ask a yes or no question, recieve an answer!')
    async def _8ball(self, ctx, question: Option(str, "yes or no question", required=True)):
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
            embed = discord.Embed(title=f'question too long!', description=f'your question is {len(question)-219} characters too long', color=0x202225)
            embed.set_footer(text=f'requested by {ctx.author}', icon_url=f'{ctx.author.avatar.url}'),
            await ctx.respond(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed(title=f'{ctx.author} asks: {question}?', description=f'egirl says: {opt[random.randrange(0, len(opt))]}', color=0x202225)
            embed.set_footer(text=f'{self.bot.user.name} • ©{reportManagerName}', icon_url=f'{self.bot.user.avatar.url}')
            await ctx.respond(embed=embed)

    roleplay = discord.SlashCommandGroup("rp", "roleplay cmds")

    @roleplay.command(name='punch', description='punch someone')
    async def _rp_punch(self, ctx, user: Option(discord.Member, 'user to punch', required=True)):
        embed = discord.Embed(title='', description=f'<@{ctx.author.id}> punches <@{user.id}>!', color=0x202225)
        embed.set_image(url=requests.get(f'{roleplay_api}punch').json()['url'])
        embed.set_footer(text=f'{self.bot.user.name} • ©{reportManagerName}', icon_url=f'{self.bot.user.avatar.url}')
        await ctx.respond(embed=embed)

    @roleplay.command(name='hug', description='hug someone')
    async def _rp_hug(self, ctx, user: Option(discord.Member, 'user to hug', required=True)):
        embed = discord.Embed(title='', description=f'<@{ctx.author.id}> hugs <@{user.id}>!', color=0x202225)
        embed.set_image(url=requests.get(f'{roleplay_api}hug').json()['url'])
        embed.set_footer(text=f'{self.bot.user.name} • ©{reportManagerName}', icon_url=f'{self.bot.user.avatar.url}')
        await ctx.respond(embed=embed)

    @roleplay.command(name='poke', description='poke someone')
    async def _rp_poke(self, ctx, user: Option(discord.Member, 'user to poke', required=True)):
        embed = discord.Embed(title='', description=f'<@{ctx.author.id}> pokes <@{user.id}>!', color=0x202225)
        embed.set_image(url=requests.get(f'{roleplay_api}poke').json()['url'])
        embed.set_footer(text=f'{self.bot.user.name} • ©{reportManagerName}', icon_url=f'{self.bot.user.avatar.url}')
        await ctx.respond(embed=embed)

    @roleplay.command(name='tickle', description='tickle someone')
    async def _rp_tickle(self, ctx, user: Option(discord.Member, 'user to tickle', required=True)):
        embed = discord.Embed(title='', description=f'<@{ctx.author.id}> tickles <@{user.id}>!', color=0x202225)
        embed.set_image(url=requests.get(f'{roleplay_api}tickle').json()['url'])
        embed.set_footer(text=f'{self.bot.user.name} • ©{reportManagerName}', icon_url=f'{self.bot.user.avatar.url}')
        await ctx.respond(embed=embed)

    @roleplay.command(name='lick', description='lick someone')
    async def _rp_lick(self, ctx, user: Option(discord.Member, 'user to lick', required=True)):
        embed = discord.Embed(title='', description=f'<@{ctx.author.id}> licks <@{user.id}>!', color=0x202225)
        embed.set_image(url=requests.get(f'{roleplay_api}lick').json()['url'])
        embed.set_footer(text=f'{self.bot.user.name} • ©{reportManagerName}', icon_url=f'{self.bot.user.avatar.url}')
        await ctx.respond(embed=embed)

    @roleplay.command(name='kiss', description='kiss someone')
    async def _rp_kiss(self, ctx, user: Option(discord.Member, 'user to AAAA', required=True)):
        embed = discord.Embed(title='', description=f'<@{ctx.author.id}> kisses <@{user.id}>!', color=0x202225)
        embed.set_image(url=requests.get(f'{roleplay_api}kiss').json()['url'])
        embed.set_footer(text=f'{self.bot.user.name} • ©{reportManagerName}', icon_url=f'{self.bot.user.avatar.url}')
        await ctx.respond(embed=embed)

    @roleplay.command(name='bite', description='bite someone')
    async def _rp_bite(self, ctx, user: Option(discord.Member, 'user to bite', required=True)):
        load_dotenv()
        tenorToken = os.getenv('TENOR')
        query, limit = 'anime bite', '10'
        try:
            res = requests.get(f'https://tenor.googleapis.com/v2/search?q={query}&limit={limit}&random=true&media_filter=gif&key={tenorToken}').json()['results'][0]['media_formats']['gif']['url']
            embed = discord.Embed(title='', description=f'<@{ctx.author.id}> bites <@{user.id}>!', color=0x202225)
            embed.set_image(url=res)
            embed.set_footer(text=f'{self.bot.user.name} • ©{reportManagerName}', icon_url=f'{self.bot.user.avatar.url}')
            await ctx.respond(embed=embed)
        except Exception as e:
            embed = discord.Embed(title=discord.Embed.Empty, description=f'**TenorAPI Inaccessible**: {e}\nUse </reportissue:1041952478540877826> or contact the developer!')
            embed.set_footer(text=f'{self.bot.user.name} • ©{reportManagerName}', icon_url=f'{self.bot.user.avatar.url}')
            await ctx.respond(embed=embed)

    @roleplay.command(name='pat', description='pat someone')
    async def _rp_pat(self, ctx, user: Option(discord.Member, 'user to pat', required=True)):
        embed = discord.Embed(title='', description=f'<@{ctx.author.id}> pats <@{user.id}>!', color=0x202225)
        embed.set_image(url=requests.get(f'{roleplay_api}pat').json()['url'])
        embed.set_footer(text=f'{self.bot.user.name} • ©{reportManagerName}', icon_url=f'{self.bot.user.avatar.url}')
        await ctx.respond(embed=embed)

    @roleplay.command(name='slap', description='slap someone')
    async def _rp_slap(self, ctx, user: Option(discord.Member, 'user to slap', required=True)):
        embed = discord.Embed(title='', description=f'<@{ctx.author.id}> slaps <@{user.id}>!', color=0x202225)
        embed.set_image(url=requests.get(f'{roleplay_api}slap').json()['url'])
        embed.set_footer(text=f'{self.bot.user.name} • ©{reportManagerName}', icon_url=f'{self.bot.user.avatar.url}')
        await ctx.respond(embed=embed)

    @roleplay.command(name='blush', description='blush')
    async def _rp_blush(self, ctx):
        embed = discord.Embed(title='', description=f'<@{ctx.author.id}> blushes', color=0x202225)
        embed.set_image(url=requests.get(f'{roleplay_api}blush').json()['url'])
        embed.set_footer(text=f'{self.bot.user.name} • ©{reportManagerName}', icon_url=f'{self.bot.user.avatar.url}')
        await ctx.respond(embed=embed)

    @roleplay.command(name='cry', description='cry')
    async def _rp_cry(self, ctx):
        embed = discord.Embed(title='', description=f'<@{ctx.author.id}> cries', color=0x202225)
        embed.set_image(url=requests.get(f'{roleplay_api}cry').json()['url'])
        embed.set_footer(text=f'{self.bot.user.name} • ©{reportManagerName}', icon_url=f'{self.bot.user.avatar.url}')
        await ctx.respond(embed=embed)

    @roleplay.command(name='pout', description='pout')
    async def _rp_pout(self, ctx):
        embed = discord.Embed(title='', description=f'<@{ctx.author.id}> pouts', color=0x202225)
        embed.set_image(url=requests.get(f'{roleplay_api}pout').json()['url'])
        embed.set_footer(text=f'{self.bot.user.name} • ©{reportManagerName}', icon_url=f'{self.bot.user.avatar.url}')
        await ctx.respond(embed=embed)

    @roleplay.command(name='sleep', description='sleep')
    async def _rp_sleep(self, ctx):
        embed = discord.Embed(title='', description=f'<@{ctx.author.id}> goes to sleep', color=0x202225)
        embed.set_image(url=requests.get(f'{roleplay_api}sleep').json()['url'])
        embed.set_footer(text=f'{self.bot.user.name} • ©{reportManagerName}', icon_url=f'{self.bot.user.avatar.url}')
        await ctx.respond(embed=embed)

    @roleplay.command(name='smug', description='smug')
    async def _rp_smug(self, ctx):
        embed = discord.Embed(title='', description=f'<@{ctx.author.id}> looks smug', color=0x202225)
        embed.set_image(url=requests.get(f'{roleplay_api}smug').json()['url'])
        embed.set_footer(text=f'{self.bot.user.name} • ©{reportManagerName}', icon_url=f'{self.bot.user.avatar.url}')
        await ctx.respond(embed=embed)

    @commands.slash_command(
        name='rockpaperscissors',
        description='play rock paper scisors against egirl'
    )
    async def _rockpaperscissors(self, ctx, choice: Option(str, 'choose gif', choices = [
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

    @commands.slash_command(
        name="dog",
        description="random dog image",
    )
    async def _dog(self, ctx, breed: Option(str, 'specify breed', choices = [
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
        embed.set_footer(text=f'{self.bot.user.name} • ©{reportManagerName}', icon_url=f'{self.bot.user.avatar.url}')
        await ctx.respond(embed=embed)

    @commands.slash_command(
        name='hypixel',
        description='get general hypixel stats for a player'
    )
    async def _hypixel(self, ctx, player: Option(str, 'username or uuid of player', required=True)):
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

    @commands.slash_command(
        name="cat",
        description="random cat image",
    )
    async def _cat(self, ctx):
        embed = discord.Embed(title=f'meow!', description='', color=0x202225)
        embed.set_image(url=requests.get(f'https://api.thecatapi.com/v1/images/search').json()[0]['url'])
        embed.set_footer(text=f'{self.bot.user.name} • ©{reportManagerName}', icon_url=f'{self.bot.user.avatar.url}')
        await ctx.respond(embed=embed)

    @commands.slash_command(
        name="howboopable",
        description="check someone's boopability",
    )
    async def _howboopable(self, ctx, user: Option(discord.Member, "choose who to check boopability for", required=False)):
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
        embed.set_footer(text=f'{self.bot.user.name} • ©{reportManagerName}', icon_url=f'{self.bot.user.avatar.url}')
        await ctx.respond(embed=embed)

    @commands.slash_command(name="tod", description="truth or dare")
    async def _tod(self, ctx, type: Option(str, 'choose between truth or dare', choices=[
        OptionChoice(name='Truth', value='truth'), 
        OptionChoice(name='Dare', value='dare'),
        OptionChoice(name='Surprise Me!', value='surprise_me')], required=True),
        rating: Option(str, 'choose rating of question', choices=[
        OptionChoice(name='PG', value='pg'), 
        OptionChoice(name='PG-13', value='pg13'),
        OptionChoice(name='R', value='r')], required=False, default='pg13')):
        async def tod(ctx, type: str, rating):
            truth_button_V = Button(label='Truth', style=discord.ButtonStyle.green)
            dare_button_V = Button(label='Dare', style=discord.ButtonStyle.red)
            random_button_V = Button(label='Surprise Me!', style=discord.ButtonStyle.blurple)

            async def truth_button(interaction):
                try:
                    await interaction.response.edit_message(embed=embed, view=None)
                    await tod(ctx, 'truth', rating)
                except discord.errors.NotFound: return
            async def dare_button(interaction):
                try:
                    await interaction.response.edit_message(embed=embed, view=None)
                    await tod(ctx, 'dare', rating)
                except discord.errors.NotFound: return
            async def random_button(interaction): 
                try:
                    await interaction.response.edit_message(embed=embed, view=None)
                    await tod(ctx, 'surprise_me', rating)
                except discord.errors.NotFound: return

            async def on_timeout():
                try:
                    view.disable_all_items()
                    truth_button.label = 'Timed Out'
                    dare_button.label = 'Timed Out'
                    random_button.label = 'Timed Out'
                    await ctx.edit(view=view)
                except: return
            
            view = View(timeout=180, disable_on_timeout=True)
            view.add_item(truth_button_V)
            view.add_item(dare_button_V)
            view.add_item(random_button_V)
            truth_button_V.callback = truth_button
            dare_button_V.callback = dare_button
            random_button_V.callback = random_button
            view.on_timeout = on_timeout

            if type == 'surprise_me': type = random.choice(['truth', 'dare'])

            todr = requests.get(f'https://api.truthordarebot.xyz/v1/{type}?rating={rating}').json()['question']

            embed = discord.Embed(title=f'Truth or Dare', description=todr, color=0x202225)
            embed.set_footer(text=f'{self.bot.user.name} • ©{reportManagerName} • Rating: {rating} • Type: {string.capwords(type)}', icon_url=f'{self.bot.user.avatar.url}')
            await ctx.respond(embed=embed, view=view)
        await tod(ctx, type, rating)

    @commands.slash_command(name="wyr", description='would you rather')
    async def _wyr(self, ctx, rating: Option(str, 'choose rating of question', choices=[
        OptionChoice(name='PG', value='pg'), 
        OptionChoice(name='PG-13', value='pg13'),
        OptionChoice(name='R', value='r')], required=False, default='pg13')):
        async def wyr(ctx, rating):
            next_button = Button(label='Next', style=discord.ButtonStyle.green)

            async def next_button_f(interaction):
                try:
                    await interaction.response.edit_message(embed=embed, view=None)
                    await wyr(ctx, rating)
                except discord.errors.NotFound: return

            async def on_timeout():
                try:
                    view.disable_all_items()
                    next_button.label = 'Timed Out'
                    await ctx.edit(view=view)
                except: return
            
            view = View(timeout=180, disable_on_timeout=True)
            view.add_item(next_button)
            next_button.callback = next_button_f
            wyrr = requests.get(f'https://api.truthordarebot.xyz/api/wyr?rating={rating}').json()['question'][17:].capitalize()

            embed = discord.Embed(title=f'Would you Rather', description=wyrr, color=0x202225)
            embed.set_footer(text=f'{self.bot.user.name} • ©{reportManagerName} • Rating: {rating}', icon_url=f'{self.bot.user.avatar.url}')
            await ctx.respond(embed=embed, view=view)
        await wyr(ctx, rating)

    @commands.slash_command(name="nhie", description='never have I ever')
    async def _nhie(self, ctx, rating: Option(str, 'choose rating of question', choices=[
        OptionChoice(name='PG', value='pg'), 
        OptionChoice(name='PG-13', value='pg13'),
        OptionChoice(name='R', value='r')], required=False, default='pg13')):
        async def nhie(ctx, rating):
            next_button = Button(label='Next', style=discord.ButtonStyle.green)

            async def next_button_f(interaction):
                try:
                    await interaction.response.edit_message(embed=embed, view=None)
                    await nhie(ctx, rating)
                except discord.errors.NotFound: return

            async def on_timeout():
                try:
                    view.disable_all_items()
                    next_button.label = 'Timed Out'
                    await ctx.edit(view=view)
                except: return
            
            view = View(timeout=180, disable_on_timeout=True)
            view.add_item(next_button)
            next_button.callback = next_button_f
            nhier = requests.get(f'https://api.truthordarebot.xyz/api/nhie?rating={rating}').json()['question']

            embed = discord.Embed(title=f'Never Have I Ever', description=nhier, color=0x202225)
            embed.set_footer(text=f'{self.bot.user.name} • ©{reportManagerName} • Rating: {rating}', icon_url=f'{self.bot.user.avatar.url}')
            await ctx.respond(embed=embed, view=view)
        await nhie(ctx, rating)

    @commands.slash_command(name='uwuifier', description='uwuify some text')
    async def _uwuifier(self, ctx, text: Option(str, 'text to uwuify', required=True), send_as_user: Option(bool, 'send message as clone of user', required=False, default=True)):
        text1 = text.replace('l','w')
        text1 = text1.replace('L','W')
        text1 = text1.replace('r','w')
        text1 = text1.replace('R','W')
        text1 = text1.replace('th','d')
        text1 = text1.replace('Th','D')
        text1 = text1.replace('tH','D')
        text1Sp = text1.split()
        rText = ''
        for w in text1Sp:
            r = random.randrange(0, 15)
            if r == 0:
                f = w[0] + '- '+ w + ' '
                rText += f
            else: rText += w + ' '

        embed = discord.Embed(title='egirl\'s uwuifier', description=discord.Embed.Empty, color=0x202225)
        #embed.set_thumbnail(url=self.bot.user.avatar.url)
        embed.add_field(name=f'Old Text', value=f'{text}', inline=False)
        embed.add_field(name=f'UwUified Text', value=f'{rText}', inline=False)
        try:
            if send_as_user == True:
                await ctx.respond(embed=embed, ephemeral=True)
                webhook = await ctx.channel.create_webhook(name=ctx.author.name)
                await webhook.send(f'{rText}', username=ctx.author.nick, avatar_url=ctx.author.avatar.url)
                await webhook.delete()
            if send_as_user == False:
                await ctx.respond(embed=embed, ephemeral=True)
        except Exception as e: await ctx.respond(f'UwUification failed! error: {e}', ephemeral=True)

    @commands.slash_command(name='nuke', description='hide or completely delete a channel')
    async def _nuke(self, ctx, 
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

    @commands.slash_command(name='kick', description='kick a member')
    async def _kick(self, ctx, member: Option(discord.Member, 'choose member to kick', required=True), reason: Option(str, 'reason displayed in audit log', required=True)):
        if ctx.author.guild_permissions.kick_members:
            try:
                await member.kick(reason=reason)
                await ctx.respond(f'**{member}** was kicked! ✅', ephemeral=True)
            except:
                await ctx.respond(f'Failed to kick **{member}**, is their role higher than egirl\'s? Are they in the server? ❌', ephemeral=True)
        else:
            await ctx.respond('You must be an administrator to kick members! ❌', ephemeral=True)

    @commands.slash_command(name='ban', description='ban a member')
    async def _ban(self, ctx, member: Option(discord.Member, 'choose member to ban', required=True), reason: Option(str, 'reason displayed in audit log', required=True)):
        if ctx.author.guild_permissions.ban_members:
            try:
                await member.ban(reason=reason, delete_message_seconds=None, delete_message_days=None)
                await ctx.respond(f'**{member}** was banned! ✅', ephemeral=True)
            except:
                await ctx.respond(f'Failed to ban **{member}**, is their role higher than egirl\'s? Are they in the server? ❌', ephemeral=True)
        else:
            await ctx.respond('You must be an administrator to ban members! ❌', ephemeral=True)

    @commands.slash_command(name='qotd', description='random qotd')
    async def _qotd(self, ctx, role: Option(discord.Role, 'choose qotd role', required=False, default=None), 
    channel: Option(discord.TextChannel, 'choose text channel to send qotd', required=False, default=None), 
    question: Option(str, 'optional custom question', required=False, default=None)):
        if ctx.author.guild_permissions.mention_everyone:
            await ctx.response.send_message('thinking... 🕐', ephemeral=True)
            if question == None:
                res = requests.get('https://chillihero.api.stdlib.com/qotd@0.1.3/question/').json()
            else:
                if question[len(question)-1:] == '?':
                    pass
                else:
                    question += '?'
                res = question
            if role == None:
                mention = ''
            else:
                mention = role.mention
            embed = discord.Embed(title=f'egirl\'s Question of The Day', description=res, color=0x202225)
            if channel == None:
                await ctx.channel.send(mention, embed=embed)
                await ctx.edit(content='done! ✅')
            else:
                await channel.send(mention, embed=embed)
                await ctx.edit(content='done! ✅')
        else:
            await ctx.respond('This command requires the \'Mention Everyone\' permission! ❌', ephemeral=True)

    @commands.slash_command(name='poll', description='poll users')
    async def _poll(self, ctx, question: Option(str, 'poll question', required=True)):
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

    @commands.slash_command(name='reportissue', description='report an issue with egirl')
    async def _reportissue(self, ctx, title: Option(str, 'report title', required=True), report: Option(str, 'describe issue', required=True)):
        global reportLock
        if ctx.author.id in reportLock:
            await ctx.respond(f'You have reported an issue too recently, try again in a few minutes! ❌', ephemeral = True)
        else:
            if len(title) > 248:
                await ctx.respond(f'Report failed! Your title is {len(title)-248} characters too long! ❌', ephemeral = True)
            elif len(report) > 1024:
                await ctx.respond(f'Report failed! Your description is {len(report)-1024} characters too long! ❌', ephemeral = True)
            else: 
                manager = self.bot.get_user(reportManager)
                embed = discord.Embed(title=f'Report: {title}', description=report, color=0x202225)
                embed.set_author(name=f'Report filed by {ctx.author}', icon_url=f'{ctx.author.avatar.url}')
                await manager.send(embed=embed)
                await ctx.respond('Report sent! Thanks for helping improve egirl! ✅', ephemeral = True)
                await self.bot.get_channel(loggingChannel).send(f'<@{reportManager}>! report filed!')
                reportLock.append(ctx.author.id)

    @commands.slash_command(name='debug', description='debug cmd, for bot owner only')
    async def _debug(self, ctx, cmd: Option(str, 'cmd', required=True), user: Option(discord.Member, 'cmd', required=False, default=None)):
        appinfo = await self.bot.application_info()
        bot_owner = appinfo.owner
        cmd = cmd.lower()
        def debug_help():
            extS = ''
            for i in list(self.bot.extensions):
                extS += i+'\n'
            if extS == '':
                extS = 'No extensions loaded!'
            helpcmds = {
                'reloadallexts': 'reload all extensions',
                'cog.<cog name>': 'reload extension with specified name',
                'pages': 'list all servers egirl is in',
                'gcount': 'get number of servers egirl is in',
                'keegan': 'i love you keegan',
                'listcommands': 'list all loaded commands',
                'banner': 'get banner of user',
                'wipecgtdb': 'wipe DBs for catgirl test',
                'say <text>': 'make egirl speak in plain text',
                'shutupeli': 'prevent eli from speaking (doesnt work)',
            }
            helptext = ''
            for i in helpcmds:
                helptext += f'• **{i}** - {helpcmds[i]}\n'
            embed = discord.Embed(title=f'welcome to {self.bot.user.name} debug mode, {bot_owner.name}!', description=f'command invoked: {cmd}\nuser invoked: {str(user)}', color=0x202225)
            embed.add_field(name='currently loaded extensions', value=extS, inline=False)
            embed.add_field(name='commands', value=helptext, inline=False)
            embed.set_footer(text = f'{self.bot.user.name}', icon_url=self.bot.user.display_avatar.url)
            return embed
        if ctx.author.id == bot_owner.id:
            if cmd.lower() == 'help':
                await ctx.respond(embed=debug_help())
            elif cmd == 'solorp':
                embed = discord.Embed(title=f'', description=':(', color=0x202225)
                await ctx.respond(embed=embed)
            elif cmd.lower() == 'reloadallexts':
                extS = ''
                failed = ''
                for ex in egirl_cogs:
                    try: 
                        self.bot.reload_extension(ex)
                        extS += ex+'\n'
                    except Exception as e: 
                        print(f'failed to reload cog {ex}\nerror: {e}')
                        failed =+ ex+'\n'
                if extS == '':
                    extS = 'no extensions reloaded!'
                if failed == '':
                    failed = 'no extensions failed!'
                embed = discord.Embed(title=f'', description=discord.Embed.Empty, color=0x202225)
                embed.add_field(name='successfully reloaded', value=f'{extS}', inline=False)
                embed.add_field(name='failed to reload', value=f'{failed}', inline=False)
                embed.set_footer(text = f'{self.bot.user.name}', icon_url=self.bot.user.display_avatar.url)
                #await self.bot.sync_commands()
                await ctx.respond(embed=embed)
            elif cmd.lower().startswith('cog.'):
                try: 
                    self.bot.reload_extension(cmd)
                    embed = discord.Embed(title=f'', description=f'successfully reloaded {cmd}', color=0x202225)
                    embed.set_footer(text = f'{self.bot.user.name}', icon_url=self.bot.user.display_avatar.url)
                    await ctx.respond(embed=embed)
                    print(f'successfully reloaded {cmd}')
                    #await self.bot.sync_commands()
                except Exception as e: 
                    print(f'failed to reload {cmd}\nerror: {e}')
                    embed = discord.Embed(title=f'', description=f'failed to reload {cmd}\nerror: {e}', color=0x202225)
                    embed.set_footer(text = f'{self.bot.user.name}', icon_url=self.bot.user.display_avatar.url)
                    await ctx.respond(embed=embed)
            elif cmd == 'banner':
                if user == None:
                    bannerEmbed = discord.Embed(title=f'', description=f'specify user pls', color=0x202225)
                    await ctx.respond(embed=bannerEmbed)
                    return
                user = ctx.author            
                bUser = await self.bot.fetch_user(user.id)
                try:
                    bannerURL = bUser.banner.url
                    bannerEmbed = discord.Embed(title=f'', description=f'{user}\'s banner', color=0x202225)
                    bannerEmbed.set_image(url=bannerURL)
                except AttributeError:
                    accentC = bUser.accent_color
                    if accentC == None:
                        bannerEmbed = discord.Embed(title=f'', description=f'no banner was found for {user}. perhaps they dont have nitro or a custom color?', color=0x202225)
                    else:
                        bannerURL = f'https://singlecolorimage.com/get/' + str(accentC).replace('#', '') + '/600x240'
                        bannerEmbed = discord.Embed(title=f'', description=f'{user}\'s banner', color=accentC)
                        bannerEmbed.set_image(url=bannerURL)
                bannerEmbed.set_footer(text=f'requested by {ctx.author}', icon_url=f'{ctx.author.avatar.url}'),
                await ctx.respond(embed=bannerEmbed)
            elif cmd == 'topmember':
                high = 0
                for guild in self.bot.guilds:
                    if guild.member_count > high:
                        if guild.name == 'Discord Bots':
                            pass
                        else:
                            high = guild.member_count
                            highName = guild.name
                    else:
                        pass
                await ctx.respond('guild with most members is '+highName+' with '+str(high)+' members', ephemeral=True)
            elif cmd == 'gcount':
                await ctx.respond(f'```Total Servers: {len(self.bot.guilds)}```')
            elif cmd == 'keegan':
                await ctx.respond('keegan? as in poppy\'s extremely romanoledgeable wife?')
            elif cmd == 'listcommands':
                cmds = '```'
                cmd_count = 0
                for cmd in self.bot.walk_application_commands():
                    cmds += cmd.qualified_name+'\n'
                    cmd_count += 1
                cmds += '```'
                embed = discord.Embed(title=f'currently loaded commands ({cmd_count} in total)', description=cmds, color=0x202225)
                embed.set_footer(text = f'{self.bot.user.name}', icon_url=self.bot.user.display_avatar.url)
                await ctx.respond(embed=embed)

            elif cmd == 'pages':
                await ctx.defer()

                pages_to_send = [[discord.Embed(title="joined guilds - page 0", description='hi poppy!')]]
                
                guild_ls = self.bot.guilds
                active_page = 'name - member count\n```'
                page_num = 1
                over_4k = False
                while guild_ls != []:
                    if len(active_page) < 4000:
                        active_page += guild_ls[0].name + ' - ' + str(guild_ls[0].member_count) + '\n'
                        del guild_ls[0]
                    else:
                        over_4k = True
                        pages_to_send.append([discord.Embed(title=f'joined guilds - page {page_num}', description=active_page+'```')])
                        page_num += 1
                        active_page = 'name - member count\n```'

                if over_4k == False:
                    pages_to_send.append([discord.Embed(title=f'joined guilds - page {page_num}', description=active_page+'```')])

                paginator = pages.Paginator(pages=pages_to_send, disable_on_timeout=True, timeout=180)
                await paginator.respond(ctx.interaction, ephemeral=False)

            elif cmd == 'wipecgtdb':
                db = sqlite3.connect("database.sqlite")
                cursor = db.cursor()
                cursor.execute(f'DELETE FROM data WHERE server_id = 951027740256137226')
                db.commit()
                embed = discord.Embed(title='', description=f'wiped db enteries for `catgirl test`', color=0x202225)
                embed.set_footer(text = f'{self.bot.user.name}', icon_url=self.bot.user.display_avatar.url)
                await ctx.respond(embed=embed)

            elif cmd.startswith('say '):
                embed = discord.Embed(title='', description=f'thinking... 🕑', color=0x202225)
                embed.set_footer(text = f'{self.bot.user.name}', icon_url=self.bot.user.display_avatar.url)
                await ctx.response.send_message(embed=embed, ephemeral=True)
                text = cmd.split(' ', 1)[1]
                await ctx.channel.send(text)
                embed.description='sent! ✅'
                await ctx.edit(embed=embed)
            elif cmd == 'shutupeli':
                await ctx.defer()
                if self.eliban == True:
                    self.eliban = False
                    embed = discord.Embed(title='', description=f'eli speech privilege set to `{self.eliban}`', color=0x202225)
                    embed.set_footer(text = f'{self.bot.user.name}', icon_url=self.bot.user.display_avatar.url)
                    await ctx.respond(embed=embed, ephemeral=True)
                elif self.eliban == False:
                    self.eliban = True
                    embed = discord.Embed(title='', description=f'eli speech privilege set to `{self.eliban}`', color=0x202225)
                    embed.set_footer(text = f'{self.bot.user.name}', icon_url=self.bot.user.display_avatar.url)
                    await ctx.respond(embed=embed, ephemeral=True)

            else: cmd = f'help (inferred from {cmd})'; await ctx.respond(embed=debug_help())
        else:
            embed = discord.Embed(title='', description='debug not accessible to you!', color=0x202225)
            embed.add_field(name=discord.Embed.Empty, value='[support server](https://discord.gg/xzAuXPz)\n[poppy\'s github](https://github.com/ignpoppyseed)', inline=False)
            embed.set_footer(text = f'{self.bot.user.name}', icon_url=self.bot.user.display_avatar.url)
            await ctx.respond(embed=embed)
            return

    @commands.slash_command(name='choose', description='choose between multiple options, seperated by commands')
    async def _choose(self, ctx, choices: Option(str, 'seperate choices with commas', required=True)):
        choices = choices.split(',')
        embed = discord.Embed(title=f'egirl\'s Choice', description='I choose: '+choices[random.randrange(0, len(choices))], color=0x202225)
        embed.set_footer(text=f'{self.bot.user.name} • ©{reportManagerName}', icon_url=f'{self.bot.user.avatar.url}')
        await ctx.respond(embed=embed)

    @commands.slash_command(name='animatedstorytitle', description='AI generated animated story title')
    async def _animatedstorytitle(self, ctx):
        res = requests.get('https://animatedstorytitles.com/api/title').json()['title']
        embed = discord.Embed(title=f'egirl\'s Animated Story Title', description=res, color=0x202225)
        embed.set_footer(text=f'{self.bot.user.name} • ©{reportManagerName}', icon_url=f'{self.bot.user.avatar.url}')
        await ctx.respond(embed=embed)

    imagegen = discord.SlashCommandGroup("imagegen", "image gen commands")

    @imagegen.command(name='clyde', description='make discord\'s clyde say something!')
    async def _clyde(self, ctx, text: Option(str, 'text to make clyde say', reqired=True)):
        res = requests.get(f'https://nekobot.xyz/api/imagegen?type=clyde&text={text}').json()['message']
        embed = discord.Embed(title=f'', description=f'**message from clyde!**', color=0x202225)
        embed.set_image(url=res)
        embed.set_footer(text=f'{self.bot.user.name} • ©{reportManagerName}', icon_url=f'{self.bot.user.avatar.url}')
        await ctx.respond(embed=embed)

    @imagegen.command(name='tweet', description='make a fake tweet')
    async def _tweet(self, ctx, text: Option(str, 'text to make tweet author say', reqired=True), username: Option(str, 'username of tweet author', reqired=False, default=None)):
        if username == None:
            username = ctx.author.name
        res = requests.get(f'https://nekobot.xyz/api/imagegen?type=tweet&text={text}&username={username}').json()['message']
        embed = discord.Embed(title=f'', description=f'**new tweet from {username}!**', color=0x202225)
        embed.set_image(url=res)
        embed.set_footer(text=f'{self.bot.user.name} • ©{reportManagerName}', icon_url=f'{self.bot.user.avatar.url}')
        await ctx.respond(embed=embed)

    @commands.slash_command(name='jortsweather', description='decide if it\'s jorts or jeans weather')
    async def _jortsweather(self, ctx, city: Option(str, 'city to find weather for', reqired=True), hidden: Option(bool, 'choose if response is hidden (just in case you dont want people to see your city', required=False, default=False)):
        apiresponse = requests.get('http://api.openweathermap.org/data/2.5/weather?appid=' + weatherToken + '&q=' + city + '&units=imperial').json()
        if apiresponse["cod"] != "404":
            try:
                current_temperature = apiresponse["main"]["temp"]
                if current_temperature >= 72:
                    dec = 'jorts'
                elif current_temperature < 72:
                    dec = 'jeans'
                embed = discord.Embed(title=f'egirl\'s Jorts Decider', description=f'In {apiresponse["name"]}, the current temperature is: {current_temperature}°F\nThat means it\'s **{dec}** weather!', color=0x202225)
                embed.set_footer(text=f'{self.bot.user.name} • ©{reportManagerName}', icon_url=f'{self.bot.user.avatar.url}')
                await ctx.respond(embed=embed)
            except KeyError:
                await ctx.respond('City not found! ❌', ephemeral=True)
        else:
            await ctx.respond('something went wrong! use </reportissue:0> ❌', ephemeral=True)

    @commands.slash_command(name='passwordgenerator', description='generate a pseudo-random password')
    async def _passwordgenerator(self, ctx, length: Option(int, 'length of password', reqired=True)):
        if length > 100:
            await ctx.respond('Password cannot be over 100 characters! ❌', ephemeral=True)
            return
        ascii_letters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
        special_characters = '*_@-!.'
        i = 0
        r = ''
        while i < length:
            c = random.randint(0,2)
            if c == 0:
                r += random.choice(ascii_letters)
            elif c == 1:
                r += str(random.randint(0, 9))
            elif c == 2:
                r += random.choice(special_characters)
            i += 1

        embed = discord.Embed(title=f'egirl\'s Password Generator', description=f'Generated password: `{r}`', color=0x202225)
        embed.set_author(name='egirl will never store your password')
        embed.set_footer(text=f'{self.bot.user.name} • ©{reportManagerName}', icon_url=f'{self.bot.user.avatar.url}')
        await ctx.respond('`'+r+'`', embed=embed, ephemeral=True)

    @commands.slash_command(name='profile', description='get the profile of a user')
    async def _profile(self, ctx, user: Option(discord.Member, 'user to get profile for', required=False)):
        await ctx.defer()
        if user == None:
            user = ctx.author
        user = await self.bot.fetch_user(user.id)
        flags = ['partner', 'staff', 'discord_certified_moderator', 'hypesquad', 'hypesquad_balance', 
        'hypesquad_bravery', 'hypesquad_brilliance', 'bug_hunter', 'bug_hunter_level_2',
        #this is where active dev would go
        'early_verified_bot_developer', 'early_supporter', 'verified_bot']
        flagDict = {
        'partner': '<:discord_partner:1042614097650389043>',
        'staff': '<:Discord_Staff:1042614098711560202>',
        'discord_certified_moderator': '<:Discord_certified_moderator:1042614096564068392>',
        'hypesquad': '<:HypeSquad_Event:1042614104260628540>',
        'hypesquad_balance': '<:HypeSquad_Balance:1042614100766752878>',
        'hypesquad_bravery': '<:HypeSquad_Bravery:1042614101857275964>',
        'hypesquad_brilliance': '<:HypeSquad_Brilliance:1042614103161704468>',
        'bug_hunter': '<:Bug_Hunter:1042614093812596837>',
        'bug_hunter_level_2': '<:Bug_Hunter_level2:1042614094940880997>',
        'early_verified_bot_developer': '<:Verified_Bot_Developer:1042614106491998208>',
        'early_supporter': '<:early_supporter:1042614099449757728>',
        'nitro': '<:nitro:1042614105401471087>',
        'verified_bot': '<:verified_bot_p1:1042615562636886076><:verified_bot_p2:1042615563693850665>'
        }
        userFlags = []
        badges = ''
        for flag in flags:
            if getattr(user.public_flags, flag):
                userFlags.append(flag)
                badges += flagDict[flag]+' '
        if user.id == reportManager:
            t = f'{user}\'s profile <:Server_Owner:1042685056277299220> <:Verified_Bot_Developer:1042614106491998208> <:Active_Developer:1042686286001090621>'
        else:
            t = f'{user}\'s profile'

        embed = discord.Embed(title=t, description='', color=0x202225)
        if badges != '':
            embed.add_field(name='Badges', value=badges, inline=False)
        try:
            act_user = ctx.guild.get_member(user.id)
            for activity in act_user.activities:
                type = str(activity.type).split('.')[1].capitalize()
                if type.lower() == 'custom': embed.add_field(name='Custom Status', value=f'{activity}', inline=False)
                elif type.lower() == 'listening': embed.add_field(name='Listening to', value=f'[{str(activity.title)}]({str(activity.track_url)}) - {str(activity.artist)}', inline=False)
                elif type.lower() == 'playing': embed.add_field(name='Playing', value=f'{activity.name}', inline=False)
                elif type.lower() == 'streaming': embed.add_field(name='Streaming', value=f'[{activity.name}]({activity.url})', inline=False)
                elif type.lower() == 'watching': embed.add_field(name='Watching', value=f'[{activity.name}]({activity.url})', inline=False)
                else: embed.add_field(name='Unknown Status Type', value=activity.name, inline=False)
        except Exception as e: embed.add_field(name='Custom Status', value=f'No activity available!', inline=False)

        embed.add_field(name='User ID', value=f'{user.id}', inline=False)
        embed.add_field(name='Joined Discord', value=f'<t:{int(user.created_at.timestamp())}:R>', inline=False)
        try:
            embed.set_image(url=user.banner.url)
            bannerState = 0
        except AttributeError:
            if user.accent_color == None:
                bannerState = 1
            else:
                embed.set_image(url=f'https://singlecolorimage.com/get/' + str(user.accent_color).replace('#', '') + '/600x240')
                bannerState = 2
        if bannerState == 0:
            if '.gif' in user.banner.url:
                v = 'GIF Banner'
            elif '.png' in user.banner.url or '.jpg' in user.banner.url or '.webp' in user.banner.url:
                v = 'Standard banner'
            embed.add_field(name='Banner', value=v)
        elif bannerState == 1:
            embed.add_field(name='Banner', value='No banner found!')
        elif bannerState == 2:
            embed.add_field(name='Banner', value='Accent color')
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.set_footer(text=f'{self.bot.user.name} • ©{reportManagerName}', icon_url=f'{self.bot.user.avatar.url}')
        await ctx.respond(embed=embed)

    nick = discord.SlashCommandGroup("nick", "nickname related commands")

    @nick.command(name='set', description='change the nickname of a user (or yourself)')
    async def _set(self, ctx, nickname: Option(str, 'new nickname', required=True), user: Option(discord.Member, 'user to change nickname of', required=False)):
        try:
            if user == None: user = ctx.author
            if user == ctx.author:
                if len(nickname) > 32:
                    await ctx.respond('Nickname must be 32 characters at most! ❌', ephemeral=True)
                    return
                oldNick = user.nick
                await user.edit(nick=nickname)
                newNick = user.nick
                embed = discord.Embed(title=f'{user}\'s Nickname Updated!', description=f'Old nickname: {oldNick}\nNew nickname: {newNick}', color=0x202225)
                embed.set_footer(text=f'{self.bot.user.name} • ©{reportManagerName}', icon_url=f'{self.bot.user.avatar.url}')
                await ctx.respond(embed=embed)
            else:
                if ctx.author.guild_permissions.manage_nicknames:
                    if len(nickname) > 32:
                        await ctx.respond('Nickname must be 32 characters at most! ❌', ephemeral=True)
                        return
                    oldNick = user.nick
                    await user.edit(nick=nickname)
                    newNick = user.nick
                    embed = discord.Embed(title=f'{user}\'s Nickname Updated!', description=f'Old nickname: {oldNick}\nNew nickname: {newNick}', color=0x202225)
                    embed.set_footer(text=f'{self.bot.user.name} • ©{reportManagerName}', icon_url=f'{self.bot.user.avatar.url}')
                    await ctx.respond(embed=embed)
                else: await ctx.respond('This command requires the \'Manage Nicknames\' permission! ❌', ephemeral=True)
        except Exception as e:
            print(f"perms error when changing nick\nError: {e}")
            await ctx.respond('Permissions error when changing nick! Is egirl is higher role than the user? ❌', ephemeral=True)

    @nick.command(name='reset', description='reset the nickname of a user (or yourself)')
    async def _reset(self, ctx, user: Option(discord.Member, 'user to reset nickname of', required=False)):
        try:
            if user == None: user = ctx.author
            if user == ctx.author:
                oldNick = user.nick
                await user.edit(nick=None)
                embed = discord.Embed(title=f'{user}\'s Nickname Reset!', description=f'Old nickname: {oldNick}\nNew name: {user.name}', color=0x202225)
                embed.set_footer(text=f'{self.bot.user.name} • ©{reportManagerName}', icon_url=f'{self.bot.user.avatar.url}')
                await ctx.respond(embed=embed)
            else:
                if ctx.author.guild_permissions.manage_nicknames:
                    oldNick = user.nick
                    await user.edit(nick=None)
                    embed = discord.Embed(title=f'{user}\'s Nickname Reset!', description=f'Old nickname: {oldNick}\nNew name: {user.name}', color=0x202225)
                    embed.set_footer(text=f'{self.bot.user.name} • ©{reportManagerName}', icon_url=f'{self.bot.user.avatar.url}')
                    await ctx.respond(embed=embed)
                else: await ctx.respond('This command requires the \'Manage Nicknames\' permission! ❌', ephemeral=True)
        except Exception as e:
            print(f"perms error when resetting nick\nError: {e}")
            await ctx.respond('Permissions error when resetting nick! Is egirl is higher role than the user? ❌', ephemeral=True)

    @commands.slash_command(name='flip', description='flip a coin, with optional suspense!')
    async def _flip(self, ctx, suspense: Option(bool, 'toggle suspense', required=False, default=False)):
        res = random.choice(['**heads**', '**tails**'])
        if suspense:
            embed = discord.Embed(title=f'egirl\'s Coin Flip', description='Flipping a coin... <a:coin:1043963826325958737>', color=0x202225)
            await ctx.response.send_message(embed=embed)
            embed = discord.Embed(title=f'egirl\'s Coin Flip', description='Hang on... <a:coin:1043963826325958737>', color=0x202225)
            await asyncio.sleep(2)
            await ctx.edit(embed=embed)
            embed = discord.Embed(title=f'egirl\'s Coin Flip', description='It\'s.. It\'s... <a:coin:1043963826325958737>', color=0x202225)
            await asyncio.sleep(2)
            await ctx.edit(embed=embed)
            embed = discord.Embed(title=f'egirl\'s Coin Flip', description=f'It\'s {res.upper()}!! <a:coin:1043963826325958737>', color=0x202225)
            await asyncio.sleep(2)
            await ctx.edit(embed=embed)
        elif suspense == False:
            embed = discord.Embed(title=f'egirl\'s Coin Flip', description=f'It\'s {res.upper()}!! <a:coin:1043963826325958737>', color=0x202225)
            await ctx.response.send_message(embed=embed)

    @commands.slash_command(name='formatting', description='help with discord\'s formatting syntax')
    async def _formatting(self, ctx):
        embed = discord.Embed(title=f'egirl\'s Formatting (Markdown) Syntax Help', description=f'Formatting is placed on either side of the desired text, like *this*. \
        Some formatting (notably italics and bolding) can be combined to make new formatting, like ***this***, which results in bold and italic text (this). \
        Formatting doesn\'t apply in codeblocks or when escaped with a backslash (*See, I\'m not formatted!*, \*Me either!\*).', color=0x202225)
        embed.add_field(name='Syntax', value='Double Underscore: \_\_underline\_\_  __text__\n\
        Single Asterisk: \*italics\* *text*\n\
        Double Asterisk: \**bold\** **text**\n\
        Double Tilde: \~~strikethrough\~~ ~~text~~\n\
        Single Backtick: \`single line codeblock\` `text`\n\
        Greater Than: > Quote\n\
        > text\n\
        Triple Backtick: \`\`\`multi line codeblock\`\`\` \n\
        ```text```', inline=False)
        #embed.set_thumbnail(url='https://raw.githubusercontent.com/ignpoppyseed/ignpoppyseed/main/img/mdW2.png')
        #embed.set_thumbnail(url='https://raw.githubusercontent.com/ignpoppyseed/ignpoppyseed/main/img/mdB2.png')
        embed.add_field(name='Helpful Resources', value='[Official Discord Formatting Guide](https://support.discord.com/hc/en-us/articles/210298617-Markdown-Text-101-Chat-Formatting-Bold-Italic-Underline-)\n\
            [matthewzring\'s Guide With Nice Examples!](https://gist.github.com/matthewzring/9f7bbfd102003963f9be7dbcf7d40e51)', inline=False)
        await ctx.respond(embed=embed)

    roll = discord.SlashCommandGroup("roll", "dice rolling commands")
    
    @roll.command(name='expression', description='roll a dice!')
    async def _roll_expression(self, ctx, expression: Option(str, 'the expression to roll', required=True), hidden: Option(bool, 'have the result hidden from other users', required=False, default=False)):
        if hidden == True:
            eph = True
        else:
            eph = False
        await ctx.defer(ephemeral=eph)
        try:
            roll = dice.roll(expression)
        except dice.exceptions.DiceException:
            embed = discord.Embed(title=f'egirl\'s Dice Roller', description=f'Parsing Error! Your expression **{expression}** was unable to be parsed! Try the </roll help:0> command for help!', color=0x202225)
            await ctx.respond(embed=embed, ephemeral=eph)
            return
        res = ''
        if type(roll) == dice.elements.Roll:
            i = 1
            for f in roll:
                res += '**Die '+str(i)+'**: '+str(f)+'\n'
                i += 1
        elif type(roll) == dice.elements.Integer: res += '**Die 1**: '+str(roll)
        embed = discord.Embed(title=f'egirl\'s Dice Roller', description=res, color=0x202225)
        try:
            await ctx.respond(embed=embed, ephemeral=eph)
        except:
            embed = discord.Embed(title=f'egirl\'s Dice Roller', description=f'Parsing Error! Your expression **{expression}** resulted in a response that was too long! Try the </roll help:0> command for help!', color=0x202225)
            await ctx.respond(embed=embed, ephemeral=eph)

    @roll.command(name='help', description='dice rolling help')
    async def _roll_help(self, ctx):
        embed = discord.Embed(title=f'egirl\'s Dice Roller Help', description=f'The documentation for the expression parser is [here](https://pypi.org/project/dice/), in the notation section. However, you may find a summary of the basics below.', color=0x202225)
        embed.add_field(name='Examples', value=f'**4d6**: Rolls 4 die with 6 sides.\n\n\
            **4d6t**: Rolls 4 die with 6 sides and returns the total(t) of those rolls.\n\n\
            **4d6 .+ 1**: Rolls 4 die with 6 sides and adds 1 to each roll (so a roll of 3 would become 4)\n\n\
            **4d6 .- 1**: Rolls 4 die with 6 sides and subtracts 1 from each roll (so a roll of 3 would become 2)', inline=False)
        await ctx.respond(embed=embed)

    @commands.slash_command(name='resources', description='resources used for/by egirl!')
    async def _resources(self, ctx):
        embed = discord.Embed(title=f'egirl\'s Resource List', description=f'A list of resources used by poppy#0001 for egirl\'s development!', color=0x202225)
        embed.add_field(name='Documentation and Help', value=f'[Discord.js](https://discord.js.org/#/docs/discord.js/main/general/welcome)\n\
            [PyCord](https://docs.pycord.dev/en/stable/)\n\
            [StackOverflow](https://stackoverflow.com/)', inline=False)
        embed.add_field(name='APIs', value=f'[cloverbrandAPI](https://api.cloverbrand.xyz/)\n\
            [DBot API](https://api.dbot.dev/endpoints)\n\
            [OpenWeatherMap API](https://openweathermap.org/api)\n\
            [NekoBot API](https://docs.nekobot.xyz/)\n\
            [Animated Story Titles](https://animatedstorytitles.com/)\n\
            [ChilliHero QOTD](https://chillihero.api.stdlib.com/qotd@0.1.3/question/)\n\
            [dog.ceo API](https://dog.ceo/api)\n\
            [The Cat API](https://thecatapi.com/)\n\
            [MusixMatch API](https://developer.musixmatch.com/)\n\
            [Truth or Dare Bot API](https://docs.truthordarebot.xyz/api-docs)\n\
            [Tenor API](https://docs.truthordarebot.xyz/api-docs)\n\
            [Hypixel API](https://api.hypixel.net/)\n\
            [Mojang API](https://api.mojang.com)\n', inline=False)
        embed.add_field(name='How to Start', value=f'Remember: Anyone can program something! Here\'s a few resources to help you begin!\n\
            [Repl.it](https://replit.com/) - A useful tool to run code online (which even works on phones!)\n\
            [W3Schools](https://www.w3schools.com/) - Free online courses for coding\n\
            [Visual Studio Code Web](https://vscode.dev/) - Free fully online code editor\n\
            [Code With Swastik](https://www.youtube.com/@CodeWithSwastik) - Fantastic PyCord/discord.py video tutorials\n\
            [Worn Off Keys](https://www.youtube.com/@WornOffKeys) - Fantastic discord.js video tutorials\n\
            ', inline=False)
        await ctx.respond(embed=embed)

    @commands.slash_command(name='texttospeech', description='generate an mp3 file of the input text')
    async def _texttospeech(self, ctx, text: Option(str, 'the text to turn into an MP3', required=True)):
        global ttsban
        if not ttsban.get(ctx.author.id):
            ttsban[ctx.author.id] = True
            await ctx.defer()
            if len(text) > 1024: 
                embed = discord.Embed(title='egirl\'s Text to Speech Generator', description=f'Unable to generate text, it is {len(text)-1024} characters too long!')
                embed.set_footer(text=f'{self.bot.user.name} • ©{reportManagerName}', icon_url=f'{self.bot.user.avatar.url}')
                await ctx.respond(embed=embed)
                return
            myobj = gtts.gTTS(text=text, lang='en', slow=False)
            myobj.save(f'temp/tts-{ctx.author.id}.mp3')
            response_file = discord.File(f'temp/tts-{ctx.author.id}.mp3', filename='generated_speech.mp3')
            embed = discord.Embed(title='egirl\'s Text to Speech Generator', description='the generated speech is in the embed above!')
            embed.add_field(name='Text', value=text)
            embed.set_footer(text=f'{self.bot.user.name} • ©{reportManagerName}', icon_url=f'{self.bot.user.avatar.url}')
            await ctx.respond(embed=embed, file=response_file)
            response_file.close()
            os.remove(f'temp/tts-{ctx.author.id}.mp3')
            ttsban.pop(ctx.author.id)
        else: 
            embed = discord.Embed(title='egirl\'s Text to Speech Generator', description=f'Please wait until your text is done generating!')
            embed.set_footer(text=f'{self.bot.user.name} • ©{reportManagerName}', icon_url=f'{self.bot.user.avatar.url}')
            await ctx.respond(embed=embed)
            return

    @commands.slash_command(name='gn-chat', description='say goodnight to chat')
    async def _gn_chat(self, ctx):
        load_dotenv()
        tenorToken = os.getenv('TENOR')
        query, limit = 'gn chat', '10'
        try:
            res = requests.get(f'https://tenor.googleapis.com/v2/search?q={query}&limit={limit}&random=true&media_filter=gif&key={tenorToken}').json()['results'][0]['media_formats']['gif']['url']
            embed = discord.Embed(title=discord.Embed.Empty, description=discord.Embed.Empty)
            embed.set_image(url=res)
            embed.set_footer(text=f'{self.bot.user.name} • ©{reportManagerName}', icon_url=f'{self.bot.user.avatar.url}')
            await ctx.respond(embed=embed)
        except Exception as e:
            embed = discord.Embed(title=discord.Embed.Empty, description=f'**TenorAPI Inaccessible**: {e}\nUse </reportissue:1041952478540877826> or contact the developer!')
            embed.set_footer(text=f'{self.bot.user.name} • ©{reportManagerName}', icon_url=f'{self.bot.user.avatar.url}')
            await ctx.respond(embed=embed)

    @commands.slash_command(name='gm-chat', description='say goodmorning to chat')
    async def _gm_chat(self, ctx):
        load_dotenv()
        tenorToken = os.getenv('TENOR')
        query, limit = 'hello gm chat', '10'
        try:
            res = requests.get(f'https://tenor.googleapis.com/v2/search?q={query}&limit={limit}&random=true&media_filter=gif&key={tenorToken}').json()['results'][0]['media_formats']['gif']['url']
            embed = discord.Embed(title=discord.Embed.Empty, description=discord.Embed.Empty)
            embed.set_image(url=res)
            embed.set_footer(text=f'{self.bot.user.name} • ©{reportManagerName}', icon_url=f'{self.bot.user.avatar.url}')
            await ctx.respond(embed=embed)
        except Exception as e:
            embed = discord.Embed(title=discord.Embed.Empty, description=f'**TenorAPI Inaccessible**: {e}\nUse </reportissue:1041952478540877826> or contact the developer!')
            embed.set_footer(text=f'{self.bot.user.name} • ©{reportManagerName}', icon_url=f'{self.bot.user.avatar.url}')
            await ctx.respond(embed=embed)

    emoji = discord.SlashCommandGroup("emoji", "emoji related commands")

    @emoji.command(name='get', description='get info about an emoji')
    async def _emoji_get(self, ctx, emoji: Option(str, 'the emoji to steal', required=True, min_length=23, max_length=57)):
        split_emoji = emoji.split(':')
        emoji_id = int(emoji.split(':')[2][:-1])
        if '<a' in split_emoji[0]: animated = True
        else: animated = False

        if animated == True: ext = 'gif'
        else: ext = 'png'

        emoji_url = f'https://cdn.discordapp.com/emojis/{emoji_id}.{ext}'

        download_button = Button(label='download emoji', style=discord.ButtonStyle.link, url=emoji_url)
        view = View(timeout=None)#timeout=180, disable_on_timeout=True)
        view.add_item(download_button)

        embed = discord.Embed(title=discord.Embed.Empty, description=discord.Embed.Empty)
        embed.add_field(name='emoji name', value=f':{split_emoji[1]}:', inline=True)
        embed.add_field(name='animated?', value=animated, inline=True)
        embed.add_field(name='emoji id', value=f'`{emoji_id}`', inline=True)
        embed.add_field(name='url', value=emoji_url, inline=False)
        embed.set_image(url=emoji_url)
        embed.set_footer(text=f'{self.bot.user.name} • ©{reportManagerName}', icon_url=f'{self.bot.user.avatar.url}')
        await ctx.respond(embed=embed, view=view)

    @commands.slash_command(name='shorten-url', description='shorten a url using is.gd')
    async def _shorten_url(self, ctx, url: Option(str, 'the url to shorten', required=True)):
        await ctx.defer()
        try:
            res = requests.get(f'https://is.gd/create.php?format=simple&url={url}').text
            if res == 'Error: Please enter a valid URL to shorten':
                embed = discord.Embed(title=discord.Embed.Empty, description=f'**InvalidURLError**: `{url}` is not a valid URL!', color=0x202225)
                embed.set_author(name=f'\u200b', icon_url='https://raw.githubusercontent.com/ignpoppyseed/ignpoppyseed/main/img/x_tossface.png')
                embed.set_footer(text=f'{self.bot.user.name} • ©{reportManagerName}', icon_url=f'{self.bot.user.avatar.url}')
                await ctx.respond(embed=embed, ephemeral=True)
            elif res.startswith('https://is.gd/'):
                embed = discord.Embed(title=discord.Embed.Empty, description=f'shortened url: {res}')
                embed.set_footer(text=f'{self.bot.user.name} • ©{reportManagerName}', icon_url=f'{self.bot.user.avatar.url}')
                await ctx.respond(embed=embed)
        except Exception as e:
            embed = discord.Embed(title=discord.Embed.Empty, description=f'**ShortenURLError**: {e}\nUse </reportissue:0> or contact the developer!', color=0x202225)
            embed.set_author(name=f'\u200b', icon_url='https://raw.githubusercontent.com/ignpoppyseed/ignpoppyseed/main/img/x_tossface.png')
            embed.set_footer(text=f'{self.bot.user.name} • ©{reportManagerName}', icon_url=f'{self.bot.user.avatar.url}')
            await ctx.respond(embed=embed, ephemeral=True)

    @commands.slash_command(name='lyrics', description='get lyrics of a song from musixmatch')
    async def _lyrics(self, ctx, track_title: Option(str, 'the name of the track', required=True), artist_name: Option(str, 'the name of the artist', required=False, default=None)):
        await ctx.defer()
        try:
            load_dotenv()
            musixmatchToken = os.getenv('MUSIX')
            if artist_name is not None:
                artist_name = '&q_artist='+artist_name
            res = requests.get(f'https://api.musixmatch.com/ws/1.1/track.search?q_track={track_title}{artist_name}&apikey={musixmatchToken}').json()
            if res['message']['header']['status_code'] == 200:
                res_ref = res['message']['body']
                if res_ref['track_list'] == []: 
                    embed = discord.Embed(title=discord.Embed.Empty, description=f'No lyrics found! ❌')
                    embed.set_footer(text=f'{self.bot.user.name} • ©{reportManagerName}', icon_url=f'{self.bot.user.avatar.url}')
                    await ctx.respond(embed=embed)
                else:
                    first_result = res_ref['track_list'][0]['track']
                    track_name = first_result['track_name']
                    track_artist = first_result['artist_name']
                    album_name = first_result['album_name']
                    org_track_url = first_result['track_share_url'].split('?')[0]
                    explicit = first_result['explicit']
                    track_id = first_result['track_id']
                    track_has_lyr = first_result['has_lyrics']
                    lyr_copyright = ''
                    lyr_title = 'lyrics'

                    res = requests.get(f'https://is.gd/create.php?format=simple&url={org_track_url}').text
                    if res.startswith('https://is.gd/'): track_url = res
                    else: track_url = org_track_url

                    if track_has_lyr == 0: lyr_desc = 'unable to find official lyrics for this song, but it\'s still in the database. try clicking the song title!'
                    elif track_has_lyr == 1:
                        res = requests.get(f'https://api.musixmatch.com/ws/1.1/track.lyrics.get?track_id={track_id}&apikey={musixmatchToken}').json()['message']['body']['lyrics']
                        lyr_desc = res['lyrics_body'].split('\n\n******* This Lyrics is NOT for Commercial use *******')[0]
                        if explicit == 1: lyr_desc = 'these lyrics are censored because they\'re explicit. click to reveal!\n||'+lyr_desc+'||'
                        lyr_copyright = '\nLyrics Provided by www.musixmatch.com. Not for comercial use.'
                        lyr_title = 'lyrics (clipped to first 30%, click the embed title to view full lyrics!)'
                    embed = discord.Embed(title=f'{track_name} - {track_artist}', description=discord.Embed.Empty, url=org_track_url)
                    embed.add_field(name='album name', value=album_name, inline=True)
                    if explicit == 0: explicit = 'no'
                    elif explicit == 1: explicit = 'yes'
                    embed.add_field(name='explicit?', value=explicit, inline=True)
                    embed.add_field(name='MusixMatch URL', value=track_url, inline=True)
                    embed.add_field(name=lyr_title, value=lyr_desc, inline=False)
                    embed.set_footer(text=f'{self.bot.user.name} • ©{reportManagerName}{lyr_copyright}', icon_url=f'{self.bot.user.avatar.url}')
                    await ctx.respond(embed=embed)
            else:
                status = res['message']['header']['status_code']
                embed = discord.Embed(title=discord.Embed.Empty, description=f'**MusixMatchAPI Inaccessible**: status: {status}\nUse </reportissue:1041952478540877826> or contact the developer!')
                embed.set_footer(text=f'{self.bot.user.name} • ©{reportManagerName}', icon_url=f'{self.bot.user.avatar.url}')
                await ctx.respond(embed=embed)
        except Exception as e:
            embed = discord.Embed(title=discord.Embed.Empty, description=f'**LyricsError**: {e}\nUse </reportissue:0> or contact the developer!', color=0x202225)
            embed.set_author(name=f'\u200b', icon_url='https://raw.githubusercontent.com/ignpoppyseed/ignpoppyseed/main/img/x_tossface.png')
            embed.set_footer(text=f'{self.bot.user.name} • ©{reportManagerName}', icon_url=f'{self.bot.user.avatar.url}')
            await ctx.respond(embed=embed, ephemeral=True)

    @commands.slash_command(name='word-counter', description='count the words in a block of text')
    async def _word_counter(self, ctx, text: Option(str, 'the text to count the words of', required=True)):
        await ctx.defer()
        word_count = str(len(text.split(' ')))
        char_count = str(len(text))
        if len(text) > 1024: send_text = text[:1021]+"..."
        else: send_text = text
        embed = discord.Embed(title=discord.Embed.Empty, description=discord.Embed.Empty)
        embed.add_field(name='words', value=word_count, inline=True)
        embed.add_field(name='characters', value=char_count, inline=True)
        embed.add_field(name='text', value=send_text, inline=False)
        embed.set_footer(text=f'{self.bot.user.name} • ©{reportManagerName}', icon_url=f'{self.bot.user.avatar.url}')
        await ctx.respond(embed=embed)
    
    @commands.slash_command(name='character-counter', description='count the characters in a block of text')
    async def _character_counter(self, ctx, text: Option(str, 'the text to count the characters of', required=True)):
        await ctx.defer()
        word_count = str(len(text.split(' ')))
        char_count = str(len(text))
        if len(text) > 1024: send_text = text[:1021]+"..."
        else: send_text = text
        embed = discord.Embed(title=discord.Embed.Empty, description=discord.Embed.Empty)
        embed.add_field(name='characters', value=char_count, inline=True)
        embed.add_field(name='words', value=word_count, inline=True)
        embed.add_field(name='text', value=send_text, inline=False)
        embed.set_footer(text=f'{self.bot.user.name} • ©{reportManagerName}', icon_url=f'{self.bot.user.avatar.url}')
        await ctx.respond(embed=embed)

    @commands.slash_command(name='ip-gen', description='generate a fake IP address')
    async def _ip_gen(self, ctx):
        await ctx.defer()
        ip = str(random.randrange(10, 255))+'.'+str(random.randrange(10, 255))+'.'+str(random.randrange(10, 255))+'.'+str(random.randrange(10, 255))
        embed = discord.Embed(title=discord.Embed.Empty, description=f'`{ip}`\nthis IP address is randomly generated, please do not DDOS, DOS or otherwise cause harm to it.')
        embed.set_footer(text=f'{self.bot.user.name} • ©{reportManagerName}', icon_url=f'{self.bot.user.avatar.url}')
        await ctx.respond(ip, embed=embed)

    @imagegen.command(name='ip-fortune-cookie', description='generate a fake IP address and put it on a fortune cookie')    
    async def _imagegen_ip_gen(self, ctx):
        await ctx.defer()
        font_size = 130

        x_offset, y_offset = (36, -180)

        ip = str(random.randrange(10, 255))+'.'+str(random.randrange(10, 255))+'.'+str(random.randrange(10, 255))+'.'+str(random.randrange(10, 255))
        img = Image.open('templates/fortune.png')
        toplayer = Image.open('templates/fortune2.png')
        img = img.convert("RGBA")
        toplayer = toplayer.convert("RGBA")
        welcFont = ImageFont.truetype('fonts/roboto.ttf', size=font_size)
        textLayer = Image.new('RGBA', img.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(textLayer)
        text_place_x, text_place_y = img.size
        draw.text((text_place_x/2, text_place_y/2), f'{ip}', (0, 0, 0), anchor="mm", font=welcFont)
        textLayer = textLayer.rotate(-344.7,  expand=False)
        Image.Image.alpha_composite(img, textLayer, (x_offset, y_offset))
        Image.Image.alpha_composite(img, toplayer)
        img.save(f'temp/fortune-{ctx.author.id}.png')
        image_file = discord.File(f'temp/fortune-{ctx.author.id}.png', filename=f'fortune-{ctx.author.id}.png')

        embed = discord.Embed(title=discord.Embed.Empty, description=f'`{ip}`\nthis IP address is randomly generated, please do not DDOS, DOS or otherwise cause harm to it.')
        embed.set_footer(text=f'{self.bot.user.name} • ©{reportManagerName}', icon_url=f'{self.bot.user.avatar.url}')
        embed.set_image(url=f'attachment://fortune-{ctx.author.id}.png')
        await ctx.respond(file=image_file, embed=embed)

def setup(bot):
    bot.add_cog(cog_all(bot))
    print('cog.all loaded')
def teardown(bot):
    print('cog.all unloading')