import aiohttp
import asyncio
import json

TOKEN = ''  # Replace with your bot's token
GUILD_ID = '1235116653432274954'  # Replace with your guild ID

async def create_channel(session, channel_name):
    url = f'https://discord.com/api/v10/guilds/{GUILD_ID}/channels'
    headers = {
        'Authorization': f'Bot {TOKEN}',
        'Content-Type': 'application/json'
    }
    data = {
        'name': channel_name,
        'type': 0  # 0 is for a text channel, 2 is for a voice channel
    }
    async with session.post(url, headers=headers, json=data) as response:
        if response.status == 201:
            print(f'Channel {channel_name} created successfully.')
        else:
            print(f'Failed to create channel {channel_name}. Status code: {response.status}')

async def main():
    async with aiohttp.ClientSession() as session:
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

            # Create channels using the REST API
            channel_names = [f'channel-{i+1}' for i in range(10)]
            tasks = [create_channel(session, name) for name in channel_names]
            await asyncio.gather(*tasks)

asyncio.run(main())