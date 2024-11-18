# TeamSpeak Discord Bot

A Discord bot that monitors a TeamSpeak server, updates Discord channel names and bot presence based on TeamSpeak user activity, and provides slash commands to list online TeamSpeak users.

## Features

- **Real-time Monitoring**: Keeps track of users joining and leaving the TeamSpeak server.
- **Discord Integration**: Updates a specified Discord channel's name and the bot's presence to reflect the number of active TeamSpeak users.
- **Slash Commands**:
  - `/online`: Lists current online TeamSpeak users.
  - `/online_ids`: Lists current online TeamSpeak users along with their IDs.

## Table of Contents

- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Dependencies](#dependencies)
- [Contributing](#contributing)
- [License](#license)

## Installation

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/yourusername/teamspeak-discord-bot.git
   cd teamspeak-discord-bot
   ```

2. **Create a Virtual Environment** (optional but recommended):

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use venv\Scripts\activate
   ```

3. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

## Configuration

Create a `config.yaml` file in the root directory with the following structure:

```yaml
# Timezone for logging and timestamps. eg:"Asia/Shanghai"
timezone: 'Your/Timezone'

# Terms used in status messages
singular_term: 'player'
plural_term: 'players'

discord:
  token: 'YOUR_DISCORD_BOT_TOKEN'
  channel_id: 'YOUR_DISCORD_CHANNEL_ID'

teamspeak:
  server_ip: 'TEAMSPEAK_SERVER_IP'
  query_port: 10011  # Default query port
  username: 'SERVER_QUERY_USERNAME'
  password: 'SERVER_QUERY_PASSWORD'
  bot_nickname: 'BotNickname'  # Nickname to ignore in user lists
```

### Configuration Parameters

- **timezone**: Your local timezone (e.g., 'America/New_York').
- **singular_term**: Singular term for users (e.g., 'player').
- **plural_term**: Plural term for users (e.g., 'players').

#### Discord Configuration

- **token**: Your Discord bot token. You can get this from the [Discord Developer Portal](https://discord.com/developers/applications).
- **channel_id**: The ID of the Discord channel whose name you want to update.

#### TeamSpeak Configuration

- **server_ip**: The IP address or hostname of your TeamSpeak server.
- **query_port**: The ServerQuery port (default is 10011).
- **username**: ServerQuery login username.
- **password**: ServerQuery login password.
- **bot_nickname**: The nickname of the bot on TeamSpeak (to exclude it from user lists).

## Usage

1. **Run the Bot**:

   ```bash
   python bot.py
   ```

2. **Invite the Bot to Your Discord Server**:

   - Use the OAuth2 URL Generator in the [Discord Developer Portal](https://discord.com/developers/applications) to generate an invite link with the necessary permissions.

3. **Use Slash Commands**:

   - `/online`: Lists currently online TeamSpeak users.
   - `/online_ids`: Lists currently online TeamSpeak users along with their IDs.

## Dependencies

- Python 3.7 or higher
- [discord.py](https://pypi.org/project/discord.py/) (`pip install discord.py`)
- [ts3.py](https://pypi.org/project/ts3/) (`pip install ts3`)
- [PyYAML](https://pypi.org/project/PyYAML/) (`pip install PyYAML`)
- [moment](https://pypi.org/project/moment/) (`pip install moment`)

Install all dependencies using:

```bash
pip install -r requirements.txt
```

### Example `requirements.txt`

```text
asyncio
PyYAML
ts3
discord.py
moment
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements.

## License

This project is licensed under the [MIT License](LICENSE).