from discord.ext import commands
from db.models import User
from utils.nitro_type import get_profile
import discord


class Register:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['reg'], pass_context=True, description='Links your Discord account with Nitro Type.')
    @commands.check(lambda ctx: not User.select().where(User.id == ctx.message.author.id).first())
    async def register(self, ctx, *, msg):
        await self.bot.send_typing(ctx.message.channel)

        # Checking if user is already registered
        user = User.select().where(User.nitro_name % msg).first()
        if user:
            await self.bot.say('**%s** is already registered to another user.' % user.nitro_name, delete_after=5)
            return

        profile = await get_profile(msg)

        # Checking if the profile could be retrieved
        if not profile:
            await self.bot.say('No profile found with the name **%s**.' % msg, delete_after=5)
            return

        await Register.update_discord_user(ctx.message.author, self.bot, profile, ctx.message.channel.server.roles)
        await self.bot.say('Successfully registered as racer **%s**.' % profile['username'], delete_after=5)

    @staticmethod
    async def update_discord_user(user, bot, profile, roles, create=True):

        # Getting racer roles
        fast_role = discord.utils.get(roles, name='Fast-Racers')
        accurate_role = discord.utils.get(roles, name='Accurate-Racers')
        active_role = discord.utils.get(roles, name='Active-Racers')
        captain_role = discord.utils.get(roles, name='Captains')
        std_role = discord.utils.get(roles, name='Racers')

        # Getting non-racer roles
        sync_roles = [r for r in user.roles if r not in (fast_role, active_role, accurate_role, captain_role, std_role)]
        sync_roles.append(std_role)

        # Checking if the user is a fast typer
        if profile['avgSpeed'] >= 100:
            sync_roles.append(fast_role)

        board = [s for s in profile['racingStats'] if s['board'] == 'weekly']
        if board:

            # Giving user active racer
            if board[0]['played'] > 500:
                sync_roles.append(active_role)

            # Giving user accurate racer
            if 100 - (board[0]['errs'] / board[0]['typed'] * 100) > 97:
                sync_roles.append(accurate_role)

        # Checking if user is captain
        if profile['isCaptain']:
            sync_roles.append(captain_role)

        # Making the user's nickname
        nick = profile['displayName'] or profile['username']
        if profile['tag']:
            nick = '[%s] %s' % (profile['tag'], nick)

        # Applying roles to user
        if create:
            User.create(id=user.id, nitro_name=profile['username'])
        await bot.replace_roles(user, *sync_roles)

        try:

            # Only changing if it needs to be
            if user.display_name != nick:
                await bot.change_nickname(user, nick)
        except Exception:
            pass


def setup(bot):
    bot.add_cog(Register(bot))
