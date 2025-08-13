import os
import io
from dotenv import load_dotenv
import discord as RialoDiscordBot
from discord.ext import commands

# Load environment variables
load_dotenv()

# Get the token from environment variables
TOKEN = os.getenv('DISCORD_TOKEN')

# Check if token is available
if not TOKEN:
    print("Error: DISCORD_TOKEN environment variable is not set!")
    print("Please create a .env file in the project root with your Discord bot token:")
    print("DISCORD_TOKEN=your_bot_token_here")
    exit(1)

intents = RialoDiscordBot.Intents.default()
# Note: members and guilds intents are privileged and need to be enabled in Discord Developer Portal
# For now, we'll disable them to make the bot work immediately
intents.members = True  
intents.guilds = True   
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

banned_keywords = ["mee6", "MEE6", "mee6.xyz", "mee6.gg", "mee6.com", "mee6.net", "mee6.org", "mee6.io", "mee6.club", "mee6.fun", "mee6.top", "mee6.xyz", "mee6.gg", "mee6.com", "mee6.net", "mee6.org", "mee6.io", "mee6.club", "mee6.fun", "mee6.top"]

# Channel ID to send logs (legacy, single-channel). Prefer per-guild map below.
LOG_CHANNEL_ID = None  # Backward compatibility fallback

# Per-guild log channel mapping: { guild_id: channel_id }
GUILD_LOG_CHANNEL_IDS = {}


async def send_log(message: str, guild_id: int | None = None):
    """Send a log message to the configured log channel for a guild.

    If per-guild channel is not set, falls back to the legacy global LOG_CHANNEL_ID.
    """
    channel_id = None
    if guild_id is not None:
        channel_id = GUILD_LOG_CHANNEL_IDS.get(guild_id)
    if channel_id is None:
        channel_id = LOG_CHANNEL_ID
    if channel_id is None:
        # Nothing configured
        return
    channel = bot.get_channel(channel_id)
    if channel is None:
        try:
            channel = await bot.fetch_channel(channel_id)
        except Exception as e:
            print(f"send_log: failed to fetch channel {channel_id}: {e}")
            return
    try:
        await channel.send(message)
    except Exception as e:
        print(f"send_log: failed to send message to channel {channel_id}: {e}")

@bot.event
async def on_ready():
    # Sync commands globally (they'll still be permission-checked at runtime)
    await bot.tree.sync()
    print(f'Logged in as {bot.user.name}')
    # Optional: print configured log channels for visibility
    if LOG_CHANNEL_ID:
        print(f"Global log channel configured: {LOG_CHANNEL_ID}")
    if GUILD_LOG_CHANNEL_IDS:
        for gid, cid in GUILD_LOG_CHANNEL_IDS.items():
            print(f"Guild {gid} -> log channel {cid}")
    
    # Print guild information for debugging
    print(f"Bot is in {len(bot.guilds)} guilds:")
    for guild in bot.guilds:
        print(f"  - {guild.name} (ID: {guild.id})")
        # Check if bot has admin permissions
        bot_member = guild.get_member(bot.user.id)
        if bot_member:
            has_admin = bot_member.guild_permissions.administrator
            print(f"    Bot has admin permissions: {has_admin}")

@bot.event
async def on_member_join(member):
    # This event requires the "Server Members Intent" to be enabled in Discord Developer Portal
    # If you get errors, enable the intent or comment out this event handler
    try:
        username = member.name.lower()
        nickname = member.display_name.lower()
        if any(keyword in username for keyword in banned_keywords) or any(keyword in nickname for keyword in banned_keywords):
            try:
                await member.ban(reason="Banned for blacklisted username or nickname")
                print(f"Banned {member.name} (nickname: {member.display_name}) for blacklisted username or nickname")
                await send_log(
                    f"Auto-ban on join: {member.mention} ({member.id}) for blacklisted username or nickname. Username: '{member.name}', Nickname: '{member.display_name}'.",
                    guild_id=member.guild.id,
                )
            except RialoDiscordBot.Forbidden:
                print(f"Failed to ban {member.name} due to insufficient permissions")
            except RialoDiscordBot.HTTPException:
                print(f"Failed to ban {member.name} due to an HTTP error")
    except Exception as e:
        print(f"Error in on_member_join: {e}")
        print("Note: This event requires 'Server Members Intent' to be enabled in Discord Developer Portal")


