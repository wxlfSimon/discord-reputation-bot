import re
import time
import typing
import sqlite3
import discord
import colorama
from discord.utils import get
from colorama import Fore, init
from discord.ext import commands
from ..functions.addRole import addRole
from ..functions.channelCheck import validate, config
colorama.init()

class reps_managment(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.addRole = addRole
        self.data = sqlite3.connect('data.db', timeout = 1)
        self.cursor = self.data.cursor()
        self.cooldownBypass = []
        self.prefix = config['prefix']
        self.cooldown = commands.CooldownMapping.from_cooldown(1, 300, commands.BucketType.member)

    def get_cooldown(self, message: discord.Message) -> typing.Optional[int]:
        bucket = self.cooldown.get_bucket(message)
        if message.author.id in self.cooldownBypass:
            self.cooldownBypass.remove(message.author.id)
            return None
        return bucket.update_rate_limit()

    def reset_cooldown(self, user_id: int):
        self.cooldownBypass.append(user_id)


    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.client.user:
            return
        prefix = config['prefix']
        if message.content.lower().startswith('+rep'):
            if await validate(message):
                ratelimit = self.get_cooldown(message)
                print(ratelimit)
                if ratelimit is not None:
                    current_timestamp = time.time()
                    new_timestamp = int(current_timestamp) + int(ratelimit)
                    return await message.channel.send(f"You're on cooldown. Run command again <t:{new_timestamp}:R> <t:{new_timestamp}:f>")
                content = message.content.lower()[5:].strip()
                args = content.split()
                if len(args) >= 2:
                    user_mention = args[0]
                    try:
                        user_id = re.findall(r'<@(\d+)>', user_mention)
                        user_id = '  '.join(user_id)
                        user = self.client.get_user(int(user_id))
                        if int(user_id) == int(message.author.id):
                            return await message.channel.send(f"nice try, bro", delete_after = 10)
                    except:
                        self.reset_cooldown(message.author.id)
                        return await message.channel.send(f"Please mention a valid user to whom you want to add the reputation.\nRun `{prefix}help` for more info.")
                    if user.bot:
                        self.reset_cooldown(message.author.id)
                        return await message.channel.send(f"You can't rep bots, LOL")
                    reason = ' '.join(args[1:100])
                    self.cursor.execute('INSERT INTO positive VALUES(?, ?, ?)', (user_id, message.author.id, reason))
                    self.data.commit()
                    positive_count = []
                    negative_count = []
                    self.cursor.execute(f'SELECT * FROM positive WHERE user_id = {user.id}')
                    positive = self.cursor.fetchall()
                    for rep in positive:
                        positive_count.append(rep[2])
                    self.cursor.execute(f'SELECT * FROM negative WHERE user_id = {user.id}')
                    negative = self.cursor.fetchall()
                    for rep in negative:
                        negative_count.append(rep[2])
                    embed = discord.Embed(title = f"Positive reputation given to {user.name}", description = f"Positive reputation has successfully been added to {user.name} in our database.", color = discord.Color.brand_green())
                    if user.avatar:
                        embed.set_thumbnail(url = user.avatar)
                    embed.add_field(name = 'Reputation giver', value = f"```{message.author.name}```", inline = True)
                    embed.add_field(name = 'Reputation added to', value = f'```{user.name}```', inline = True)
                    embed.add_field(name = 'Reputation reason', value = f'```{reason}```', inline = True)
                    embed.add_field(name = 'Negative reps', value = f'```{len(negative_count)}```', inline = True)
                    embed.add_field(name = 'Positive reps', value = f'```{len(positive_count)}```', inline = True)
                    embed.add_field(name = 'Reps in total', value = f'```{(len(negative_count) + len(positive_count))}```', inline = True)
                    embed.set_author(name = f"{user.name}", icon_url = user.avatar)
                    embed.set_footer(text = f"Developed by wxlfSimon | https://github.com/wxlfSimon/discord-reputation-bot", icon_url = "https://media.discordapp.net/attachments/1140645551180894209/1140695745486409768/git.png")
                    await message.channel.send(embed = embed)
                    member = await message.guild.fetch_member(user.id)
                    await member.edit(nick = f"[+{len(positive_count)} | -{len(negative_count)}] {member.global_name}")
                    await self.addRole(message.guild, user.id)
                else:
                    self.reset_cooldown(message.author.id)
                    await message.channel.send(f"Please provide the reason for the reputation.\nRun `{prefix}help` for more info.")

        if message.content.lower().startswith('-rep'):
            if await validate(message):
                ratelimit = self.get_cooldown(message)
                if ratelimit is not None:
                    current_timestamp = time.time()
                    new_timestamp = int(current_timestamp) + int(ratelimit)
                    return await message.channel.send(f"You're on cooldown. Run command again <t:{new_timestamp}:R> <t:{new_timestamp}:f>")
                content = message.content.lower()[5:].strip()
                args = content.split()
                if len(args) >= 2:
                    user_mention = args[0]
                    try:
                        user_id = re.findall(r'<@(\d+)>', user_mention)
                        user_id = '  '.join(user_id)
                        user = self.client.get_user(int(user_id))
                        if int(user_id) == int(message.author.id):
                            self.reset_cooldown(message.author.id)
                            return await message.channel.send(f"nice try, bro", delete_after = 10)
                    except:
                        self.reset_cooldown(message.author.id)
                        return await message.channel.send(f"Please mention a valid user to whom you want to add the reputation.\nRun `{prefix}help` for more info.")
                    if user.bot:
                        self.reset_cooldown(message.author.id)
                        return await message.channel.send(f"You can't rep bots, LOL")
                    reason = ' '.join(args[1:100])
                    self.cursor.execute('INSERT INTO negative VALUES(?, ?, ?)', (user_id, message.author.id, reason))
                    self.data.commit()
                    positive_count = []
                    negative_count = []
                    self.cursor.execute(f'SELECT * FROM positive WHERE user_id = {user.id}')
                    positive = self.cursor.fetchall()
                    for rep in positive:
                        positive_count.append(rep[2])
                    self.cursor.execute(f'SELECT * FROM negative WHERE user_id = {user.id}')
                    negative = self.cursor.fetchall()
                    for rep in negative:
                        negative_count.append(rep[2])
                    embed = discord.Embed(title = f"Negative reputation given to {user.name}", description = f"Negative reputation has successfully been added to {user.name} in our database.", color = discord.Color.brand_red())
                    if user.avatar:
                        embed.set_thumbnail(url = user.avatar)
                    embed.add_field(name = 'Reputation giver', value = f"```{message.author.name}```", inline = True)
                    embed.add_field(name = 'Reputation added to', value = f'```{user.name}```', inline = True)
                    embed.add_field(name = 'Reputation reason', value = f'```{reason}```', inline = True)
                    embed.add_field(name = 'Negative reps', value = f'```{len(negative_count)}```', inline = True)
                    embed.add_field(name = 'Positive reps', value = f'```{len(positive_count)}```', inline = True)
                    embed.add_field(name = 'Reps in total', value = f'```{(len(negative_count) + len(positive_count))}```', inline = True)
                    embed.set_author(name = f"{user.name}", icon_url = user.avatar)
                    embed.set_footer(text = f"Developed by wxlfSimon | https://github.com/wxlfSimon/discord-reputation-bot", icon_url = "https://media.discordapp.net/attachments/1140645551180894209/1140695745486409768/git.png")
                    await message.channel.send(embed = embed)
                    member = await message.guild.fetch_member(user.id)
                    await member.edit(nick = f"[+{len(positive_count)} | -{len(negative_count)}] {user.global_name}")
                    await self.addRole(message.guild, user.id)
                else:
                    self.reset_cooldown(message.author.id)
                    await message.channel.send(f"Please provide the reason for the reputation.\nRun `{prefix}help` for more info.")

async def setup(client):
    await client.add_cog(reps_managment(client))