# bot.py
import os
import re

import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
message = """
Hello, this is dog:

2*Tank
4*Dps
2*Heal

2*Bench
"""
bot_channel='aaa'

def process_message(text):
    """ Takes a simple message and expands it into a full roster

    Example: '4*tank' will be replaced with 4 'Tank: ' lines
    """
    regex = r'^([0-9]+)[*](Tank|dps|heal|bench)$'
    message = ''
    for line in text.splitlines():
        matches = re.search(regex, line, re.IGNORECASE)
        if matches:
            if len(matches.groups()) != 2:
                message += 'malformed input\n'
            else:
                message += f'{matches.group(2)}: \n' * int(matches.group(1))
        else:
            message += line+'\n'
    print(message)

roles = {'🧱':'Tank','🩹':'Heal','🔫':'Dps','🪑':'Bench'}

class MyClient(discord.Client):
    """ Extends the base class by adding handlers for event types.

    There's probably a nicer/more efficient way to do this, but this works for now
    """
    target_message = None

    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))
        channel = discord.utils.get(client.get_all_channels(), name=bot_channel)
        self.target_message = await channel.send('Hello!')

    async def on_message(self, message):
        print('Message from {0.author}: {0.content}'.format(message))

    async def on_reaction_add(self, reaction, user):
        # Reacts only to a particular message - ideally the announcement
        print(f'{reaction} by {user}')
        if reaction.message.id == self.target_message.id:
            await self.target_message.edit(content='This was a triumph')

process_message(message)
client = MyClient()
client.run(TOKEN)