@bot.event
async def on_member_update(before, after):
    # This event requires the "Server Members Intent" to be enabled in Discord Developer Portal
    # If you get errors, enable the intent or comment out this event handler
    try:
        username = after.name.lower()
        nickname = after.display_name.lower()
        if any(keyword in username for keyword in banned_keywords) or any(keyword in nickname for keyword in banned_keywords):
            try:
                await after.ban(reason="Banned for blacklisted username or nickname")
                print(f"Banned {after.name} (nickname: {after.display_name}) for blacklisted username or nickname")
                await send_log(
                    f"Auto-ban on name change: {after.mention} ({after.id}) for blacklisted username or nickname. Username: '{after.name}', Nickname: '{after.display_name}'.",
                    guild_id=after.guild.id,
                )
            except RialoDiscordBot.Forbidden:
                print(f"Failed to ban {after.name} due to insufficient permissions")
            except RialoDiscordBot.HTTPException:
                print(f"Failed to ban {after.name} due to an HTTP error")
    except Exception as e:
        print(f"Error in on_member_update: {e}")
        print("Note: This event requires 'Server Members Intent' to be enabled in Discord Developer Portal")


#Admin Commands:

# Slash Commands: /addword

@bot.tree.command(name="addword", description="Add a word to the banned list")
@RialoDiscordBot.app_commands.checks.has_permissions(administrator=True)
async def addword(interaction: RialoDiscordBot.Interaction, word: str):
    word = word.lower()
    if word not in banned_keywords:
        banned_keywords.append(word)
        await interaction.response.send_message(f"Added '{word}' to the banned list", ephemeral=True)
        try:
            if interaction.guild:
                await send_log(f"Banned word added by {interaction.user.mention}: '{word}'", guild_id=interaction.guild.id)
        except Exception:
            pass
    else:
        await interaction.response.send_message(f"'{word}' is already in the banned list", ephemeral=True)

# Slash Commands: /removeword

@bot.tree.command(name="removeword", description="Remove a word from the banned list")
@RialoDiscordBot.app_commands.checks.has_permissions(administrator=True)
async def removeword(interaction: RialoDiscordBot.Interaction, word: str):
    word = word.lower()
    if word in banned_keywords:
        banned_keywords.remove(word)
        await interaction.response.send_message(f"Removed '{word}' from the banned list")
        try:
            if interaction.guild:
                await send_log(f"Banned word removed by {interaction.user.mention}: '{word}'", guild_id=interaction.guild.id)
        except Exception:
            pass
    else:
        await interaction.response.send_message(f"'{word}' is not in the banned list", ephemeral=True)


# Slash Commands: /listwords
@bot.tree.command(name="listwords", description="List all banned words")
@RialoDiscordBot.app_commands.checks.has_permissions(administrator=True)
async def listwords(interaction: RialoDiscordBot.Interaction):
    if not banned_keywords:
        await interaction.response.send_message("No banned words found", ephemeral=True)
    else:
        await interaction.response.send_message(f"Banned words: {', '.join(banned_keywords)}", ephemeral=True)


#Slash Commands: /clearbannedword

