# RialoSentry Moderation Bot

A Discord bot designed to automatically ban users with blacklisted keywords in their username or nickname, and provide a suite of moderation slash commands to manage banned words and user moderation actions easily.

---

## Features

- Automatic banning of users whose username or nickname contains any blacklisted keyword.
- Real-time detection on user join and nickname updates.
- Moderation slash commands for admins:
  - `/addword <word>` — Add a word to the banned keywords list.
  - `/removeword <word>` — Remove a word from the banned keywords list.
  - `/listwords` — List all currently banned keywords.
  - `/clearbannedwords` — Clear all banned keywords.
  - `/banuser <user> [reason]` — Ban a specified user with an optional reason.
  - `/unbanuser <user>` — Unban a specified user.
  - `/kickuser <user> [reason]` — Kick a specified user with an optional reason.
  - `/addlogchannelid <channel>` — Add a channel to send ban/kick logs.

---

## Technologies Used

- Python 3.8+
- `discord.py` library (Discord API wrapper)
- `python-dotenv` for environment variable management
- Discord Slash Commands via `discord.app_commands`

---

## Getting Started

### Prerequisites

- Python 3.8 or higher installed
- Discord bot application created with a bot token (see [Discord Developer Portal](https://discord.com/developers/applications))
- The bot added to your Discord server with these permissions enabled:
  - Read Messages / View Channels
  - Send Messages
  - Ban Members
  - Kick Members
  - Manage Messages (optional, if extending functionality)
  - Use Slash Commands (applications.commands scope)
- Enable Server Members Intent in Discord Developer Portal (Bot section → Privileged Gateway Intents)

### Installation

1. Clone the repository or download the source code:

```bash
git clone https://github.com/yourusername/discord-moderation-bot.git
cd discord-moderation-bot
```

2. Create and activate a virtual environment (recommended):

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root directory with the following content:

```bash
DISCORD_TOKEN=your_bot_token_here
```

5. Replace `LOG_CHANNEL_ID` in the code with your mod-log Discord channel ID, or use `/addlogchannelid` command after starting the bot.

### Running the Bot

Run the bot with:

```bash
python bot.py
```

Upon startup, the bot will sync slash commands with Discord and begin monitoring user joins and nickname updates.

---

## Usage

### Automatic Moderation

The bot bans any user whose username or nickname contains blacklisted keywords.

This is checked immediately on user join and anytime their nickname changes.

### Admin Slash Commands

- `/addword <word>`: Add new banned keyword.
- `/removeword <word>`: Remove banned keyword.
- `/listwords`: View banned keywords.
- `/clearbannedwords`: Clear all banned keywords.
- `/banuser <user> [reason]`: Ban a user manually.
- `/unbanuser <user>`: Unban a user.
- `/kickuser <user> [reason]`: Kick a user.
- `/addlogchannelid <channel>`: Add a channel for ban/kick logs.

---

## Configuration

### Banned Keywords

Predefined in the `banned_keywords` list inside the script. Can be modified live via slash commands.

### Log Channel

The bot sends ban/kick action logs to the channel ID(s) stored in `LOG_CHANNEL_ID`. Use `/addlogchannelid` to add more channels dynamically.

---

## Permissions and Intents

Make sure the bot has the following intents enabled both in the code and on Discord Developer Portal:

- Members intent enabled in code (`intents.members = True`)
- Server Members Intent enabled in Discord Developer Portal under Bot settings.

---

## Contributing

Contributions are welcome! Feel free to open issues or pull requests to improve the bot functionality.

---

## License

This project is licensed under the MIT License.

---

## Contact

For support or questions, open an issue or contact the maintainer: [@CryptoMax_07](https://x.com/CryptoMax_07)

---

## Examples

### Example .env file

```env
DISCORD_TOKEN=YOUR_DISCORD_BOT_TOKEN
```

### Example command to add log channel after running the bot

```bash
/addlogchannelid #mod-log
```
