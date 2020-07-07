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
roster=[]

def process_message(text):
    """ Takes a simple message and expands it into a full roster

    Example: '4*tank' will be replaced with 4 'Tank: ' lines
    """
    regex = r'^([0-9]+)[*](tank|dps|heal|bench)$'
    message = ''
    for line in text.splitlines():
        matches = re.search(regex, line, re.IGNORECASE)
        if matches:
            if len(matches.groups()) != 2:
                message += 'malformed input\n'
            else:
                amount = int(matches.group(1))
                role = matches.group(2)
                message += f'{role}: \n' * amount
                roster.extend([(role, '') for i in range(amount)])
        else:
            message += line+'\n'
    return message

roles = {'🧱':'Tank','🩹':'Heal','🔫':'Dps','🪑':'Bench'}

class MyClient(discord.Client):
    """ Extends the base class by adding handlers for event types.

    There's probably a nicer/more efficient way to do this, but this works for now
    """
    target_message = None

    # This may result in race conditions? Check how async/await work in Python
    def add_user(self, user, role_emoji):
        role = roles[role_emoji.emoji]
        print(f'Adding: {user} with role {role}')

        # First check the user doesn't already have a role
        # TODO: Handle the case when user can bring multiple roles

        for _, name in roster:
            if name == user.mention: return
        
        for idx, spot in enumerate(roster):
            print(role, spot[0])
            if spot[0] == role and spot[1]=='':
                roster[idx] = (spot[0], user.mention)
                return True
        return False

    def remove_user(self, user, reaction):
        # TODO: Implement some method to swap spots, if the primary spot is removed
        # Possibly automatically move people from the waiting list and notify them?
        for idx, spot in enumerate(roster):
            if spot[1] == user.mention:
                roster[idx] = (spot[0], '')
                return True
        return False

    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))
        channel = discord.utils.get(client.get_all_channels(), name=bot_channel)
        self.target_message = await channel.send(process_message(message))
        for emoji in roles.keys():
            await self.target_message.add_reaction(emoji)

    async def on_message(self, message):
        print('Message from {0.author}: {0.content}'.format(message))

    async def on_reaction_add(self, reaction, user):
        # Reacts only to a particular message - ideally the announcement
        # Refactor code duplication, if possible?
        if reaction.message.id == self.target_message.id and user != client.user:
            should_update = self.add_user(user, reaction)
            if should_update:
                await self.target_message.edit(content=f'{roster}')
            print(roster)

    async def on_reaction_remove(self, reaction, user):
        if reaction.message.id == self.target_message.id and user != client.user:
            should_update = self.remove_user(user, reaction)
            if should_update:
                await self.target_message.edit(content=f'{roster}')
            print(roster)
    
client = MyClient()
client.run(TOKEN)