@bot.tree.command(name="clearbannedword", description="Remove a specific word from the banned list")
@RialoDiscordBot.app_commands.checks.has_permissions(administrator=True)
async def clearbannedword(interaction: RialoDiscordBot.Interaction, word: str):
    word = word.lower()
    if word in banned_keywords:
        banned_keywords.remove(word)
        await interaction.response.send_message(f"Removed '{word}' from the banned list", ephemeral=True)
        try:
            if interaction.guild:
                await send_log(f"Banned word removed by {interaction.user.mention}: '{word}'", guild_id=interaction.guild.id)
        except Exception:
            pass
    else:
        await interaction.response.send_message(f"'{word}' is not in the banned list", ephemeral=True)


# Slash Commands: /clearbannedwords

@bot.tree.command(name="clearbannedwords", description="Clear all banned words")
@RialoDiscordBot.app_commands.checks.has_permissions(administrator=True)
async def clearbannedwords(interaction: RialoDiscordBot.Interaction):
    
     banned_keywords.clear()
     await interaction.response.send_message("All banned words have been cleared", ephemeral=True)
     try:
         if interaction.guild:
             await send_log(f"Banned words list cleared by {interaction.user.mention}", guild_id=interaction.guild.id)
     except Exception:
         pass




#User Commands:

#SLash Commands: /Listbanusers

@bot.tree.command(name="listbanusers", description="List all banned users in this server")
@RialoDiscordBot.app_commands.checks.has_permissions(administrator=True)
async def listbanusers(interaction: RialoDiscordBot.Interaction):
    if interaction.guild is None:
        await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
        return
    try:
        await interaction.response.defer(ephemeral=True)
        bans = []
        async for ban_entry in interaction.guild.bans(limit=None):
            bans.append(ban_entry)
        if not bans:
            await interaction.followup.send("No banned users in this server.", ephemeral=True)
            return
        lines = []
        for entry in bans:
            user = entry.user
            reason = entry.reason or "No reason provided"
            lines.append(f"{user} ({user.id}) - {reason}")
        content = "\n".join(lines)
        if len(content) <= 1900:
            await interaction.followup.send(content, ephemeral=True)
        else:
            buffer = io.StringIO(content)
            buffer.seek(0)
            await interaction.followup.send(file=RialoDiscordBot.File(buffer, filename="banned_users.txt"), ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"Failed to list banned users: {e}", ephemeral=True)
    # Also log the action (non-ephemeral log)
    try:
        await send_log(f"Ban list requested by {interaction.user.mention}", guild_id=interaction.guild.id)
    except Exception:
        pass

# Slash Commands: /banuser

@bot.tree.command(name="banuser", description="Ban a user")
@RialoDiscordBot.app_commands.checks.has_permissions(administrator=True)
async def banuser(interaction: RialoDiscordBot.Interaction, user: RialoDiscordBot.Member, reason: str = "No reason provided"):
    await user.ban(reason=reason)
    await interaction.response.send_message(f"Banned {user.name} for {reason}", ephemeral=True)
    try:
        if interaction.guild:
            await send_log(f"Manual ban: {user.mention} ({user.id}) by {interaction.user.mention}. Reason: {reason}", guild_id=interaction.guild.id)
    except Exception:
        pass

# Slash Commands: /unbanuser

@bot.tree.command(name="unbanuser", description="Unban a user by selecting them or providing their ID")
@RialoDiscordBot.app_commands.checks.has_permissions(administrator=True)
async def unbanuser(interaction: RialoDiscordBot.Interaction, user: RialoDiscordBot.User):
    if interaction.guild is None:
        await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
        return
    try:
        await interaction.guild.unban(user, reason=f"Unbanned by {interaction.user} via command")
        await interaction.response.send_message(f"Unbanned {user} ({user.id})", ephemeral=True)
        await send_log(
            f"Manual unban: {user.mention} ({user.id}) by {interaction.user.mention}",
            guild_id=interaction.guild.id,
        )
    except RialoDiscordBot.NotFound:
        await interaction.response.send_message("That user is not currently banned.", ephemeral=True)
    except RialoDiscordBot.Forbidden:
        await interaction.response.send_message("I don't have permission to unban this user.", ephemeral=True)
    except RialoDiscordBot.HTTPException as e:
        await interaction.response.send_message(f"Failed to unban user: {e}", ephemeral=True)


