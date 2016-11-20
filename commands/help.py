from discord.ext import commands


class Help:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['?', 'man', 'manual', 'commands'], pass_context=True, description='Shows this command.')
    async def help(self, ctx):
        commands = (self.bot.commands[key] for key in self.bot.commands if key not in self.bot.commands[key].aliases)
        messages = []
        message = ''

        for command in commands:
            m = self.compose_command_doc(ctx, command)

            # Checking if message surpasses 200 characters
            if len(message) + len(m) >= 2000:
                messages.append(message)
                message = ''

            message += m

        # Adding last message to the help
        messages.append(message)

        for m in messages:
            await self.bot.send_message(ctx.message.author, '```yml\n%s```' % m)

    def compose_command_doc(self, ctx, command, level=1):

        # Checking if command is hidden from help
        if command.hidden:
            return ''

        # Checking if user can run command
        for check in command.checks:
            if not check(ctx):
                return ''

        # Adding command details
        m = '\n\n%s%s:' % ('\t' * (level - 1), command.name)
        m += '\n%saliases: %s' % ('\t' * level, ', '.join(command.aliases))
        m += '\n%sdescription: "%s"' % ('\t' * level, command.description)

        # Adding sub-commands
        if hasattr(command, 'commands'):
            itr = (command.commands[key] for key in command.commands if key not in command.commands[key].aliases)
            for c in itr:
                m += self.compose_command_doc(ctx, c, level + 1)

        return m


def setup(bot):
    bot.add_cog(Help(bot))
