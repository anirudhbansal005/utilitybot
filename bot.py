import discord
from discord.ext import commands
from decouple import config

class MyBot(commands.Bot):
    def __init__(self, command_prefix):
        super().__init__(command_prefix)
        self.load_token()
        self.setup_mongo()

    def load_token(self):
        self.token = config('TOKEN')

    def setup_mongo(self):
        mongo_connection_string = config('CONNECTION_URI')
        database_name = config('DB_NAME')

        self.mongo_client = motor.motor_asyncio.AsyncIOMotorClient(mongo_connection_string)
        self.db = self.mongo_client[database_name]

    async def on_ready(self):
        print(f'Started {self.user.name}')
        
    async def on_message(self, message):
        if message.author == self.user:
            return
            
    @commands.command(name='test')
    async def test(self, ctx):
        await ctx.send(f'test, {ctx.author.mention}!')

def run_bot():
    bot = UtilityBot(command_prefix='==')
    
    bot.run(bot.token)

if __name__ == "__main__":
    run_bot()
