import sqlite3
import discord
from discord.utils import get
from discord.ext import commands

async def addRole(guild, userID: int):
    member = await guild.fetch_member(userID)
    data = sqlite3.connect('././data.db', timeout = 1)
    cursor = data.cursor()
    if member:
        try:
            positive_count = 0
            negative_count = 0
            cursor.execute(f'SELECT * FROM positive WHERE user_id = {userID}')
            positive = cursor.fetchall()
            for rep in positive:
                positive_count += 1
            cursor.execute(f'SELECT * FROM negative WHERE user_id = {userID}')
            negative = cursor.fetchall()
            for rep in negative:
                negative_count += 1
        except Exception as e:
            return print(e)
        if int(positive_count - negative_count) >= 10:
            trustedRole = discord.utils.get(guild.roles, name = "trusted | 10+ reps")
            if trustedRole:
                if trustedRole not in member.roles:
                    await member.add_roles(trustedRole)
                    await member.send(f"You have been granted the `trusted` role on the **{guild}** server due to your accumulation of 10 or more positive reputation points. Congratulations!")
            else:
                await guild.create_role(name = "trusted | 10+ reps", color = discord.Color.brand_green())
                trustedRole = discord.utils.get(guild.roles, name = "trusted | 10+ reps")
                await member.add_roles(trustedRole)
                await member.send(f"You have been granted the `trusted` role on the **{guild}** server due to your accumulation of 10 or more positive reputation points. Congratulations!")
        if int(positive_count - negative_count) >= 20:
            trustedRole = discord.utils.get(guild.roles, name = "fr trusted | 20+ reps")
            if trustedRole:
                if trustedRole not in member.roles:
                    await member.add_roles(trustedRole)
                    await member.send(f"You have been granted the `fr trusted` role on the **{guild}** server due to your accumulation of 20 or more positive reputation points. Congratulations!")
            else:
                trustedRole10 = discord.utils.get(guild.roles, name = "trusted | 10+ reps")
                await guild.create_role(name = "fr trusted | 20+ reps", color = discord.Color.green())
                trustedRole = discord.utils.get(guild.roles, name = "fr trusted | 20+ reps")
                await trustedRole.edit(position = int(trustedRole10.position))
                await member.add_roles(trustedRole)
                await member.send(f"You have been granted the `fr trusted` role on the **{guild}** server due to your accumulation of 20 or more positive reputation points. Congratulations!")
        if int(positive_count - negative_count) <= 10:
            trustedRole = discord.utils.get(guild.roles, name = "trusted | 10+ reps")
            if trustedRole in member.roles:
                await member.remove_roles(trustedRole)
                await member.send(f"Unfortunately, you have lost the `trusted` role on the **{guild}** server due to a decrease in your positive reputation points. Please feel free to work towards regaining the role. Best of luck!")
        if int(positive_count - negative_count) <= 20:
            trustedRole = discord.utils.get(guild.roles, name = "fr trusted | 20+ reps")
            if trustedRole in member.roles:
                await member.remove_roles(trustedRole)
                await member.send(f"Unfortunately, you have lost the `fr trusted` role on the **{guild}** server due to a decrease in your positive reputation points. Please feel free to work towards regaining the role. Best of luck!")
