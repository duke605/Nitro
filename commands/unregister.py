from db.models import User
from discord.ext import commands


class Unregister:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, aliases=['unreg'], description='Unlinks your Discord account from Nitro Type.')
    @commands.check(lambda ctx: 'Racers' in [r.name for r in ctx.message.author.roles])
    async def unregister(self, ctx):
        await self.bot.send_typing(ctx.message.channel)
        user = User.select().where(User.id == ctx.message.author.id).first()
        await Unregister.update_discord_user(self.bot, ctx.message.author, user)
        await self.bot.say('Your Discord account has been unlinked from Nitro Type.')

    @staticmethod
    async def update_discord_user(bot, user, model):

        # Deleting record from DB
        model.delete_instance()

        # Removing roles
        roles = [r for r in user.roles
                 if r.name not in ('Fast-Racers', 'Accurate-Racers', 'Active-Racers', 'Captains', 'Racers')]
        await bot.replace_roles(user, *roles)
        await bot.change_nickname(user, None)


def setup(bot):
    bot.add_cog(Unregister(bot))
