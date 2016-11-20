from discord.ext import commands


def is_bot_owner():
    return commands.check(lambda ctx: ctx.message.author.id == '136856172203474944')


def is_server():
    return commands.check(lambda ctx: not ctx.message.channel.is_private)
