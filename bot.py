import asyncio
import os
import logging
import yaml
import ts3
import discord
from discord.ext import commands, tasks
import moment
from discord import app_commands

# Load configuration from YAML file
with open('config.yaml', 'r') as file:
    cfg = yaml.safe_load(file)

# Logging setup
log_filename = 'teamspeak_bot.log'
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s', datefmt='%Y-%m-%dT%H:%M:%S%z', handlers=[
    logging.FileHandler(log_filename),
    logging.StreamHandler()
])
log = logging.getLogger(__name__)


def log_with_timestamp(message):
    timestamp = moment.now().timezone(cfg['timezone']).strftime('%Y-%m-%dT%H:%M:%S%z')
    log.info(f'{message}')


# Configuration
singular_term = cfg['singular_term']
plural_term = cfg['plural_term']

DISCORD_TOKEN = cfg['discord']['token']
CHANNEL_ID = cfg['discord']['channel_id']

# Initialize Discord bot
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)
tree = bot.tree

last_presence_user_count = -1
last_channel_name_user_count = -1

# Global TeamSpeak client
ts_client = None
previous_active_users = set()
tasks_started = False


async def connect_to_teamspeak():
    #增加重连机制
    global ts_client
    while True:
        try:
            log_with_timestamp("Connecting to TeamSpeak server...")
            ts_client = ts3.query.TS3Connection(cfg['teamspeak']['server_ip'], cfg['teamspeak']['query_port'])
            ts_client.login(
                client_login_name=cfg['teamspeak']['username'],
                client_login_password=cfg['teamspeak']['password']
            )
            ts_client.use(sid=1)
            log_with_timestamp("Connected to TeamSpeak server.")
            break  # 连接成功，跳出循环
        except Exception as e:
            log.error(f"Failed to connect to TeamSpeak: {e}. Retrying in 10 seconds...")
            await asyncio.sleep(10)


async def get_active_users_from_teamspeak():
    # fix: 使用线程池执行同步操作，并处理连接失效
    loop = asyncio.get_running_loop()
    try:
        client_list = await loop.run_in_executor(None, ts_client.clientlist)
        active_users = [client for client in client_list if client['client_type'] == '0' and client['client_nickname'] != cfg['teamspeak']['bot_nickname']]
        active_user_nicknames = [user['client_nickname'] for user in active_users]
        active_user_ids = [user['clid'] for user in active_users]
        return active_users, active_user_nicknames, active_user_ids
    except Exception as e:
        log.error(f"Failed to retrieve TeamSpeak user count: {e}")
        await connect_to_teamspeak()
        return [], [], []

@tasks.loop(seconds=10)
async def monitor_user_changes():
    try:
        _, active_user_nicknames, _ = await get_active_users_from_teamspeak()
        global previous_active_users
        current_active_users = set(active_user_nicknames)

        # Find newly joined users
        new_users = current_active_users - previous_active_users
        for user in new_users:
            log_with_timestamp(f"User joined: {user}")

        # Find users who left
        left_users = previous_active_users - current_active_users
        for user in left_users:
            log_with_timestamp(f"User left: {user}")

        previous_active_users = current_active_users
    except Exception as e:
        log.error(f"Failed to monitor user changes: {e}")


@tasks.loop(minutes=5)
async def update_channel_name_periodically():
    try:
        active_users, _, _ = await get_active_users_from_teamspeak()
        user_count = len(active_users)
        global last_channel_name_user_count

        if user_count == last_channel_name_user_count:
            return

        channel = bot.get_channel(int(CHANNEL_ID))
        if channel:
            new_name = 'nobody-on-ts' if user_count == 0 else f'✅{user_count}-on-ts'
            await channel.edit(name=new_name)
            log_with_timestamp(f"Updated channel name to '{new_name}'.")
            last_channel_name_user_count = user_count
    except Exception as e:
        log.error(f"Failed to fetch or update channel name: {e}")


@tasks.loop(seconds=10)
async def update_presence_periodically():
    try:
        active_users, _, _ = await get_active_users_from_teamspeak()
        user_count = len(active_users)
        global last_presence_user_count

        if user_count == last_presence_user_count:
            return

        status = '0' if user_count == 0 else f'✅{user_count}'
        status_message = f"{status} {plural_term} on TeamSpeak"
        await bot.change_presence(activity=discord.CustomActivity(name=status_message))
        log_with_timestamp(f"Updated presence with {user_count} {plural_term}.")
        last_presence_user_count = user_count
    except Exception as e:
        log.error(f"Failed to update presence: {e}")


@bot.event
async def on_ready():
    global tasks_started
    log_with_timestamp(f"Logged in as {bot.user}! Starting periodic updates...")
    if not tasks_started:
        update_channel_name_periodically.start()
        update_presence_periodically.start()
        monitor_user_changes.start()
        tasks_started = True
        log_with_timestamp("Periodic tasks started.")
    await tree.sync()
    log_with_timestamp("Slash commands synced.")


@tree.command(name='online', description='List current online TeamSpeak users')
async def online(interaction: discord.Interaction):
    try:
        active_users, active_user_nicknames, _ = await get_active_users_from_teamspeak()
        if active_user_nicknames:
            reply_message = f"Currently online players: {', '.join(active_user_nicknames)}"
        else:
            reply_message = "No players are currently online."
        await interaction.response.send_message(reply_message)
    except Exception as e:
        await interaction.response.send_message("Unable to retrieve the list of online players.", ephemeral=True)
        log.error(f"Error retrieving online players for {interaction.user}: {e}")


@tree.command(name='online_ids', description='List current online TeamSpeak user IDs')
async def online_ids(interaction: discord.Interaction):
    try:
        active_users, active_user_nicknames, active_user_ids = await get_active_users_from_teamspeak()
        if active_user_ids:
            reply_message = f"Currently online players: {', '.join(active_user_nicknames)} (ID: {', '.join(active_user_ids)})"
        else:
            reply_message = "No players are currently online."
        await interaction.response.send_message(reply_message)
    except Exception as e:
        await interaction.response.send_message("Unable to retrieve the list of online player IDs.", ephemeral=True)
        log.error(f"Error retrieving online player IDs for {interaction.user}: {e}")


async def main():
    await connect_to_teamspeak()
    await bot.start(DISCORD_TOKEN)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log_with_timestamp("Bot stopped by user.")
        if ts_client:
            ts_client.quit()
        exit(0)
    except Exception as e:
        log.error(f"Unexpected error: {e}")
        if ts_client:
            ts_client.quit()
        exit(1)