# Slash Commands: /unbanuserid

@bot.tree.command(name="unbanuserid", description="Unban a user by their numeric user ID")
@RialoDiscordBot.app_commands.checks.has_permissions(administrator=True)
async def unbanuserid(interaction: RialoDiscordBot.Interaction, user_id: str):
    if interaction.guild is None:
        await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
        return
    try:
        await interaction.response.defer(ephemeral=True)
        # Normalize the ID (strip whitespace and mention formatting)
        cleaned = user_id.strip().replace("<@", "").replace(">", "").replace("!", "")
        target_id = int(cleaned)
        # Unban using a lightweight object
        await interaction.guild.unban(RialoDiscordBot.Object(id=target_id), reason=f"Unbanned by {interaction.user} via ID command")
        mention = f"<@{target_id}>"
        await interaction.followup.send(f"Unbanned {mention} ({target_id})", ephemeral=True)
        await send_log(
            f"Manual unban (by ID): {mention} ({target_id}) by {interaction.user.mention}",
            guild_id=interaction.guild.id,
        )
    except ValueError:
        await interaction.followup.send("Please provide a valid numeric user ID.", ephemeral=True)
    except RialoDiscordBot.NotFound:
        await interaction.followup.send("That user is not currently banned.", ephemeral=True)
    except RialoDiscordBot.Forbidden:
        await interaction.followup.send("I don't have permission to unban this user.", ephemeral=True)
    except RialoDiscordBot.HTTPException as e:
        await interaction.followup.send(f"Failed to unban user: {e}", ephemeral=True)

#Slash Commands: /kickuser

@bot.tree.command(name="kickuser", description="Kick a user")
@RialoDiscordBot.app_commands.checks.has_permissions(administrator=True)
async def kickuser(interaction: RialoDiscordBot.Interaction, user: RialoDiscordBot.Member, reason: str = "No reason provided"):
    await user.kick(reason=reason)
    await interaction.response.send_message(f"Kicked {user.name} for {reason}", ephemeral=True)
    try:
        if interaction.guild:
            await send_log(f"Manual kick: {user.mention} ({user.id}) by {interaction.user.mention}. Reason: {reason}", guild_id=interaction.guild.id)
    except Exception:
        pass

#Slash Commands: /addlogchannelid

@bot.tree.command(name="addlogchannelid", description="Add a log channel ID")
@RialoDiscordBot.app_commands.checks.has_permissions(administrator=True)
async def addlogchannelid(interaction: RialoDiscordBot.Interaction, channel: RialoDiscordBot.TextChannel):
    global LOG_CHANNEL_ID, GUILD_LOG_CHANNEL_IDS
    # Set both: per-guild mapping and legacy fallback
    if interaction.guild:
        GUILD_LOG_CHANNEL_IDS[interaction.guild.id] = channel.id
    LOG_CHANNEL_ID = channel.id
    await interaction.response.send_message(f"Added {channel.name} as the log channel for this server", ephemeral=True)
    try:
        await channel.send("This channel has been set as the log channel for moderation events.")
    except Exception:
        pass
    try:
        if interaction.guild:
            await send_log(f"Log channel set to {channel.mention} by {interaction.user.mention}", guild_id=interaction.guild.id)
    except Exception:
        pass


# Utility: test log command
@bot.tree.command(name="testlog", description="Send a test message to the configured log channel for this server")
@RialoDiscordBot.app_commands.checks.has_permissions(administrator=True)
async def testlog(interaction: RialoDiscordBot.Interaction):
    if interaction.guild is None:
        await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
        return
    await interaction.response.send_message("Attempting to send a test log...", ephemeral=True)
    await send_log("This is a test log message.", guild_id=interaction.guild.id)


bot.run(TOKEN)
