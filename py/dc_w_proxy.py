# Not sure if the code below is working because I haven't tested it out yet. (update this comment if you tested it before me)

import os
os.system("pip install aiohttp")
os.system("pip install aiohttp_socks")
os.system("pip install asyncio")
import aiohttp
import asyncio
import json
from aiohttp_socks import ProxyConnector

TOKEN = ''  # Replace with your bot's token
GUILD_ID = '1235116653432274954'  # Replace with your guild ID
PROXY_URL = 'socks5://yourproxy'

async def delete_channel(session, channel_id):
    url = f'https://discord.com/api/v10/channels/{channel_id}'
    headers = {
        'Authorization': f'Bot {TOKEN}',
        'Content-Type': 'application/json'
    }
    async with session.delete(url, headers=headers) as response:
        if response.status == 204:
            print(f'Channel {channel_id} deleted successfully.')
        else:
            print(f'Failed to delete channel {channel_id}. Status code: {response.status}')

async def fetch_and_delete_channels():
    connector = ProxyConnector.from_url(PROXY_URL)
    async with aiohttp.ClientSession(connector=connector) as session:
        # Fetch all channels in the guild
        url = f'https://discord.com/api/v10/guilds/{GUILD_ID}/channels'
        headers = {
            'Authorization': f'Bot {TOKEN}',
            'Content-Type': 'application/json'
        }
        async with session.get(url, headers=headers) as response:
            if response.status != 200:
                print(f'Failed to fetch channels. Status code: {response.status}')
                return
            channels = await response.json()

        # Delete all channels concurrently
        tasks = [delete_channel(session, channel['id']) for channel in channels]
        await asyncio.gather(*tasks)

async def main():
    connector = ProxyConnector.from_url(PROXY_URL)
    async with aiohttp.ClientSession(connector=connector) as session:
        async with session.ws_connect('wss://gateway.discord.gg/?v=10&encoding=json') as ws:
            # Receive the Hello message
            hello_message = await ws.receive_json()
            print('Received Hello:', hello_message)

            heartbeat_interval = hello_message['d']['heartbeat_interval'] / 1000

            # Identify payload
            identify_payload = {
                'op': 2,
                'd': {
                    'token': TOKEN,
                    'intents': 513,  # Example intents
                    'properties': {
                        '$os': 'linux',
                        '$browser': 'my_library',
                        '$device': 'my_library'
                    }
                }
            }
            await ws.send_json(identify_payload)

            async def send_heartbeat():
                while True:
                    await asyncio.sleep(heartbeat_interval)
                    await ws.send_json({'op': 1, 'd': None})

            asyncio.create_task(send_heartbeat())

            # Listen for Ready event to confirm identification
            while True:
                message = await ws.receive_json()
                print('Received Event:', message)

                if message['t'] == 'READY':
                    print('Bot is ready and connected.')
                    break

            await fetch_and_delete_channels()

asyncio.run(main())
