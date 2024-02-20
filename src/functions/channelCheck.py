import discord
from config import config
from discord.ext import commands

channels = config['repChannels']

async def validate(ctx):
	if ctx.channel.id not in channels:
		channels_list = ' '.join([f'<#{channel}>' for channel in channels])
		try:
			await ctx.delete()
		except:
			await ctx.message.delete()
		finally:
			pass
		await ctx.channel.send(f"{ctx.author.mention}, command usage is available only in {channels_list} channel(s)")
		return False
	else:
		return True
