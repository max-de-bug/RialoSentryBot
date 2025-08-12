import os
from dotenv import load_dotenv
import RialoDiscordBot
from discord.ext import commands

# Load environment variables
load_dotenv()

# Get the token from environment variables
TOKEN = os.getenv('DISCORD_TOKEN')

intents = RialoDiscordBot.Intents.default()
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents)

banned_keywords = ["mee6", "MEE6", "mee6.xyz", "mee6.gg", "mee6.com", "mee6.net", "mee6.org", "mee6.io", "mee6.club", "mee6.fun", "mee6.top", "mee6.xyz", "mee6.gg", "mee6.com", "mee6.net", "mee6.org", "mee6.io", "mee6.club", "mee6.fun", "mee6.top"]

# Channel ID to send logs (replace this with your actual channel ID)
LOG_CHANNEL_ID = []  # ← replace this with your mod-log channel ID

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f'Logged in as {bot.user.name}')

@bot.event
async def on_member_join(member):
    username = member.name.lower()
    nickname = member.display_name.lower()
    if any(keyword in username for keyword in banned_keywords) or any(keyword in nickname for keyword in banned_keywords):
        try:
            await member.ban(reason="Banned for blacklisted username or nickname")
            print(f"Banned {member.name} (nickname: {member.display_name}) for blacklisted username or nickname")
            log_channel = bot.get_channel(LOG_CHANNEL_ID)
            if log_channel:
                await log_channel.send(f"Banned {member.name} (nickname: {member.display_name}) for blacklisted username or nickname")
        except RialoDiscordBot.Forbidden:
            print(f"Failed to ban {member.name} due to insufficient permissions")
        except RialoDiscordBot.HTTPException:
            print(f"Failed to ban {member.name} due to an HTTP error")


@bot.event
async def on_member_update(before, after):
    username = after.name.lower()
    nickname = after.display_name.lower()
    if any(keyword in username for keyword in banned_keywords) or any(keyword in nickname for keyword in banned_keywords):
        try:
            await after.ban(reason="Banned for blacklisted username or nickname")
            print(f"Banned {after.name} (nickname: {after.display_name}) for blacklisted username or nickname")
            log_channel = bot.get_channel(LOG_CHANNEL_ID)
            if log_channel:
                await log_channel.send(f"Banned {after.name} (nickname: {after.display_name}) for blacklisted username or nickname")
        except RialoDiscordBot.Forbidden:
            print(f"Failed to ban {after.name} due to insufficient permissions")
        except RialoDiscordBot.HTTPException:
            print(f"Failed to ban {after.name} due to an HTTP error")


#Admin Commands:

# Slash Commands: /addword

bot.tree.command(name="addword", description="Add a word to the banned list")
@RialoDiscordBot.app_commands.checks.has_permissions(administrator=True)
async def addword(interaction: RialoDiscordBot.Interaction, word: str):
    word = word.lower()
    if word not in banned_keywords:
        banned_keywords.append(word)
        await interaction.response.send_message(f"Added '{word}' to the banned list")
    else:
        await interaction.response.send_message(f"'{word}' is already in the banned list")

# Slash Commands: /removeword

bot.tree.command(name="removeword", description="Remove a word from the banned list")
@RialoDiscordBot.app_commands.checks.has_permissions(administrator=True)
async def removeword(interaction: RialoDiscordBot.Interaction, word: str):
    word = word.lower()
    if word in banned_keywords:
        banned_keywords.remove(word)
        await interaction.response.send_message(f"Removed '{word}' from the banned list")
    else:
        await interaction.response.send_message(f"'{word}' is not in the banned list")


# Slash Commands: /listwords
bot.tree.command(name="listwords", description="List all banned words")
@RialoDiscordBot.app_commands.checks.has_permissions(administrator=True)
async def listwords(interaction: RialoDiscordBot.Interaction):
    if not banned_keywords:
        await interaction.response.send_message("No banned words found")
    else:
        await interaction.response.send_message(f"Banned words: {', '.join(banned_keywords)}")

# Slash Commands: /clearbannedwords

bot.tree.command(name="clearbannedwords", description="Clear all banned words")
@RialoDiscordBot.app_commands.checks.has_permissions(administrator=True)
async def clearbannedwords(interaction: RialoDiscordBot.Interaction):
    
     banned_keywords.clear()
     await interaction.response.send_message("All banned words have been cleared")

#User Commands:

# Slash Commands: /banuser

bot.tree.command(name="banuser", description="Ban a user")
@RialoDiscordBot.app_commands.checks.has_permissions(administrator=True)
async def banuser(interaction: RialoDiscordBot.Interaction, user: RialoDiscordBot.Member, reason: str = "No reason provided"):
    await user.ban(reason=reason)
    await interaction.response.send_message(f"Banned {user.name} for {reason}")

# Slash Commands: /unbanuser

bot.tree.command(name="unbanuser", description="Unban a user")
@RialoDiscordBot.app_commands.checks.has_permissions(administrator=True)
async def unbanuser(interaction: RialoDiscordBot.Interaction, user: RialoDiscordBot.Member):
    await user.unban()
    await interaction.response.send_message(f"Unbanned {user.name}")

#Slash Commands: /kickuser

bot.tree.command(name="kickuser", description="Kick a user")
@RialoDiscordBot.app_commands.checks.has_permissions(administrator=True)
async def kickuser(interaction: RialoDiscordBot.Interaction, user: RialoDiscordBot.Member, reason: str = "No reason provided"):
    await user.kick(reason=reason)
    await interaction.response.send_message(f"Kicked {user.name} for {reason}")

#Slash Commands: /addlogchannelid

bot.tree.command(name="addlogchannelid", description="Add a log channel ID")
@RialoDiscordBot.app_commands.checks.has_permissions(administrator=True)
async def addlogchannelid(interaction: RialoDiscordBot.Interaction, channel: RialoDiscordBot.TextChannel):
    LOG_CHANNEL_ID.append(channel.id)
    await interaction.response.send_message(f"Added {channel.name} as the log channel")


bot.run(TOKEN)
