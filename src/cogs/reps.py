import time
import typing
import sqlite3
import discord
import colorama
from colorama import Fore, init
from discord.ext import commands
from ..functions.addRole import addRole
from ..functions.channelCheck import validate, config
colorama.init()

class rep(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.addRole = addRole
        self.data = sqlite3.connect('data.db', timeout = 1)
        self.cursor = self.data.cursor()
        self.dev = config['devs']

    async def addRole(self, guild, userID: int):
        member = await guild.fetch_member(userID)
        if member:
            try:
                positive_count = 0
                negative_count = 0
                self.cursor.execute(f'SELECT * FROM positive WHERE user_id = {userID}')
                positive = self.cursor.fetchall()
                for rep in positive:
                    positive_count += 1
                self.cursor.execute(f'SELECT * FROM negative WHERE user_id = {userID}')
                negative = self.cursor.fetchall()
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

    @commands.Cog.listener()
    async def on_member_join(self, member):
        try:
            positive_count = []
            negative_count = []
            self.cursor.execute(f'SELECT * FROM positive WHERE user_id = {member.id}')
            positive = self.cursor.fetchall()
            for rep in positive:
                positive_count.append(rep[2])
            self.cursor.execute(f'SELECT * FROM negative WHERE user_id = {member.id}')
            negative = self.cursor.fetchall()
            for rep in negative:
                negative_count.append(rep[2])
            if member.global_name:
                await member.edit(nick = f"[+{len(positive_count)} | -{len(negative_count)}] {member.global_name}")
            else:
                await member.edit(nick = f"[+{len(positive_count)} | -{len(negative_count)}] {member.name}")
        except Exception as e:
            print(e)

    @commands.command(aliases = ['p'])
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def profile(self, ctx, user: discord.User = None):
        if user is None:
            user = ctx.author
        try:
            positive_list = []
            negative_list = []
            positive_count = 1
            negative_count = 1
            self.cursor.execute(f'SELECT * FROM positive WHERE user_id = {user.id}')
            positive = self.cursor.fetchall()
            for rep in positive:
                giver = self.client.get_user(int(rep[1]))
                try:
                    positive_list.append(f"From {giver.mention} ({giver}) `->` {str(rep[2])}\n")
                except:
                    positive_list.append(f"From undefinedGiver (undefinedGiverName) `->` {str(rep[2])}\n")
                positive_count += 1
            self.cursor.execute(f'SELECT * FROM negative WHERE user_id = {user.id}')
            negative = self.cursor.fetchall()
            for rep in negative:
                giver = self.client.get_user(int(rep[1]))
                try:
                    negative_list.append(f"From {giver.mention} ({giver}) `->` {str(rep[2])}\n")
                except:
                    negative_list.append(f"From undefinedGiver (undefinedGiverName) `->` {str(rep[2])}\n")
                negative_count += 1
            embed = discord.Embed(title = f"", description = f"", color = discord.Color.light_gray())
            if user.avatar:
                embed.set_thumbnail(url = user.avatar)
            embed.set_author(name = f"{user.name}'s profile", icon_url = user.avatar)
            embed.add_field(name = 'Positive reps', value = f'```{len(positive_list)}```', inline = True)
            embed.add_field(name = 'Negative reps', value = f'```{len(negative_list)}```', inline = True)
            embed.add_field(name = 'Reps in total', value = f'```{(len(negative_list) + len(positive_list))}```', inline = True)
            embed.set_footer(text = f"Developed by wxlfSimon | https://github.com/wxlfSimon/discord-reputation-bot", icon_url = "https://media.discordapp.net/attachments/1140645551180894209/1140695745486409768/git.png")
            if len(positive_list) != 0:
                pos2 = [f'*Due to Discord Embeds limits there are last `5` positive reps given to {user}*\n\n']
                if len(positive_list) > 5:      
                    for rep in positive_list[::-1]:
                        if len(pos2) != 6:
                            pos2.append(rep)
                    pos = '  '.join(pos2)
                else:
                    pos = '  '.join(positive_list)
                embed.add_field(name = 'Positive reps information', value = f'{pos}', inline = True)
            if len(negative_list) != 0:
                neg2 = [f'*Due to Discord Embeds limits there are last `5` negative reps given to {user}*\n\n']
                if len(negative_list) > 5:
                    for rep in negative_list[::-1]:
                        if len(neg2) != 6:
                            neg2.append(rep)
                    neg = '  '.join(neg2)
                else:
                    neg = '  '.join(negative_list)
                embed.add_field(name = 'Negative reps information', value = f'{neg}', inline = True)
            await ctx.send(embed = embed)
            try:
                member = await ctx.guild.fetch_member(int(user.id))
                positive_count = []
                negative_count = []
                self.cursor.execute(f'SELECT * FROM positive WHERE user_id = {member.id}')
                positive = self.cursor.fetchall()
                for rep in positive:
                    positive_count.append(rep[2])
                self.cursor.execute(f'SELECT * FROM negative WHERE user_id = {member.id}')
                negative = self.cursor.fetchall()
                for rep in negative:
                    negative_count.append(rep[2])
                if member.global_name:
                    await member.edit(nick = f"[+{len(positive_count)} | -{len(negative_count)}] {member.global_name}")
                else:
                    await member.edit(nick = f"[+{len(positive_count)} | -{len(negative_count)}] {member.name}")
            except Exception as e:
                print(e)
            await self.addRole(ctx.guild, user.id)
        except Exception as e:
            embed = discord.Embed(title = "Unexpected error", description = f"```{e}```")
            await ctx.send(content = "`❓` Oops...", embed = embed, delete_after = 10)

    @commands.command(aliases = ['lb'])
    async def leadboard(self, ctx):
        self.cursor.execute(f'SELECT user_id, COUNT(reason) AS reason_count FROM positive GROUP BY user_id ORDER BY reason_count DESC LIMIT 10')
        positive = self.cursor.fetchall()
        positiveTop = []
        positiveTopCount = 1
        for rep in positive:
            user = self.client.get_user(int(rep[0]))
            try:
                positiveTop.append(f"`{positiveTopCount}.` {user.mention} ({user.name}) `->` {rep[1]} positive reps\n")
            except:
                positiveTop.append(f"`{positiveTopCount}.` undefinedUser (undefinedUserName) `->` {rep[1]} positive reps\n")
            positiveTopCount += 1
        positiveTopResult = '  '.join(positiveTop)
        self.cursor.execute(f'SELECT user_id, COUNT(reason) AS reason_count FROM negative GROUP BY user_id ORDER BY reason_count DESC LIMIT 10')
        negative = self.cursor.fetchall()
        negativeTop = []
        negativeTopCount = 1
        for rep in negative:
            user = self.client.get_user(int(rep[0]))
            try:
                negativeTop.append(f"`{negativeTopCount}.` {user.mention} ({user.name}) `->` {rep[1]} negative reps\n")
            except:
                negativeTop.append(f"`{negativeTopCount}.` undefinedUser (undefinedUserName) `->` {rep[1]} negative reps\n")
            negativeTopCount += 1
        negativeTopCountResult = '  '.join(negativeTop)
        embed = discord.Embed(title = "", description = "", color = discord.Color.light_gray())
        embed.add_field(name = 'Top 10 by positive reputation', value = positiveTopResult, inline = True)
        embed.add_field(name = 'Top 10 by negative reputation', value = negativeTopCountResult, inline = True)
        embed.set_author(name = self.client.user.name, icon_url = self.client.user.avatar)
        embed.set_footer(text = f"Developed by wxlfSimon | https://github.com/wxlfSimon/discord-reputation-bot", icon_url = "https://media.discordapp.net/attachments/1140645551180894209/1140695745486409768/git.png")
        await ctx.send(embed = embed)

    @commands.command()
    async def recover(self, ctx, oldID, newID):
        if ctx.author.id in self.dev:
            try:
                user = self.client.get_user(int(newID))
            except Exception as e:
                embed = discord.Embed(title = "Unexpected error", description = f"```{e}```")
                return await ctx.send(content = "`❓` Oops...", embed = embed)
            await ctx.send(f"Getting `{oldID}` reputation...")
            self.cursor.execute(f'SELECT * FROM positive WHERE user_id = {int(oldID)}')
            positive = self.cursor.fetchall()
            if positive:
                await ctx.send(f"Positive reputation found.")
                positive_count = 0
                for rep in positive:
                    self.cursor.execute('INSERT INTO positive VALUES(?, ?, ?)', (user.id, rep[1], rep[2]))
                    self.data.commit()
                    positive_count += 1
                await ctx.send(f"Recovered {positive_count} positive rep(s).")
            else:
                await ctx.send(f"No positive reputation found.")
            self.cursor.execute(f'SELECT * FROM negative WHERE user_id = {int(oldID)}')
            negative = self.cursor.fetchall()
            if negative:
                await ctx.send(f"Negative reputation found.")
                negative_count = 0
                for rep in negative:
                    self.cursor.execute('INSERT INTO negative VALUES(?, ?, ?)', (user.id, rep[1], rep[2]))
                    self.data.commit()
                    negative_count += 1
                await ctx.send(f"Recovered {negative_count} negative rep(s).")
            else:
                await ctx.send(f"No negative reputation found.")
            try:
                member = await ctx.guild.fetch_member(int(newID))
                positive_count = []
                negative_count = []
                self.cursor.execute(f'SELECT * FROM positive WHERE user_id = {member.id}')
                positive = self.cursor.fetchall()
                for rep in positive:
                    positive_count.append(rep[2])
                self.cursor.execute(f'SELECT * FROM negative WHERE user_id = {member.id}')
                negative = self.cursor.fetchall()
                for rep in negative:
                    negative_count.append(rep[2])
                if member.global_name:
                    await member.edit(nick = f"[+{len(positive_count)} | -{len(negative_count)}] {member.global_name}")
                else:
                    await member.edit(nick = f"[+{len(positive_count)} | -{len(negative_count)}] {member.name}")
            except Exception as e:
                print(e)
            await self.addRole(ctx.guild, user.id)

    @commands.command(aliases = ['repsid', 'ids','id'])
    async def reps(self, ctx, user: discord.User = None):
        if user is None:
            return await ctx.send(f"Provide a valid user whose rep(s) IDs you want to get.")
        if user == ctx.author:
            return await ctx.send(f"You can't review your rep(s) IDs.")
        positive_list = [f'**Positive reputation(s) IDs you have given to {user.name}**\nID           GIVER            REASON\n\n']
        negative_list = [f'**Negative reputation(s) IDs you have given to {user.name}**\nID           GIVER            REASON\n\n']
        positive_count = 0
        negative_count = 0
        self.cursor.execute(f'SELECT rowid, * FROM positive WHERE user_id = {user.id} AND giver = {ctx.author.id}')
        positive = self.cursor.fetchall()
        for rep in positive:
            giver = self.client.get_user(int(rep[2]))
            try:
                positive_list.append(f"`{rep[0]}` {giver.mention} ({giver}) {str(rep[3])}\n")
            except:
                positive_list.append(f"`{rep[0]}` undefinedGiver (undefinedGiverName) {str(rep[3])}\n")
            positive_count += 1
        self.cursor.execute(f'SELECT rowid, * FROM negative WHERE user_id = {user.id} AND giver = {ctx.author.id}')
        negative = self.cursor.fetchall()
        for rep in negative:
            giver = self.client.get_user(int(rep[2]))
            try:
                negative_list.append(f"`{rep[0]}` {giver.mention} ({giver}) {str(rep[3])}\n")
            except:
                negative_list.append(f"`{rep[0]}` undefinedGiver (undefinedGiverName) {str(rep[3])}\n")
            negative_count += 1
        if positive_count == 0:
            positive_list.clear()
            positive_list.append(f"**Positive reputation(s) IDs you have given to {user.name}**\n*No rep(s) IDs found.*")
        if negative_count == 0:
            negative_list.clear()
            negative_list.append(f"**Negative reputation(s) IDs you have given to {user.name}**\n*No rep(s) IDs found.*")
        pos = '  '.join(positive_list)
        neg = '  '.join(negative_list)
        embed = discord.Embed(title = f"{user.name}'s reputation(s) IDs", description = f"{pos}\n{neg}", color = discord.Color.light_gray())
        embed.set_author(name = self.client.user.name, icon_url = self.client.user.avatar)
        embed.set_footer(text = f"Developed by wxlfSimon | https://github.com/wxlfSimon/discord-reputation-bot", icon_url = "https://media.discordapp.net/attachments/1140645551180894209/1140695745486409768/git.png")
        if user.avatar:
            embed.set_thumbnail(url = user.avatar)
        await ctx.send(embed = embed)
        await self.addRole(ctx.guild, user.id)

    @commands.command(aliases = ['posremove', 'positiverepremove', 'removepostive', 'positivedelete'])
    async def positiveremove(self, ctx, repID: int = None):
        if repID is None:
            if repID is None:
                return await ctx.send(f"Provide a valid reputation ID.\nUse `!reps @username` to get user's reputation(s) IDs.")
        self.cursor.execute(f'SELECT rowid, * FROM positive WHERE giver = {ctx.author.id} AND rowid = {repID}')
        positive = self.cursor.fetchone()
        if positive:
            class ConfirmOrCancel(discord.ui.View):
                def __init__(self):
                    super().__init__(timeout = None)
                    self.data = sqlite3.connect('data.db', timeout = 1)
                    self.cursor = self.data.cursor()
                    self.ctx = ctx

                @discord.ui.button(label = 'Confirm', style = discord.ButtonStyle.grey, custom_id = 'Confirmed', disabled = False)
                async def confirm_button(self, interaction: discord.Interaction, button: discord.ui.Button):
                    if interaction.user.id == ctx.author.id:
                        await interaction.response.send_message(f"Starting reputation deleting process right now.", ephemeral = True)
                        self.cursor.execute(f"DELETE FROM positive WHERE giver = {ctx.author.id} AND rowid = {repID}")
                        self.data.commit()
                        try:
                            member = await ctx.guild.fetch_member(int(positive[1]))
                            positive_count = []
                            negative_count = []
                            self.cursor.execute(f'SELECT * FROM positive WHERE user_id = {member.id}')
                            positive2 = self.cursor.fetchall()
                            for rep in positive2:
                                positive_count.append(rep[2])
                            self.cursor.execute(f'SELECT * FROM negative WHERE user_id = {member.id}')
                            negative = self.cursor.fetchall()
                            for rep in negative:
                                negative_count.append(rep[2])
                            if member.global_name:
                                await member.edit(nick = f"[+{len(positive_count)} | -{len(negative_count)}] {member.global_name}")
                            else:
                                await member.edit(nick = f"[+{len(positive_count)} | -{len(negative_count)}] {member.name}")
                            await self.addRole(ctx.guild, member.id)
                        except Exception as e:
                            print(e)
                        await ctx.send(f"Reputation successfully deleted.")
                    else:
                        await interaction.response.send_message(f"`❌ ERROR` | Only the user who used the command ({ctx.author.mention}) can manage this.", ephemeral = True)
            embed = discord.Embed(title = "Are you sure?", description = f"After confirmation, reputation with ID `{positive[0]}` and reason `{positive[3]}` will be deleted from the user `{positive[1]}.`", color = discord.Color.light_gray())
            embed.set_author(name = self.client.user.name, icon_url = self.client.user.avatar)
            embed.set_footer(text = f"Developed by wxlfSimon | https://github.com/wxlfSimon/discord-reputation-bot", icon_url = "https://media.discordapp.net/attachments/1140645551180894209/1140695745486409768/git.png")
            await ctx.send(embed = embed, view = ConfirmOrCancel())
        else:
            await ctx.send(f"You aren't the reputation giver for reputation with ID `{repID}`.")

    @commands.command(aliases = ['negremove', 'negativerepremove', 'removenegative', 'negativedelete'])
    async def negativeremove(self, ctx, repID: int = None):
        if repID is None:
            return await ctx.send(f"Provide a valid reputation ID.\nUse `!reps @username` to get user's reputation(s) IDs.")
        self.cursor.execute(f'SELECT rowid, * FROM negative WHERE giver = {ctx.author.id} AND rowid = {repID}')
        negative = self.cursor.fetchone()
        if negative:
            class ConfirmOrCancel(discord.ui.View):
                def __init__(self):
                    super().__init__(timeout = None)
                    self.data = sqlite3.connect('data.db', timeout = 1)
                    self.cursor = self.data.cursor()
                    self.ctx = ctx

                @discord.ui.button(label = 'Confirm', style = discord.ButtonStyle.grey, custom_id = 'Confirmed', disabled = False)
                async def confirm_button(self, interaction: discord.Interaction, button: discord.ui.Button):
                    if interaction.user.id == ctx.author.id:
                        await interaction.response.send_message(f"Starting reputation deleting process right now.", ephemeral = True)
                        self.cursor.execute(f"DELETE FROM negative WHERE giver = {ctx.author.id} AND rowid = {repID}")
                        self.data.commit()
                        try:
                            member = await ctx.guild.fetch_member(int(negative[1]))
                            positive_count = []
                            negative_count = []
                            self.cursor.execute(f'SELECT * FROM positive WHERE user_id = {member.id}')
                            positive = self.cursor.fetchall()
                            for rep in positive:
                                positive_count.append(rep[2])
                            self.cursor.execute(f'SELECT * FROM negative WHERE user_id = {member.id}')
                            negative2 = self.cursor.fetchall()
                            for rep in negative2:
                                negative_count.append(rep[2])
                            if member.global_name:
                                await member.edit(nick = f"[+{len(positive_count)} | -{len(negative_count)}] {member.global_name}")
                            else:
                                await member.edit(nick = f"[+{len(positive_count)} | -{len(negative_count)}] {member.name}")
                            await self.addRole(ctx.guild, member.id)
                        except Exception as e:
                            print(e)
                        await ctx.send(f"Reputation successfully deleted.")
                    else:
                        await interaction.response.send_message(f"`❌ ERROR` | Only the user who used the command ({ctx.author.mention}) can manage this.", ephemeral = True)
            embed = discord.Embed(title = "Are you sure?", description = f"After confirmation, reputation with ID `{negative[0]}` and reason `{negative[3]}` will be deleted from the user `{negative[1]}.`", color = discord.Color.light_gray())
            embed.set_author(name = self.client.user.name, icon_url = self.client.user.avatar)
            embed.set_footer(text = f"Developed by wxlfSimon | https://github.com/wxlfSimon/discord-reputation-bot", icon_url = "https://media.discordapp.net/attachments/1140645551180894209/1140695745486409768/git.png")
            await ctx.send(embed = embed, view = ConfirmOrCancel())
        else:
            await ctx.send(f"You aren't the reputation giver for reputation with ID `{repID}`.")
    
    @profile.error
    async def reps_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f'`❌ ERROR` | You must wait {round(error.retry_after, 2)} second(s) before you can use another command again.')

async def setup(client):
    await client.add_cog(rep(client))