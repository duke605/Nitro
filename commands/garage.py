from discord.ext import commands
from utils.arguments import Arguments
from utils.choices import user
from db.models import User
from utils.nitro_type import get_car, get_profile
from math import ceil, floor
from PIL import Image
from io import BytesIO
from utils.checks import is_server
import discord
import gc
import numpy


class Garage:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, description="Shows a racer's garage.")
    @is_server()
    @commands.check(lambda ctx: discord.utils.get(ctx.message.channel.server.roles, name='Racers') in
                                ctx.message.author.roles)
    async def garage(self, ctx, *, msg=''):
        parser = Arguments(allow_abbrev=False, prog='garage')
        parser.add_argument('user', type=user(ctx.message.channel.server), nargs='?', default=ctx.message.author
                            , help='The name of the user to look up Nitro Type garage for. (As a mention)')

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

        cars = len([c for c in profile['garage'] if c])
        # Player has no cars
        if cars == 0:
            await self.bot.say('**%s** has no cars in their garage.' % args.user.display_name)
            return

        # Warning user this may take a while
        if cars > 15:
            await self.bot.say('**%s** has a lot of cars. Generating their garage may take a while.'
                               % args.user.display_name)

        width = 913 + 24
        height = 30 + (ceil(len(profile['garage']) / 30) * 291)
        with Image.new('RGBA', (width, height)) as img:

            # Pasting lots
            with Image.open('assets/images/parking_spots_all.png') as lots:
                for i in range(ceil(len(profile['garage']) / 30)):
                    img.paste(lots, (12, 15 + (291 * i)), lots)

            garage = numpy.reshape(profile['garage'], (ceil(len(profile['garage']) / 15), 15))
            for y, row in enumerate(garage):
                for x, id in enumerate(row):

                    # Skipping blanks
                    if not id:
                        continue

                        # Looking for garage car in cars
                    id = int(id)
                    car_details = [c for c in profile['cars'] if c['carID'] == id and c['status'] == 'owned']

                    if not car_details:
                        continue

                    car_details = car_details[0]
                    car = await get_car(id, car_details['hueAngle'], 'small')
                    with Image.open(car) as c:
                        width = c.size[1]
                        length = c.size[0]
                        with c.rotate(90 if y % 2 == 0 else -90, expand=True, resample=Image.NEAREST) as temp:
                            _x = 12 + ((x * 61) + (30 - floor(width / 2)))
                            _y = 20 + (48 - floor(length / 2)) + (y * 181 - (floor(y / 2) * 71))
                            img.paste(temp, (_x, _y))

                    car.close()

            with BytesIO() as b:
                img.save(b, 'PNG')
                b.seek(0)
                await self.bot.send_file(ctx.message.channel, b, filename='garage.png')


def setup(bot):
    bot.add_cog(Garage(bot))
