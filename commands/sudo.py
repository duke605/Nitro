from utils.arguments import Arguments
from discord.ext import commands
from utils import choices
from utils.checks import is_server
from utils.nitro_type import get_profile
from db.models import User
import gc


class Sudo:

    def __init__(self, bot):
        self.bot = bot

    @commands.group(aliases=['s'])
    @is_server()
    @commands.check(lambda ctx: '230762590060544002' in [r.id for r in ctx.message.author.roles])
    async def sudo(self):
        pass

    @sudo.command(pass_context=True, aliases=['reg'], description="Links a Discord user's account with Nitro Type.")
    async def register(self, ctx, *, msg):
        parser = Arguments(allow_abbrev=False, prog='sudo register')
        parser.add_argument('user', type=choices.user(ctx.message.channel.server))
        parser.add_argument('username', nargs='+')

        await self.bot.send_typing(ctx.message.channel)

        args = await parser.do_parse(self.bot, msg)
        if not args:
            return

        # Joining username
        args.username = ' '.join(args.username)

        # Checking if username is registered already
        if User.select().where(User.nitro_name % args.username).first():
            await self.bot.say('**%s** is already registered to another user.' % args.username)
            return

        # Getting profile for user
        profile = await get_profile(args.username)

        # Checking if username has profile
        if not profile:
            await self.bot.say('No profile found with the name **%s**.' % args.username)

        await self.bot.cogs['Register'].update_discord_user(args.user, self.bot, profile
                                                            , ctx.message.channel.server.roles)
        await self.bot.say('Successfully registered %s racer **%s**.' % (args.user.mention, profile['username']))

    @sudo.command(pass_context=True, aliases=['unreg'], description="Unlinks a Discord user's account from Nitro Type.")
    async def unregister(self, ctx, *, msg):
        parser = Arguments(allow_abbrev=False, prog='sudo register')
        parser.add_argument('user', type=choices.user(ctx.message.channel.server))

        await self.bot.send_typing(ctx.message.channel)

        args = await parser.do_parse(self.bot, msg)
        if not args:
            return

        # Checking if the user is in the DB
        u = User.select().where(User.id == args.user.id).first()
        if not u:
            await self.bot.say('**%s**\'s Discord account is not linked to Nitro Type.' % args.user.display_name)
            return

        await self.bot.cogs['Unregister'].update_discord_user(self.bot, args.user, u)
        await self.bot.say('**%s**\'s Nitro Type account has been unregistered.' % args.user.display_name)

    @sudo.command(pass_context=True, name='gc', description='Runs the Garbage Collector and frees up some memory.')
    async def _gc(self, ctx):
        await self.bot.send_typing(ctx.message.channel)
        await self.bot.say('Done... Cleaned {:,}B'.format(gc.collect()))

    @sudo.command(pass_context=True, aliases=['clear'], description='Clears messages from this bot and command calls.')
    async def clean(self, ctx):
        await self.bot.send_typing(ctx.message.channel)
        deleted = await self.bot.purge_from(ctx.message.channel
                        , check=lambda m: m.author.id == ctx.message.channel.server.me.id or m.content.startswith('!'))
        await self.bot.say('Deleted **{:,}** message{}.'.format(len(deleted), 's' if len(deleted) != 1 else '')
                           , delete_after=5)

    @sudo.command(description="Updates Discord user's accounts with their most recent Nitro Type information.")
    async def update(self):
        await self.bot.say("Updating users...")
        await self.bot.update_racers(User.select().execute())
        print('Updated profiles...')
        await self.bot.say('Completed updating users.')

    @sudo.command(pass_context=True, aliases=['purge'],
                  description='Deletes specific message from the channel this command is used in.')
    async def prune(self, ctx, *, msg=''):
        parser = Arguments(allow_abbrev=False, prog='sudo prune')
        parser.add_argument('-b', '--bot', action='store_true', default=False, help='Deletes messages from bots.')
        parser.add_argument('-e', '--embeds', action='store_true', default=False, help='Deletes messages with embeds.')
        parser.add_argument('-c', '--contains', nargs='?', default=None, help='Deletes messages containing a phrase.')
        parser.add_argument('-u', '--user', nargs='?', default=None, type=choices.user(ctx.message.channel.server),
                            help='Deletes messages from a user.')
        parser.add_argument('-l', '--limit', type=choices.between(1, 1000, True), default=100,
                            help='The number of messages to look through to see what messages can be purged.')

        await self.bot.send_typing(ctx.message.channel)
        args = await parser.do_parse(self.bot, msg)
        if not args:
            return

        _all = not args.bot and not args.embeds and args.contains is None and args.user is None
        deleted_messages = await self.bot.purge_from(ctx.message.channel, limit=args.limit,
                                                     check=lambda m: _all
                                                     or (args.bot and m.author.bot)
                                                     or (m.id == ctx.message.id)
                                                     or (args.embeds and (m.embeds or m.attachments))
                                                     or (args.user and m.author.id == args.user.id)
                                                     or (args.contains and args.contains.lower() in m.content.lower()))
        await self.bot.say('Deleted **{:,}** messages.'.format(len(deleted_messages)), delete_after=5)


def setup(bot):
    bot.add_cog(Sudo(bot))
