import os
import discord
import sqlite3
import colorama
from os import path
from config import config
from colorama import Fore, init
from discord.ext import commands
colorama.init()

client = commands.Bot(command_prefix = config['prefix'], intents = discord.Intents.all(), description = 'Discord Reputation Bot')
client.remove_command('help')

devs = config['devs']
prefix = config['prefix']

async def load_cogs():
    for filename in os.listdir('./src/cogs'):
        if filename.endswith('.py'):
            try:
                await client.load_extension(f'src.cogs.{filename[:-3]}')
                print(f'[{Fore.GREEN}+{Fore.RESET}] Loaded {filename[:-3]}')
            except Exception as e:
                print(f'[{Fore.RED}-{Fore.RESET}] Failed to load extension {filename}: {e}')

@client.event
async def on_ready():
	await load_cogs()
	try:
		await client.tree.sync()
	except Exception as e:
		print(e)
	data = sqlite3.connect('data.db')
	cursor = data.cursor()
	cursor.execute('''CREATE TABLE IF NOT EXISTS positive (
		user_id INT,
		giver INT,
		reason TEXT
	)''')
	cursor.execute('''CREATE TABLE IF NOT EXISTS negative (
		user_id INT,
		giver INT,
		reason TEXT
	)''')
	data.commit()
	activity = discord.Activity(type = discord.ActivityType.custom, name = f'{client.user.name} | !help')
	await client.change_presence(status = discord.Status.online, activity = activity)
	print(f'[{Fore.GREEN}+{Fore.RESET}] Logged in as {client.user} | {client.user.id}')

@client.command()
async def help(ctx):
	embed = discord.Embed(title = 'Available bot commands', description = '`<  >` - required arguments\n`[  ]` - not required arguments\n\nㅤ')
	embed.add_field(name = '+rep < `@username` > < `reason` >', value = 'Adds positive reputation to user', inline = True)
	embed.add_field(name = '-rep < `@username` > < `reason` >', value = 'Adds negative reputation to user', inline = True)
	embed.add_field(name = f'{prefix}profile [ `@username` ]', value = "Shows user's / message author profile", inline = True)
	embed.add_field(name = f'{prefix}posremove < `reputationID` >', value = 'Removes positive reputation you have given to user by ID', inline = True)
	embed.add_field(name = f'{prefix}negremove < `reputationID` >', value = 'Removes negative reputation you have given to user by ID', inline = True)
	embed.add_field(name = f'{prefix}reps < `@username` >', value = 'Shows reputation(s) IDs you have given to user', inline = True)
	embed.add_field(name = f'{prefix}leadboard', value = 'Shows top 10 by positive and negative reputation', inline = True)
	embed.set_author(name = client.user.name, icon_url = client.user.avatar)
	embed.set_footer(text = f'Developed by wxlfSimon | https://github.com/wxlfSimon/discord-reputation-bot', icon_url = 'https://media.discordapp.net/attachments/1140645551180894209/1140695745486409768/git.png')
	await ctx.send(embed = embed)

@client.command()
async def load(ctx, extension):
	if ctx.author.id in devs:
		client.load_extension(f'cogs.{extension}')
		await ctx.send('Done')
	else:
		await ctx.send('You cannot use this command.')

@client.command()
async def unload(ctx, extension):
	if ctx.author.id in devs:
		client.unload_extension(f'cogs.{extension}')
		await ctx.send('Done')
	else:
		await ctx.send('You cannot use this command.')

@client.command()
async def reload(ctx, extension):
	if ctx.author.id in devs:
		client.unload_extension(f'cogs.{extension}')
		client.load_extension(f'cogs.{extension}')
		await ctx.send('Done')
	else:
		await ctx.send('You cannot use this command.')

@client.command()
async def leave(ctx):
	if ctx.author.id in devs:
		await client.get_guild(int(ctx.guild.id)).leave()
	else:
		return

@client.command()
async def data(ctx):
	if ctx.author.id in devs:
		await ctx.send(file = discord.File(f'{path.dirname(path.realpath(__file__))}\\data.db'))

client.run(config['token'])
