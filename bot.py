import discord
from discord.ext import commands
from decouple import config

class MyBot(commands.Bot):
    def __init__(self, command_prefix):
        super().__init__(command_prefix)
        self.load_token()

    def load_token(self):
        # Load the token from a .env file
        self.token = config('DISCORD_BOT_TOKEN')

    async def on_ready(self):
        print(f'Started {self.user.name}')

    @commands.command(name='test')
    async def test(self, ctx):
        await ctx.send(f'test, {ctx.author.mention}!')

def run_bot():
    bot = UtilityBot(command_prefix='==')
    
    bot.run(bot.token)

if __name__ == "__main__":
    run_bot()
