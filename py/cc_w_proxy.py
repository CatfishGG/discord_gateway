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
GUILD_ID = ''  # Replace with your guild ID
PROXY_URL = 'socks5://yourproxy' # Replace with your Proxy

async def create_channel(session, guild_id, channel_name):
    url = f'https://discord.com/api/v10/guilds/{guild_id}/channels'
    headers = {
        'Authorization': f'Bot {TOKEN}',
        'Content-Type': 'application/json'
    }
    data = {
        'name': channel_name,
        'type': 0  # Text channel
    }
    async with session.post(url, headers=headers, json=data) as response:
        if response.status == 201:
            print(f'Channel {channel_name} created successfully.')
        else:
            print(f'Failed to create channel {channel_name}. Status code: {response.status}')

async def create_channels(number_of_channels):
    connector = ProxyConnector.from_url(PROXY_URL)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [create_channel(session, GUILD_ID, f'channel-{i+1}') for i in range(number_of_channels)]
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

    number_of_channels = int(input('Enter the number of channels to create: '))
    await create_channels(number_of_channels)

asyncio.run(main())
