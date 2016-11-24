from discord.ext import commands
from utils.nitro_type import get_profile
from datetime import datetime
from db.models import User
import secret
import asyncio
import inspect
import discord

bot = commands.Bot(command_prefix='!')
bot.remove_command('help')
bot.start_time = datetime.utcnow()


@bot.event
async def on_ready():
    bot.update_racers = _update_racers
    cogs = ['register', 'stats', 'sudo', 'about', 'racer', 'help', 'garage', 'unregister']

    for cog in cogs:
        bot.load_extension('commands.%s' % cog)


@bot.event
async def on_message(m):

    if m.channel.id == '223233024127533056' and m.author.id != '246467186506334209':
        await bot.delete_message(m)

    await bot.process_commands(m)


@bot.event
async def on_member_remove(m):
    user = User.select().where(User.id == m.id).first()

    # User was not registered
    if not user:
        return

    # Removing user from registered users
    user.delete_instance()
    await bot.send_message(discord.Object(id='249835423415664640'), '**%s** left the server and has been successfully '
                                                                    'unregistered.' % m.display_name)


@bot.event
async def on_command_error(ex, ctx):
    c = discord.Object(id='249835423415664640')
    e = discord.Embed()

    e.description = '[]()'
    e.title = type(ex).__name__
    e.url = 'http://leekspin.com/'
    e.set_author(name=ctx.message.author.display_name, icon_url=ctx.message.author.avatar_url)
    e.timestamp = datetime.now()

    e.add_field(name='Input', value=ctx.message.content, inline=False)
    e.add_field(name='Error', value=str(ex.original), inline=False)
    e.add_field(name='Channel', value=ctx.message.channel.mention, inline=False)

    # Adding information if HTTP error
    if type(ex.original).__name__ == 'HTTPException':
        e.add_field(name='Response', value=await ex.original.response.text())

    await bot.send_message(c, embed=e)


@bot.command(name='eval', hidden=True, pass_context=True)
@commands.check(lambda ctx: ctx.message.author.id == '136856172203474944')
async def _eval(ctx, *, code):

    """Evaluates code."""
    python = '```py\n' \
             '# Input\n' \
             '{}\n\n' \
             '# Output\n' \
             '{}' \
             '```'

    env = {
        'bot': bot,
        'ctx': ctx,
        'message': ctx.message,
        'server': ctx.message.server,
        'channel': ctx.message.channel,
        'author': ctx.message.author
    }

    env.update(globals())

    await bot.send_typing(ctx.message.channel)

    try:
        result = eval(code, env)
        if inspect.isawaitable(result):
            result = await result
    except Exception as e:
        await bot.say(python.format(code, type(e).__name__ + ': ' + str(e)))
        return

    await bot.say(python.format(code, result or 'N/A'))


async def update_racers():
    await bot.wait_until_ready()

    while not bot.is_closed:
        await asyncio.sleep(60*30)
        await _update_racers(User.select().execute())
        print('Updated profiles...')


async def _update_racers(users):

    # Updating users
    for user in users:
        server = bot.get_server('223233024127533056')
        duser = server.get_member(user.id)
        profile = await get_profile(user.nitro_name)

        # Checking if profile could be found
        if not profile or not duser:
            print("User's profile not found. Unregistering them. %s" % user.id)

            # Unregistering if the user no longer has a Nitro Type account
            if duser:
                await bot.cogs['Unregister'].update_discord_user(bot, duser, user)

            # Deleting model as user is no longer in server
            else:
                user.delete_instance()

            continue

        # Updating discord user
        print('Updating %s... ' % duser.id, end='')

        try:
            await bot.cogs['Register'].update_discord_user(duser, bot, profile, server.roles, False)
        except Exception as e:
            print(str(e))
            continue

        print('Done')

bot.loop.create_task(update_racers())
bot.run(secret.BOT_TOKEN)
