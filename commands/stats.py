from discord.ext import commands
from utils.arguments import Arguments
from utils.choices import user
from db.models import User
from utils.nitro_type import get_profile
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from datetime import datetime
from utils.checks import is_server
import discord
import gc


class Stats:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, description="Shows a racer's Nitro Type statistics.")
    @is_server()
    @commands.check(lambda ctx: discord.utils.get(ctx.message.channel.server.roles, name='Racers') in
                                ctx.message.author.roles)
    async def stats(self, ctx, *, msg=''):
        parser = Arguments(allow_abbrev=False, prog='stats')
        parser.add_argument('user', nargs='?', type=user(ctx.message.channel.server), default=ctx.message.author,
                            help='The name of the user to look up Nitro Type stats for. (As a mention)')
        await self.bot.send_typing(ctx.message.channel)
        args = await parser.do_parse(self.bot, msg)

        # Checking if parse was success
        if not args:
            return

        nitro_record = User.select().where(User.id == args.user.id).limit(1).first()

        # Checking if the is a user for the duser
        if not nitro_record:
            await self.bot.say('That user does not have their Discord account linked to Nitro Type.')
            return

        profile = await get_profile(nitro_record.nitro_name)

        # Checking if the profile was found
        if not profile:
            await self.bot.say('Could not retrieve **%s**\'s Nitro Type account.' % nitro_record.nitro_name)
            return

        with Image.open('assets/images/stats_template.png') as i:
            d = ImageDraw.Draw(i)
            fnt_bold = ImageFont.truetype('assets/fonts/DroidSerif-Bold.ttf', 22)
            fnt_reg = ImageFont.truetype('assets/fonts/DroidSerif-Regular.ttf', 16)

            # Racing record text
            d.text((35, 96), '{:,} WPM'.format(profile['avgSpeed']), '#2f93db', font=fnt_bold)
            d.text((194, 96), '{:,} WPM'.format(profile['highestSpeed']), '#2f93db', font=fnt_bold)

            # Profile info text
            d.text((396, 96), '${:,}'.format(profile['money'] + profile['moneySpent']), '#44b938', font=fnt_bold)
            d.text((578, 96), '${:,}'.format(profile['moneySpent']), '#44b938', font=fnt_bold)
            d.text((761, 96), '%s' % datetime.fromtimestamp(profile['createdStamp']).strftime('%b %d, %Y')
                   , '#2f93db', font=fnt_bold)

            d.text((87, 186), 'x{:,}'.format(profile['placed1']), '#2f93db', font=fnt_reg)
            d.text((193, 186), 'x{:,}'.format(profile['placed2']), '#2f93db', font=fnt_reg)
            d.text((299, 186), 'x{:,}'.format(profile['placed3']), '#2f93db', font=fnt_reg)

            fnt_reg.size = 10
            d.text((162, 262-4), '{:,} races'.format(profile['racesPlayed']), '#2f93db', font=fnt_reg)
            d.text((162, 296-4), '{:,} races'.format(profile['longestSession']), '#2f93db', font=fnt_reg)
            d.text((162, 330-4), '{:,} nitros'.format(profile['nitrosUsed']), '#2f93db', font=fnt_reg)

            # Race summary text
            fnt_reg.size = 15
            offset = [0, 3, -38, -57]
            for x in range(4):
                b = profile['boards'][x]
                played = b.get('played', 0)
                rank = b.get('rank', 0)
                wpm = int(round(b['typed'] / 5 / (float(b['secs']) / 60))) \
                    if b.get('secs', False) is not False else 0

                acc = round(100 - b['errs'] / b['typed'] * 100, 2) \
                    if b.get('secs', False) is not False else 0

                d.text((246 + (x * 199) + offset[x], 509), '{:,}'.format(played), '#2f93db', font=fnt_reg)
                d.text((246 + (x * 199) + offset[x], 557), '{:,} WPM'.format(wpm), '#2f93db', font=fnt_reg)
                d.text((246 + (x * 199) + offset[x], 605), '{}%'.format(acc), '#2f93db', font=fnt_reg)
                d.text((246 + (x * 199) + offset[x], 653), '{:,}'.format(rank), '#2f93db', font=fnt_reg)

            del d
            del fnt_bold
            del fnt_reg
            with BytesIO() as b:
                i.save(b, 'PNG')
                b.seek(0)
                await self.bot.send_file(ctx.message.channel, b, filename='stats.png')

        gc.collect()


def setup(bot):
    bot.add_cog(Stats(bot))
