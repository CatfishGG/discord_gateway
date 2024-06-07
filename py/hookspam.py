import aiohttp
import asyncio

TOKEN = ''
GUILD_ID = ''
MESSAGE_CONTENT = 'Certified loverboy, Certified Pedophile. @evertone @here'

async def fetch_channels(session, guild_id):
    url = f'https://discord.com/api/v10/guilds/{guild_id}/channels'
    headers = {
        'Authorization': f'Bot {TOKEN}',
        'Content-Type': 'application/json'
    }
    async with session.get(url, headers=headers) as response:
        if response.status == 200:
            return await response.json()
        else:
            print(f'Failed to fetch channels. Status code: {response.status}')
            return []

async def send_message(session, channel_id, content):
    url = f'https://discord.com/api/v10/channels/{channel_id}/messages'
    headers = {
        'Authorization': f'Bot {TOKEN}',
        'Content-Type': 'application/json'
    }
    data = {
        'content': content
    }
    async with session.post(url, headers=headers, json=data) as response:
        if response.status == 200 or response.status == 201:
            print(f'Message sent to channel {channel_id}')
        else:
            print(f'Failed to send message to channel {channel_id}. Status code: {response.status}')

async def main():
    async with aiohttp.ClientSession() as session:
        channels = await fetch_channels(session, GUILD_ID)
        if not channels:
            return
        
        tasks = []
        for channel in channels:
            if channel['type'] == 0:  # Ensure it's a text channel
                for _ in range(10):  # Send 10 messages
                    tasks.append(send_message(session, channel['id'], MESSAGE_CONTENT))
        
        await asyncio.gather(*tasks)

asyncio.run(main())