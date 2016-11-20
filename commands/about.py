import discord
import psutil
from discord.ext import commands
from datetime import datetime
from db.models import User


class About:

    def __init__(self, bot):
        self.bot = bot

    @property
    def version(self):
        return '0.1.0'

    @commands.command(aliases=['info'], pass_context=True, description='Shows information about this bot.')
    async def about(self, ctx):
        await self.bot.send_typing(ctx.message.channel)

        e = discord.Embed(title='Official Development Server Invite', url='https://discord.gg/q3UNHq8'
                          , description='[]()')
        owner = await self.bot.get_user_info('136856172203474944')

        # Preparing field data
        delta = datetime.utcnow() - self.bot.start_time
        mem_usage = round(psutil.Process().memory_full_info().uss / 1024**2, 2)
        mem_per = round(psutil.Process().memory_percent(memtype='uss'), 2)
        total_users = sum(not u.bot for u in self.bot.get_server('223233024127533056').members)
        reg_users = User.select().count()
        unreg_users = total_users - reg_users
        uptime = '{:,}h {}m {}s'.format(int(delta.total_seconds() / 3600), int(delta.total_seconds() % 3600 / 60),
                                        int(round(delta.total_seconds() % 3600 % 60)))

        # Fields
        e.add_field(name='Uptime', value=uptime)
        e.add_field(name='Version', value=self.version)
        e.add_field(name='Memory Usage', value='{:,} MiB\n{:,}%'.format(mem_usage, mem_per))
        e.add_field(name='Members', value='{:,} Total\n{:,} Registered\n{:,} Unregistered'
                    .format(total_users, reg_users, unreg_users))

        e.set_author(name=str(owner), icon_url=owner.avatar_url)
        e.set_footer(text='Made with discord.py', icon_url='http://i.imgur.com/5BFecvA.png')

        await self.bot.say(embed=e)


def setup(bot):
    bot.add_cog(About(bot))
