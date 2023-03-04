import discord
from discord.ext import tasks, commands
from discord.utils import get
from dotenv import load_dotenv
from openpyxl import Workbook
import asyncio
import os

#For a more secure, we loaded the .env file and assign the token value to a variable 
load_dotenv(".env")
TOKEN = os.getenv("TOKEN")

#Intents are permissions for the bot that are enabled based on the features necessary to run the bot.
intents=discord.Intents.all()

#Comman prefix is setup here, this is what you have to type to issue a command to the bot
prefix = '$'
bot = commands.Bot(command_prefix=prefix, intents=intents)

#Removed the help command to create a custom help guide
bot.remove_command('help')

#------------------------------------------------Events------------------------------------------------------#

# Get the id of the rules channel
# @bot.event
# async def on_ready():
#     print('Bot is ready to use!')
#     for guild in bot.guilds:
#         for channel in guild.text_channels:
#             if str(channel).strip() == "📑rules":
#                 # id of the channel you have setup as your rules channel
#                 global verify_channel_id
#                 verify_channel_id = channel.id
#                 break

# # Called when a reaction is added to a message
# @bot.event 
# async def on_raw_reaction_add(reaction):
#     # check if the reaction came from the correct channel
#     if reaction.channel_id == verify_channel_id:
#         # Check what emoji was reacted as
#         if str(reaction.emoji) == "✅":
#              # Add the user role
#             verified_role = get(reaction.member.guild.roles, name = "membears")
#             await reaction.member.add_roles(verified_role)
#             await reaction.member.send(f"Hi {reaction.member.name}, you have joined the membears!")

#Welcome new members to the server
@bot.event
async def on_member_join(member):
    #When a member joins the discord, they will get mentioned with this welcome message
    await member.create_dm()
    await member.dm_channel.send(f'Hi {member.name}, welcome to our Discord server!\nMake sure to read our guidelines in the welcome channel.')

#Basic Discord Bot Commands: Chat with your bot!
@bot.command(name='hello')
async def msg(ctx):
    if ctx.author == bot.user:
        return
    else:
        await ctx.send("Hello there!")

#Delete the blacklist message and warn the user to refrain them from sending using such words again.
@bot.event
async def on_message(message):
    if prefix in message.content:
        print("This is a command")
        await bot.process_commands(message)
    else:
        with open("words_blacklist.txt") as bf:
            blacklist = [word.strip().lower() for word in bf.readlines()]
        bf.close()

        channel = message.channel
        for word in blacklist:
            if word in message.content:
                bot_message = await channel.send("Message contains  a banned word!")
                await message.delete()
                await asyncio.sleep(3)
                await bot_message.delete()
                
        await bot.process_commands(message)
#This code block uses a dictionary message_count to store the number of messages sent by each user. Every time the on_message.
# message_count = {}

# @bot.event
# async def on_message(message):
#     if message.author in message_count:
#         message_count[message.author] += 1
#     else:
#         message_count[message.author] = 1


#-----------------------------------------Moderation---------------------------------------------------------------#

