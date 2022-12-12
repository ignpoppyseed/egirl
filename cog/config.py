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

class cog_config(commands.Cog):
    def __init__(self, bot, *args, **kwargs):
        self.bot = bot

    config = discord.SlashCommandGroup("config", "egirl per-server config commands")
    config_welcome = config.create_subgroup('welcome', 'welcome config commands')
    config_goodbye = config.create_subgroup('goodbye', 'goodbye config commands')
    config_uwumode = config.create_subgroup('uwumode', 'uwumode config commands')

    @config_welcome.command(name='set_channel', description='set or change the welcome channel')
    async def _set_welcome_channel(self, ctx, channel: Option(discord.TextChannel, "channel ID", required=True)):
        if ctx.author.guild_permissions.administrator:
            try:
                db = sqlite3.connect("database.sqlite")
                cursor = db.cursor()
                cursor.execute(f'SELECT server_id FROM data WHERE server_id="{ctx.guild.id}"')
                try: server_result = cursor.fetchone()[0]
                except: server_result = cursor.fetchone()
                if server_result is None:
                    sql = ("INSERT INTO data(server_id, welcome_channel) VALUES(?,?)")
                    val = (ctx.guild.id, channel.id)
                    cursor.execute(sql, val)
                    db.commit()
                    embed = discord.Embed(title=discord.Embed.Empty, description=f'welcome channel set to {channel.mention}', color=0x202225)
                    embed.set_author(name=f'\u200b', icon_url='https://raw.githubusercontent.com/ignpoppyseed/ignpoppyseed/main/img/check_tossface.png')
                    embed.set_footer(text = f'{self.bot.user.name}', icon_url=self.bot.user.display_avatar.url)
                    await ctx.respond(embed=embed)
                else:
                    cursor.execute(f"SELECT welcome_channel FROM data WHERE server_id = {ctx.guild.id}")
                    try: result = cursor.fetchone()[0]
                    except: result = cursor.fetchone()
                    if result is None:
                        if server_result is None:
                            sql = ("INSERT INTO data(server_id, welcome_channel) VALUES(?,?)")
                            val = (ctx.guild.id, channel.id)
                            cursor.execute(sql, val)
                            db.commit()
                            embed = discord.Embed(title=discord.Embed.Empty, description=f'welcome channel set to {channel.mention}', color=0x202225)
                            embed.set_author(name=f'\u200b', icon_url='https://raw.githubusercontent.com/ignpoppyseed/ignpoppyseed/main/img/check_tossface.png')
                            embed.set_footer(text = f'{self.bot.user.name}', icon_url=self.bot.user.display_avatar.url)
                            await ctx.respond(embed=embed)
                        elif server_result is not None:
                            sql = ("UPDATE data SET welcome_channel = ? WHERE server_id = ?")
                            val = (channel.id, ctx.guild.id)
                            cursor.execute(sql, val)
                            db.commit()
                            embed = discord.Embed(title=discord.Embed.Empty, description=f'welcome channel set to {channel.mention}', color=0x202225)
                            embed.set_author(name=f'\u200b', icon_url='https://raw.githubusercontent.com/ignpoppyseed/ignpoppyseed/main/img/check_tossface.png')
                            embed.set_footer(text = f'{self.bot.user.name}', icon_url=self.bot.user.display_avatar.url)
                            await ctx.respond(embed=embed)
                    elif result is not None:
                        sql = ("UPDATE data SET welcome_channel = ? WHERE server_id = ?")
                        val = (channel.id, ctx.guild.id)
                        cursor.execute(sql, val)
                        db.commit()
                        embed = discord.Embed(title=discord.Embed.Empty, description=f'welcome channel changed to {channel.mention}', color=0x202225)
                        embed.set_author(name=f'\u200b', icon_url='https://raw.githubusercontent.com/ignpoppyseed/ignpoppyseed/main/img/check_tossface.png')
                        embed.set_footer(text = f'{self.bot.user.name}', icon_url=self.bot.user.display_avatar.url)
                        await ctx.respond(embed=embed)
                db.close()
            except Exception as e:
                embed = discord.Embed(title=discord.Embed.Empty, description=f'**SQLDatabaseError**: {e}\nUse </reportissue:1041952478540877826> or contact the developer!', color=0x202225)
                embed.set_author(name=f'\u200b', icon_url='https://raw.githubusercontent.com/ignpoppyseed/ignpoppyseed/main/img/x_tossface.png')
                embed.set_footer(text = f'{self.bot.user.name}', icon_url=self.bot.user.display_avatar.url)
                await ctx.respond(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed(title=discord.Embed.Empty, description=f'**PermissionsError**: You must be an administrator to run this command!', color=0x202225)
            embed.set_author(name=f'\u200b', icon_url='https://raw.githubusercontent.com/ignpoppyseed/ignpoppyseed/main/img/x_tossface.png')
            embed.set_footer(text = f'{self.bot.user.name}', icon_url=self.bot.user.display_avatar.url)
            await ctx.respond(embed=embed, ephemeral=True)

    @config_welcome.command(name='remove_channel', description='remove and disable the welcome channel')
    async def _remove_welcome_channel(self, ctx):
        if ctx.author.guild_permissions.administrator:
            try:
                db = sqlite3.connect("database.sqlite")
                cursor = db.cursor()
                cursor.execute(f"SELECT welcome_channel FROM data WHERE server_id = {ctx.guild.id}")
                result = cursor.fetchone()[0]
                if result is None:
                    embed = discord.Embed(title=discord.Embed.Empty, description=f'there was no welcome channel so nothing was removed!', color=0x202225)
                    embed.set_author(name=f'\u200b', icon_url='https://raw.githubusercontent.com/ignpoppyseed/ignpoppyseed/main/img/dash_tossface.png')
                    embed.set_footer(text = f'{self.bot.user.name}', icon_url=self.bot.user.display_avatar.url)
                    await ctx.respond(embed=embed)
                elif result is not None:
                    sql = (f"UPDATE data SET welcome_channel = NULL WHERE server_id = {ctx.guild.id}")
                    embed = discord.Embed(title=discord.Embed.Empty, description=f'welcome channel removed!', color=0x202225)
                    embed.set_author(name=f'\u200b', icon_url='https://raw.githubusercontent.com/ignpoppyseed/ignpoppyseed/main/img/check_tossface.png')
                    embed.set_footer(text = f'{self.bot.user.name}', icon_url=self.bot.user.display_avatar.url)
                    cursor.execute(sql)
                    db.commit()
                    await ctx.respond(embed=embed)
                db.close()
            except Exception as e:
                embed = discord.Embed(title=discord.Embed.Empty, description=f'**SQLDatabaseError**: {e}\nUse </reportissue:0> or contact the developer!', color=0x202225)
                embed.set_author(name=f'\u200b', icon_url='https://raw.githubusercontent.com/ignpoppyseed/ignpoppyseed/main/img/x_tossface.png')
                embed.set_footer(text = f'{self.bot.user.name}', icon_url=self.bot.user.display_avatar.url)
                await ctx.respond(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed(title=discord.Embed.Empty, description=f'**PermissionsError**: You must be an administrator to run this command!', color=0x202225)
            embed.set_author(name=f'\u200b', icon_url='https://raw.githubusercontent.com/ignpoppyseed/ignpoppyseed/main/img/x_tossface.png')
            embed.set_footer(text = f'{self.bot.user.name}', icon_url=self.bot.user.display_avatar.url)
            await ctx.respond(embed=embed, ephemeral=True)

    @config_goodbye.command(name='set_channel', description='set or change the goodbye channel')
    async def _set_goodbye_channel(self, ctx, channel: Option(discord.TextChannel, "channel ID", required=True)):
        if ctx.author.guild_permissions.administrator:
            try:
                db = sqlite3.connect("database.sqlite")
                cursor = db.cursor()
                cursor.execute(f'SELECT server_id FROM data WHERE server_id="{ctx.guild.id}"')
                try: server_result = cursor.fetchone()[0]
                except: server_result = cursor.fetchone()
                if server_result is None:
                    sql = ("INSERT INTO data(server_id, goodbye_channel) VALUES(?,?)")
                    val = (ctx.guild.id, channel.id)
                    cursor.execute(sql, val)
                    db.commit()
                    embed = discord.Embed(title=discord.Embed.Empty, description=f'goodbye channel set to {channel.mention}', color=0x202225)
                    embed.set_author(name=f'\u200b', icon_url='https://raw.githubusercontent.com/ignpoppyseed/ignpoppyseed/main/img/check_tossface.png')
                    embed.set_footer(text = f'{self.bot.user.name}', icon_url=self.bot.user.display_avatar.url)
                    await ctx.respond(embed=embed)
                else:
                    cursor.execute(f"SELECT goodbye_channel FROM data WHERE server_id = {ctx.guild.id}")
                    try: result = cursor.fetchone()[0]
                    except: result = cursor.fetchone()
                    if result is None:
                        if server_result is None:
                            sql = ("INSERT INTO data(server_id, goodbye_channel) VALUES(?,?)")
                            val = (ctx.guild.id, channel.id)
                            cursor.execute(sql, val)
                            db.commit()
                            embed = discord.Embed(title=discord.Embed.Empty, description=f'welcome channel set to {channel.mention}', color=0x202225)
                            embed.set_author(name=f'\u200b', icon_url='https://raw.githubusercontent.com/ignpoppyseed/ignpoppyseed/main/img/check_tossface.png')
                            embed.set_footer(text = f'{self.bot.user.name}', icon_url=self.bot.user.display_avatar.url)
                            await ctx.respond(embed=embed)
                        elif server_result is not None:
                            sql = ("UPDATE data SET goodbye_channel = ? WHERE server_id = ?")
                            val = (channel.id, ctx.guild.id)
                            cursor.execute(sql, val)
                            db.commit()
                            embed = discord.Embed(title=discord.Embed.Empty, description=f'welcome channel set to {channel.mention}', color=0x202225)
                            embed.set_author(name=f'\u200b', icon_url='https://raw.githubusercontent.com/ignpoppyseed/ignpoppyseed/main/img/check_tossface.png')
                            embed.set_footer(text = f'{self.bot.user.name}', icon_url=self.bot.user.display_avatar.url)
                            await ctx.respond(embed=embed)
                    elif result is not None:
                        sql = ("UPDATE data SET goodbye_channel = ? WHERE server_id = ?")
                        val = (channel.id, ctx.guild.id)
                        cursor.execute(sql, val)
                        db.commit()
                        embed = discord.Embed(title=discord.Embed.Empty, description=f'goodbye channel changed to {channel.mention}', color=0x202225)
                        embed.set_author(name=f'\u200b', icon_url='https://raw.githubusercontent.com/ignpoppyseed/ignpoppyseed/main/img/check_tossface.png')
                        embed.set_footer(text = f'{self.bot.user.name}', icon_url=self.bot.user.display_avatar.url)
                        await ctx.respond(embed=embed)
                db.close()
            except Exception as e:
                embed = discord.Embed(title=discord.Embed.Empty, description=f'**SQLDatabaseError**: {e}\nUse </reportissue:1041952478540877826> or contact the developer!', color=0x202225)
                embed.set_author(name=f'\u200b', icon_url='https://raw.githubusercontent.com/ignpoppyseed/ignpoppyseed/main/img/x_tossface.png')
                embed.set_footer(text = f'{self.bot.user.name}', icon_url=self.bot.user.display_avatar.url)
                await ctx.respond(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed(title=discord.Embed.Empty, description=f'**PermissionsError**: You must be an administrator to run this command!', color=0x202225)
            embed.set_author(name=f'\u200b', icon_url='https://raw.githubusercontent.com/ignpoppyseed/ignpoppyseed/main/img/x_tossface.png')
            embed.set_footer(text = f'{self.bot.user.name}', icon_url=self.bot.user.display_avatar.url)
            await ctx.respond(embed=embed, ephemeral=True)

    @config_goodbye.command(name='remove_channel', description='remove and disable the goodbye channel')
    async def _remove_goodbye_channel(self, ctx):
        if ctx.author.guild_permissions.administrator:
            try:
                db = sqlite3.connect("database.sqlite")
                cursor = db.cursor()
                cursor.execute(f"SELECT goodbye_channel FROM data WHERE server_id = {ctx.guild.id}")
                result = cursor.fetchone()[0]
                if result is None:
                    embed = discord.Embed(title=discord.Embed.Empty, description=f'there was no goodbye channel so nothing was removed!', color=0x202225)
                    embed.set_author(name=f'\u200b', icon_url='https://raw.githubusercontent.com/ignpoppyseed/ignpoppyseed/main/img/dash_tossface.png')
                    embed.set_footer(text = f'{self.bot.user.name}', icon_url=self.bot.user.display_avatar.url)
                    await ctx.respond(embed=embed)
                elif result is not None:
                    sql = (f"UPDATE data SET goodbye_channel = NULL WHERE server_id = {ctx.guild.id}")
                    embed = discord.Embed(title=discord.Embed.Empty, description=f'goodbye channel removed!', color=0x202225)
                    embed.set_author(name=f'\u200b', icon_url='https://raw.githubusercontent.com/ignpoppyseed/ignpoppyseed/main/img/check_tossface.png')
                    embed.set_footer(text = f'{self.bot.user.name}', icon_url=self.bot.user.display_avatar.url)
                    cursor.execute(sql)
                    db.commit()
                    await ctx.respond(embed=embed)
            except Exception as e:
                embed = discord.Embed(title=discord.Embed.Empty, description=f'**SQLDatabaseError**: {e}\nUse </reportissue:0> or contact the developer!', color=0x202225)
                embed.set_author(name=f'\u200b', icon_url='https://raw.githubusercontent.com/ignpoppyseed/ignpoppyseed/main/img/x_tossface.png')
                embed.set_footer(text = f'{self.bot.user.name}', icon_url=self.bot.user.display_avatar.url)
                await ctx.respond(embed=embed, ephemeral=True)
            db.close()
        else:
            embed = discord.Embed(title=discord.Embed.Empty, description=f'**PermissionsError**: You must be an administrator to run this command!', color=0x202225)
            embed.set_author(name=f'\u200b', icon_url='https://raw.githubusercontent.com/ignpoppyseed/ignpoppyseed/main/img/x_tossface.png')
            embed.set_footer(text = f'{self.bot.user.name}', icon_url=self.bot.user.display_avatar.url)
            await ctx.respond(embed=embed, ephemeral=True)

    @config_uwumode.command(name='enable', description='enable uwumode')
    async def _uwumode_enable(self, ctx):
        if ctx.author.guild_permissions.administrator:
            try:
                db = sqlite3.connect("database.sqlite")
                cursor = db.cursor()
                cursor.execute(f'SELECT server_id FROM data WHERE server_id="{ctx.guild.id}"')
                try: server_result = cursor.fetchone()[0]
                except: server_result = cursor.fetchone()
                if server_result is None:
                    sql = ("INSERT INTO data(server_id, uwumode) VALUES(?,?)")
                    val = (ctx.guild.id, 'ON')
                    cursor.execute(sql, val)
                    db.commit()
                    embed = discord.Embed(title=discord.Embed.Empty, description=f'uwumode enabled!', color=0x202225)
                    embed.set_author(name=f'\u200b', icon_url='https://raw.githubusercontent.com/ignpoppyseed/ignpoppyseed/main/img/check_tossface.png')
                    embed.set_footer(text = f'{self.bot.user.name}', icon_url=self.bot.user.display_avatar.url)
                    await ctx.respond(embed=embed)
                else:
                    cursor.execute(f"SELECT uwumode FROM data WHERE server_id = {ctx.guild.id}")
                    try: result = cursor.fetchone()[0]
                    except: result = cursor.fetchone()
                    if result is None:
                        sql = ("UPDATE data SET uwumode = ? WHERE server_id = ?")
                        val = ('ON', ctx.guild.id)
                        cursor.execute(sql, val)
                        db.commit()
                        embed = discord.Embed(title=discord.Embed.Empty, description=f'uwumode enabled!', color=0x202225)
                        embed.set_author(name=f'\u200b', icon_url='https://raw.githubusercontent.com/ignpoppyseed/ignpoppyseed/main/img/check_tossface.png')
                        embed.set_footer(text = f'{self.bot.user.name}', icon_url=self.bot.user.display_avatar.url)
                        await ctx.respond(embed=embed)
                    elif result is not None:
                        embed = discord.Embed(title=discord.Embed.Empty, description=f'uwumode was already enabled!', color=0x202225)
                        embed.set_author(name=f'\u200b', icon_url='https://raw.githubusercontent.com/ignpoppyseed/ignpoppyseed/main/img/dash_tossface.png')
                        embed.set_footer(text = f'{self.bot.user.name}', icon_url=self.bot.user.display_avatar.url)
                        await ctx.respond(embed=embed)
                db.close()
            except Exception as e:
                embed = discord.Embed(title=discord.Embed.Empty, description=f'**SQLDatabaseError**: {e}\nUse </reportissue:1041952478540877826> or contact the developer!', color=0x202225)
                embed.set_author(name=f'\u200b', icon_url='https://raw.githubusercontent.com/ignpoppyseed/ignpoppyseed/main/img/x_tossface.png')
                embed.set_footer(text = f'{self.bot.user.name}', icon_url=self.bot.user.display_avatar.url)
                await ctx.respond(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed(title=discord.Embed.Empty, description=f'**PermissionsError**: You must be an administrator to run this command!', color=0x202225)
            embed.set_author(name=f'\u200b', icon_url='https://raw.githubusercontent.com/ignpoppyseed/ignpoppyseed/main/img/x_tossface.png')
            embed.set_footer(text = f'{self.bot.user.name}', icon_url=self.bot.user.display_avatar.url)
            await ctx.respond(embed=embed, ephemeral=True)

    @config_uwumode.command(name='disable', description='disable uwumode')
    async def _uwumode_disable(self, ctx):
        if ctx.author.guild_permissions.administrator:
            try:
                db = sqlite3.connect("database.sqlite")
                cursor = db.cursor()
                cursor.execute(f"SELECT uwumode FROM data WHERE server_id = {ctx.guild.id}")
                #result = cursor.fetchone()
                try: result = cursor.fetchone()[0]
                except: result = cursor.fetchone()
                if result is None:
                    embed = discord.Embed(title=discord.Embed.Empty, description=f'uwumode wasn\'t enabled, so it couldn\'t be disabled!', color=0x202225)
                    embed.set_author(name=f'\u200b', icon_url='https://raw.githubusercontent.com/ignpoppyseed/ignpoppyseed/main/img/dash_tossface.png')
                    embed.set_footer(text = f'{self.bot.user.name}', icon_url=self.bot.user.display_avatar.url)
                    await ctx.respond(embed=embed)
                elif result is not None:
                    sql = (f"UPDATE data SET uwumode = NULL WHERE server_id = {ctx.guild.id}")
                    embed = discord.Embed(title=discord.Embed.Empty, description=f'uwumode disabled!', color=0x202225)
                    embed.set_author(name=f'\u200b', icon_url='https://raw.githubusercontent.com/ignpoppyseed/ignpoppyseed/main/img/check_tossface.png')
                    embed.set_footer(text = f'{self.bot.user.name}', icon_url=self.bot.user.display_avatar.url)
                    cursor.execute(sql)
                    db.commit()
                    await ctx.respond(embed=embed)
                db.close()
            except Exception as e:
                embed = discord.Embed(title=discord.Embed.Empty, description=f'**SQLDatabaseError**: {e}\nUse </reportissue:0> or contact the developer!', color=0x202225)
                embed.set_author(name=f'\u200b', icon_url='https://raw.githubusercontent.com/ignpoppyseed/ignpoppyseed/main/img/x_tossface.png')
                embed.set_footer(text = f'{self.bot.user.name}', icon_url=self.bot.user.display_avatar.url)
                await ctx.respond(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed(title=discord.Embed.Empty, description=f'**PermissionsError**: You must be an administrator to run this command!', color=0x202225)
            embed.set_author(name=f'\u200b', icon_url='https://raw.githubusercontent.com/ignpoppyseed/ignpoppyseed/main/img/x_tossface.png')
            embed.set_footer(text = f'{self.bot.user.name}', icon_url=self.bot.user.display_avatar.url)
            await ctx.respond(embed=embed, ephemeral=True)

def setup(bot):
    bot.add_cog(cog_config(bot))
    print('cog.config loaded')
def teardown(bot):
    print('cog.config unloading')