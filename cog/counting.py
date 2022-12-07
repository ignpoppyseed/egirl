import os, random, discord, time, asyncio, aiohttp, json, sqlite3
from discord import Option, OptionChoice, guild
from discord.ext import tasks, commands
from dotenv import load_dotenv

db = sqlite3.connect("database.sqlite")
cursor = db.cursor()

class cog_counting(commands.Cog):
    def __init__(self, bot, *args, **kwargs):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        try:
            cursor.execute(f"SELECT current_count FROM counting WHERE server_id = {str(message.guild.id)}")
            try: count = int(''.join(cursor.fetchone()))
            except TypeError: count = int(cursor.fetchone())
        except:
            return
        if count is None:
            return
        else:
            try: int(message.content) 
            except: return
            cursor.execute(f"SELECT last_author FROM counting WHERE server_id = {str(message.guild.id)}")
            try: last_author = ''.join(cursor.fetchone())
            except: last_author = '000'
            cursor.execute(f"SELECT reset_type FROM counting WHERE server_id = {str(message.guild.id)}")
            reset_type = ''.join(cursor.fetchone())
            if str(message.author.id) != last_author:
                if int(message.content) == count+1:
                    sql = ("UPDATE counting SET current_count = ? WHERE server_id = ?")
                    val = (count+1, str(message.guild.id))
                    cursor.execute(sql, val)
                    sql = ("UPDATE counting SET last_author = ? WHERE server_id = ?")
                    val = (str(message.author.id), str(message.guild.id))
                    cursor.execute(sql, val)
                    db.commit()
                    await message.add_reaction("a:egirl_check:1047715534566854676")
                else:
                    if reset_type == 'ignore_failure':
                        await message.add_reaction("a:egirl_x:1047723503991930951")
                    elif reset_type == 'reset_on_failure':
                        sql = ("UPDATE counting SET current_count = ? WHERE server_id = ?")
                        val = ('0', str(message.guild.id))
                        cursor.execute(sql, val)
                        sql = ("UPDATE counting SET last_author = ? WHERE server_id = ?")
                        val = ("000", str(message.guild.id))
                        cursor.execute(sql, val)
                        db.commit()
                        embed = discord.Embed(title=discord.Embed.Empty, description=f'{message.author.mention}({message.author}) ruined the count at **{str(count)}**! starting over at 0 <a:egirl_cat_headbang:1047718263842418719>', color=0x202225)
                        embed.set_footer(text = f'{self.bot.user.name}', icon_url=self.bot.user.display_avatar.url)
                        await message.add_reaction("a:egirl_x:1047723503991930951")
                        await message.reply(embed=embed, mention_author=False)
            else:
                if reset_type == 'ignore_failure':
                    await message.add_reaction("a:egirl_x:1047723503991930951")
                elif reset_type == 'reset_on_failure':
                    sql = ("UPDATE counting SET current_count = ? WHERE server_id = ?")
                    val = ('0', str(message.guild.id))
                    cursor.execute(sql, val)
                    sql = ("UPDATE counting SET last_author = ? WHERE server_id = ?")
                    val = ("000", str(message.guild.id))
                    cursor.execute(sql, val)
                    db.commit()
                    embed = discord.Embed(title=discord.Embed.Empty, description=f'{message.author.mention}({message.author}) ruined the count at **{str(count)}**! starting over at 0 <a:egirl_cat_headbang:1047718263842418719>', color=0x202225)
                    embed.set_footer(text = f'{self.bot.user.name}', icon_url=self.bot.user.display_avatar.url)
                    await message.add_reaction("a:egirl_x:1047723503991930951")
                    await message.reply(embed=embed, mention_author=False)

    counting = discord.SlashCommandGroup("counting", "counting config commands")

    @counting.command(name='set_channel', description='set or change the counting channel')
    async def _set_channel(self, ctx, channel: Option(discord.TextChannel, "channel ID", required=True), reset_mode: Option(str, 'whether to reset the count on failure or just ignore it', choices=[
            OptionChoice(name='reset on mistake', value='reset_on_failure'), 
            OptionChoice(name='ignore mistakes', value='ignore_failure')], required=False, default='reset_on_failure')):
        if ctx.author.guild_permissions.administrator:
            try:
                cursor.execute(f"SELECT channel_id FROM counting WHERE server_id = {ctx.guild.id}")
                result = cursor.fetchone()
                if result is None:
                    sql = ("INSERT INTO counting(server_id, channel_id, current_count, reset_type, last_author) VALUES(?,?,0,?,000)")
                    val = (ctx.guild.id, channel.id, reset_mode)
                    reset_mode_str = reset_mode.replace('_', ' ')
                    cursor.execute(sql, val)
                    db.commit()
                    embed = discord.Embed(title=discord.Embed.Empty, description=f'counting channel set to {channel.mention}\nreset mode: `{reset_mode_str}`', color=0x202225)
                    embed.set_author(name=f'\u200b', icon_url='https://raw.githubusercontent.com/ignpoppyseed/ignpoppyseed/main/img/check_tossface.png')
                    embed.set_footer(text = f'{self.bot.user.name}', icon_url=self.bot.user.display_avatar.url)
                    await ctx.respond(embed=embed)
                    cursor.execute(f"SELECT channel_id FROM counting WHERE server_id = {ctx.guild.id}")
                    counting_channel = self.bot.get_channel(int(''.join(cursor.fetchone())))
                    embed = discord.Embed(title=discord.Embed.Empty, description=f'This is now the counting channel, the current count is **0**!', color=0x202225)
                    embed.set_footer(text = f'{self.bot.user.name}', icon_url=self.bot.user.display_avatar.url)
                    await counting_channel.send(embed=embed)
                elif result is not None:
                    sql = ("UPDATE counting SET channel_id = ? WHERE server_id = ?")
                    val = (channel.id, ctx.guild.id)
                    cursor.execute(sql, val)
                    sql = ("UPDATE counting SET reset_type = ? WHERE server_id = ?")
                    val = (reset_mode, ctx.guild.id)
                    cursor.execute(sql, val)
                    db.commit()
                    embed = discord.Embed(title=discord.Embed.Empty, description=f'counting channel changed to {channel.mention}', color=0x202225)
                    embed.set_author(name=f'\u200b', icon_url='https://raw.githubusercontent.com/ignpoppyseed/ignpoppyseed/main/img/check_tossface.png')
                    embed.set_footer(text = f'{self.bot.user.name}', icon_url=self.bot.user.display_avatar.url)
                    await ctx.respond(embed=embed)
                    cursor.execute(f"SELECT channel_id FROM counting WHERE server_id = {ctx.guild.id}")
                    counting_channel = self.bot.get_channel(int(''.join(cursor.fetchone())))
                    cursor.execute(f"SELECT current_count FROM counting WHERE server_id = {ctx.guild.id}")
                    count = ''.join(cursor.fetchone())
                    embed = discord.Embed(title=discord.Embed.Empty, description=f'This is now the counting channel, the current count is **{count}**!', color=0x202225)
                    embed.set_footer(text = f'{self.bot.user.name}', icon_url=self.bot.user.display_avatar.url)
                    await counting_channel.send(embed=embed)
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

    @counting.command(name='remove_channel', description='remove and disable the counting channel')
    async def _remove_channel(self, ctx):
        if ctx.author.guild_permissions.administrator:
            try:
                cursor.execute(f"SELECT channel_id FROM counting WHERE server_id = {ctx.guild.id}")
                result = cursor.fetchone()
                if result is None:
                    embed = discord.Embed(title=discord.Embed.Empty, description=f'there was no counting channel so nothing was removed!', color=0x202225)
                    embed.set_author(name=f'\u200b', icon_url='https://raw.githubusercontent.com/ignpoppyseed/ignpoppyseed/main/img/dash_tossface.png')
                    embed.set_footer(text = f'{self.bot.user.name}', icon_url=self.bot.user.display_avatar.url)
                    await ctx.respond(embed=embed)
                elif result is not None:
                    sql = ("DELETE FROM counting WHERE server_id = ?")
                    val = (str(ctx.guild.id),)
                    embed = discord.Embed(title=discord.Embed.Empty, description=f'counting channel removed!', color=0x202225)
                    embed.set_author(name=f'\u200b', icon_url='https://raw.githubusercontent.com/ignpoppyseed/ignpoppyseed/main/img/check_tossface.png')
                    embed.set_footer(text = f'{self.bot.user.name}', icon_url=self.bot.user.display_avatar.url)
                    cursor.execute(sql, val)
                    db.commit()
                    await ctx.respond(embed=embed)
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

    @counting.command(name='set_count', description='set the current count ')
    async def _set_count(self, ctx, new_count: Option(int, "number to set count to", required=True)):
        if ctx.author.guild_permissions.administrator:
            try:
                cursor.execute(f"SELECT current_count FROM counting WHERE server_id = {ctx.guild.id}")
                result = cursor.fetchone()
                if result is None:
                    embed = discord.Embed(title=discord.Embed.Empty, description=f'**WriteError**: can\'t set the count without a welcome channel!!', color=0x202225)
                    embed.set_author(name=f'\u200b', icon_url='https://raw.githubusercontent.com/ignpoppyseed/ignpoppyseed/main/img/check_tossface.png')
                    embed.set_footer(text = f'{self.bot.user.name}', icon_url=self.bot.user.display_avatar.url)
                    await ctx.respond(embed=embed)
                elif result is not None:
                    sql = ("UPDATE counting SET current_count = ? WHERE server_id = ?")
                    val = (str(new_count), ctx.guild.id)
                    cursor.execute(sql, val)
                    db.commit()
                    embed = discord.Embed(title=discord.Embed.Empty, description=f'count updated to **{new_count}**!', color=0x202225)
                    embed.set_author(name=f'\u200b', icon_url='https://raw.githubusercontent.com/ignpoppyseed/ignpoppyseed/main/img/check_tossface.png')
                    embed.set_footer(text = f'{self.bot.user.name}', icon_url=self.bot.user.display_avatar.url)
                    await ctx.respond(embed=embed, ephemeral=True)
                    cursor.execute(f"SELECT channel_id FROM counting WHERE server_id = {ctx.guild.id}")
                    counting_channel = self.bot.get_channel(int(''.join(cursor.fetchone())))
                    embed = discord.Embed(title=discord.Embed.Empty, description=f'count updated to **{new_count}**!', color=0x202225)
                    embed.set_footer(text = f'{self.bot.user.name}', icon_url=self.bot.user.display_avatar.url)
                    await counting_channel.send(embed=embed)
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
    bot.add_cog(cog_counting(bot))
    print('cog.counting loaded')
def teardown(bot):
    print('cog.other unloading')