@bot.event
async def on_command_error(context, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await context.send("Oh no! Looks like you have missed out an argument for this command.")
    if isinstance(error, commands.MissingPermissions):
        await context.send("Oh no! Looks like you Dont have the permissions for this command.")
    if isinstance(error, commands.MissingRole):
        await context.send("Oh no! Looks like you Dont have the roles for this command.")
    #bot errors
    if isinstance(error, commands.BotMissingPermissions):
        await context.send("Oh no! Looks like I Dont have the permissions for this command.")
    if isinstance(error, commands.BotMissingRole):
        await context.send("Oh no! Looks like I Dont have the roles for this command.")

@bot.event
async def on_ready():
    # Get all the channels in the server
    channels = bot.get_all_channels()
    # Iterate through the channels
    for channel in channels:
        if isinstance(channel, discord.TextChannel):
            # Check if the channel name is "admin"
            if channel.name == "admin":
                # Send a message and add a reaction to the channel
                message = await channel.send("Welcome to the admin channel!")
                await message.add_reaction('📝')

@bot.event
async def on_raw_reaction_add(payload):
    if payload.emoji.name == '📝' and payload.message_id == 'message-id':
        channel = bot.get_channel(payload.channel_id)
        await channel.send("Please fill out the following form:")
        await channel.send("Name:")
        await channel.send("Email:")
        await channel.send("Phone Number:")
        await channel.send("Country:")
        await channel.send("Age:")
        await channel.send("Submit your form by typing 'submit' when done.")
        def check(m):
            return m.author.id == payload.user_id and m.channel == channel
        msg = await bot.wait_for('message', check=check)
        if msg.content == "submit":
            await channel.send(f"Form submitted by {msg.author.name}")
    

#|------------------COMMANDS------------------|   
@bot.command()
async def help(message):
    helpC = discord.Embed(title="Fuzzy Bot \nHelp Guide", description="discord bot built for moderation",color=0x00ff00)
    helpC.add_field(name="Clear", value="To use this command type $clear and the number of messages you would like to delete, the default is 5.", inline=False)
    helpC.add_field(name="kick/ban/unban", value="To use this command type $kick/$ban/$unban then mention the user you would like to perform this on, NOTE: user must have permissions to use this command.", inline=False)
    helpC.add_field(name="$create_channel", value="create a new  channels with it", inline=False)
    helpC.add_field(name="$delete_channel", value="delete channels with it", inline=False)
    helpC.add_field(name="$create_category", value="create a new category with it", inline=False)
    helpC.add_field(name="$delete_category", value="delete a category with it", inline=False)
    helpC.add_field(name="$create_category_with_channels", value="create a new category and channels with it", inline=False)
    helpC.add_field(name="$delete_category_with_channels", value="delete a category and channels with it", inline=False)
    helpC.add_field(name="$register", value="register a user by passing name, TAG ,email and DiscordID", inline=False)


    await message.channel.send(embed=helpC)

@bot.command()
#Checks whether the user has the correct permissions when this command is issued
@commands.has_permissions(manage_messages=True)
async def clear(context, amount=5):
    await context.channel.purge(limit=amount+1)

#Kick and ban work in a similar way as they both require a member to kick/ban and a reason for this
#As long as the moderator has the right permissions the member will be banned/kicked
@bot.command()
@commands.has_permissions(kick_members=True)   
async def kick(context, member : discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await context.send(f'Member {member} kicked')

@bot.command()
@commands.has_permissions(ban_members=True)   
async def ban(context, member : discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await context.send(f'{member} has been banned')

#Unbanning a member is done via typing ./unban and the ID of the banned member
@bot.command()
@commands.has_permissions(ban_members=True)   
async def unban(context, id : int):
    user = await bot.fetch_user(id)
    await context.guild.unban(user)
    await context.send(f'{user.name} has been unbanned')
    
#Bans a member for a specific number of days
@bot.command()
@commands.has_permissions(ban_members=True)
async def softban(context, member : discord.Member, days, reason=None):
    #Asyncio uses seconds for its sleep function
    #multiplying the num of days the user enters by the num of seconds in a day
    days * 86400 
    await member.ban(reason=reason)
    await context.send(f'{member} has been softbanned')
    await asyncio.sleep(days)
    print("Time to unban")
    await member.unban()
    await context.send(f'{member} softban has finished')

#This command will add a word to the blacklist to prevent users from typing that specific word
@bot.command()
@commands.has_permissions(ban_members=True)
async def blacklist_add(context, *, word):
    with open("words_blacklist.txt", "a") as f:
        f.write(word+"\n")
    f.close()

    await context.send(f'Word "{word}" added to blacklist.')
#This command will make different chanels and delete also
@bot.command()
async def create_channel(ctx, channel_name: str):
    channel = await ctx.guild.create_text_channel(channel_name)
    await ctx.send(f'Created text channel {channel_name}')
@bot.command()
async def delete_channel(ctx, channel_name: str):
    channel = discord.utils.get(ctx.guild.text_channels, name=channel_name)
    if channel is not None:
        await channel.delete()
        await ctx.send(f'Deleted text channel {channel_name}')
    else:
        await ctx.send(f'{channel_name} channel not found.')
#This command will make different category and delete also
@bot.command()
async def create_category(ctx, category_name: str):
    category = await ctx.guild.create_category(category_name)
    await ctx.send(f'Created category {category_name}')

@bot.command()
async def delete_category(ctx, category_name: str):
    category = discord.utils.get(ctx.guild.categories, name=category_name)
    if category is not None:
        await category.delete()
        await ctx.send(f'Deleted category {category_name}')
    else:
        await ctx.send(f'{category_name} category not found.')
# Create catagory with channels 
@bot.command()
async def create_category_with_channels(ctx, category_name: str):
    category = await ctx.guild.create_category(category_name)
    channel1 = await ctx.guild.create_text_channel("Registration", category=category)
    channel2 = await ctx.guild.create_text_channel("chat1", category=category)
    channel3 = await ctx.guild.create_text_channel("chat2", category=category)
    channel4 = await ctx.guild.create_text_channel("chat3", category=category)
    await ctx.send(f'Created category {category_name} and channels {channel1.name}, {channel2.name}, {channel3.name}, {channel4.name}')
# for delete catagory with channel
@bot.command()
async def delete_category_with_channels(ctx, category_name: str):
    category = discord.utils.get(ctx.guild.categories, name=category_name)
    if category is not None:
        for channel in category.channels:
            await channel.delete()
        await category.delete()
        await ctx.send(f'Deleted category {category_name} and all its channels')
    else:
        await ctx.send(f'{category_name} category not found.')

#This will register the user
@bot.command()
async def register(ctx, name: str, tag: str, email: str, discordid: str):
    # Create a new Excel file
    wb = Workbook()
    sheet = wb.active
    sheet.title = "Registration"
    # Add headers to the sheet
    sheet['A1'] = "Name"
    sheet['B1'] = "tag"
    sheet['C1'] = "Email"
    sheet['D1'] = "Discord ID"
    # Add the user's registration data to the sheet
    sheet.append([name, tag, email , discordid])
    wb.save("registrations.xlsx")
    await ctx.send("Registration successful.")
@bot.command()
async def give_role(message, role_name):
    guild = message.guild
    role = discord.utils.get(guild.roles, name=role_name)
    user = message.author
    await user.add_roles(role)
    await message.channel.send(f'{user.mention} has been given the {role.name} role.')

#it show the leaderboard of tournament..
# @bot.command()
# async def leaderboard(ctx):
#     top_users = sorted(message_count.items(), key=lambda x: x[1], reverse=True)[:10]
#     leaderboard_message = ""
#     for i, user in enumerate(top_users):
#         leaderboard_message += f"{i+1}. {user[0]} - {user[1]} messages\n"
#     await ctx.send(leaderboard_message)


#Run the bot
bot.run(TOKEN)
