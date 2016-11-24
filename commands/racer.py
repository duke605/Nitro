from discord.ext import commands
from PIL import ImageDraw, ImageFont, Image
from utils.nitro_type import get_profile, get_car, get_car_name
from utils.arguments import Arguments
from utils.choices import user
from utils.checks import is_server
from db.models import User
from io import BytesIO
import discord
import gc


class Racer:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, description="Shows a racer's racer card.")
    @is_server()
    @commands.check(lambda ctx: discord.utils.get(ctx.message.channel.server.roles, name='Racers') in
                                ctx.message.author.roles)
    async def racer(self, ctx, *, msg=''):
        parser = Arguments(allow_abbrev=False, prog='racer')
        parser.add_argument('user', type=user(ctx.message.channel.server), default=ctx.message.author, nargs='?'
                            , help='The name of the user to look up Nitro racer card for. (As a mention)')

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

        with Image.open('assets/images/racer_template.png') as i:
            i.convert('RGBA')
            fnt_12 = ImageFont.truetype('assets/fonts/DroidSerif-Regular.ttf', 12)
            fnt_16 = ImageFont.truetype('assets/fonts/DroidSerif-Regular.ttf', 16)
            fnt_18 = ImageFont.truetype('assets/fonts/DroidSerif-Regular.ttf', 18)
            d = ImageDraw.Draw(i)

            # Preparing data
            is_gold = profile['membership'] == 'gold'
            top3 = len([b for b in profile['boards'] if b.get('rank', 0) <= 3 and b.get('rank', 0) != 0]) > 0
            money = '${:,}'.format(profile['money'])
            nitros = '{:,} Nitros'.format(profile['nitros'])
            car_name = get_car_name(profile['carID'])
            title = profile['title']
            name = ('' if not profile['tag'] else '[%s] ' % profile['tag'])\
                   + (profile['displayName'] or profile['username'])

            # Applying banner
            img = 'assets/images/banner_gold.png' if is_gold else 'assets/images/banner_silver.png'
            with Image.open(img) as b:
                i.paste(b, (1, 13), b)

            # Applying top 3
            if top3:
                with Image.open('assets/images/scoreboard_champion.png') as b:
                    i.paste(b, (31, 111), b)

            # Title stuff
            d.text((149 - fnt_18.getsize(name)[0] / 2, 66), name, fill='#333' if is_gold else '#2f93db', font=fnt_18)
            d.text((149 - fnt_12.getsize(title)[0] / 2, 41), profile['title'], fill='#333', font=fnt_12)
            d.text((338, 41), str(profile['level']), fill='#2f93db', font=fnt_18)

            if is_gold:
                d.text((338, 73), 'Nitro Type Gold Member', fill='#fed034', font=fnt_16)

            # Stats stuff
            d.text((31, 173), car_name, fill='#2f93db', font=fnt_16)
            d.text((31, 221), money, fill='#44b938', font=fnt_16)
            d.text((31, 269), nitros, fill='#2f93db', font=fnt_16)

            # Drawing car
            car = await get_car(profile['carID'], profile['carHueAngle'])
            with Image.open(car) as c:
                with c.convert('RGBA') as c1:
                    i.paste(c1, (599 - c.size[0], 280 - c.size[1]), c1)

            car.close()

            del fnt_12, fnt_16, fnt_18, d, car
            with BytesIO() as b:
                i.save(b, 'PNG')
                b.seek(0)
                await self.bot.send_file(ctx.message.channel, b, filename='racer.png'
                                         , content='<https://www.nitrotype.com/racer/%s>' % profile['username'])

        gc.collect()


def setup(bot):
    bot.add_cog(Racer(bot))
