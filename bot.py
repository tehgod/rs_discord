import os
import discord
from dotenv import load_dotenv
from discord import app_commands
import requests
import re
from database import database_connection



load_dotenv("./config/.env") #loads db credentials
guild_id = 516101938165710859
guild_name = "Poggies Mob"
intents = discord.Intents.all()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
db_conn = database_connection("Runescape")
bot_token = db_conn.grab_secret('BotSecretKey')

def validate_username(username):
    return (
        (re.match("^[A-Za-z0-9-_]*$", username)) and 
        (len(username)<=12) and 
        (";" not in username)
        )

@tree.command(name = "update-gainzbot-username", description = "Used to update username in gainzbot", guild=discord.Object(id=guild_id))
async def first_command(interaction, old_username: str, new_username: str):
    await interaction.response.send_message("Updating, please wait.")
    stored_usernames = db_conn.retrieve_usernames(interaction.user.id)
    if old_username.lower() not in stored_usernames:
        await interaction.followup.send("Your old username is incorrect.")
        return
    if requests.get(f"https://secure.runescape.com/m=hiscore_oldschool/index_lite.ws?player={new_username}").status_code!=200:
        await interaction.followup.send("Your new username is invalid.")
        return
    if not((new_username.lower()!=old_username.lower()) and validate_username(old_username) and validate_username(new_username)):
        await interaction.followup.send("Your new username is invalid.")
        return
    db_conn.update_usernames(old_username, new_username)
    await interaction.followup.send("Name has been updated")
    return
    

@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=guild_id))
    for guild in client.guilds:
        if guild.name == guild_name:
            break
    print(f'{client.user} is now connected to {guild.name}(id: {guild.id}).')
    text_channel_list = []
    for guild in client.guilds:
        if guild.name == "":
            for channel in guild.text_channels:
                text_channel_list.append(channel)

client.run(bot_token)