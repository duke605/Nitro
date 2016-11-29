from datetime import datetime, timedelta
from discord.ext import commands
from utils import checks, utils
from db.models import User
import asyncio
import discord


class Tasks:

    def __init__(self, bot):
        self.bot = bot
        self.kick_unregistered_users_task = bot.loop.create_task(self.kick_unregistered_users())
        self.ensure_registered_users_task = bot.loop.create_task(self.ensure_registered_users())

    def get_server(self):
        """
        Gets the Nitro Type server
        """

        return self.bot.get_server('223233024127533056')

    @utils.ignore_exception()
    async def kick_unregistered_users(self):
        """
        Kicks unregistered users that have been on the server for more than a day
        """

        await self.bot.wait_until_ready()
        server = self.get_server()
        mod_log = server.get_channel('249835423415664640')

        while not self.bot.is_closed:

            # Finding users that have not registered for 1 or more days
            time = datetime.utcnow() - timedelta(hours=1)
            unregistered_users = [u for u in server.members if 'Racers' not in [r.name for r in u.roles] and u.joined_at < time
                                  and not u.bot]

            # Kicking unregistered users
            for u in unregistered_users:
                await self.bot.send_message(u, 'You have been kicked from **%s** for not registering within the the appropriate time. '
                                               'Please join the server again and type `!reg <nitro_name>` in #welcome to register your '
                                               'account. <http://bit.ly/NitroTypeDiscord>' % server.name)
                await self.bot.send_message(mod_log, 'Kicked **%s** for not registering within the appropriate time.' % u.name)
                await self.bot.kick(u)

            del time, unregistered_users
            await asyncio.sleep(60*5)

    @utils.ignore_exception()
    async def ensure_registered_users(self):
        """
        Makes sure everyone with the racer role is actually registered
        """

        await self.bot.wait_until_ready()
        server = self.get_server()
        mod_log = server.get_channel('249835423415664640')
        racer_role = discord.utils.get(server.roles, name='Racers')

        while not self.bot.is_closed:

            # Finding users that have not registered for 1 or more days
            users = User.select().execute()
            user_ids = [u.id for u in users]
            false_registered = [u for u in server.members if racer_role in u.roles and u.id not in user_ids]

            # "Unregistering" users
            for u in false_registered:
                await self.bot.change_nickname(u, None) if u.display_name != u.name else None
                await self.bot.replace_roles(u, *[r for r in u.roles if 'Racers' not in r.name and r.name not in ('Gold', 'Veteran', 'Captains')])
                await self.bot.send_message(mod_log, '**%s** was falsely registered and has had their NT roles stripped.' % u.name)
                await self.bot.send_message(u, 'You were falsely registered in **%s** and have had your NT roles stripped. Type '
                                               '`!reg <nitro_name>` in #welcome to register your account.' % server.name)

            del user_ids, users, false_registered
            await asyncio.sleep(60*10)

    @commands.group(hidden=True, aliases=['task'])
    @checks.is_bot_owner()
    async def tasks(self):
        pass

    @commands.command(hidden=True, aliases=['refresh'])
    async def reload(self):

        # Canceling tasks
        self.kick_unregistered_users_task.cancel()
        self.kick_unregistered_users_task.cancel()

        # Reloading
        self.bot.unload_extension('commands.tasks')
        self.bot.load_extension('commands.tasks')


def setup(bot):
    bot.add_cog(Tasks(bot))
