import discord
from discord.ext import commands,tasks
import os
import decouple 
from datetime import datetime, timedelta
import motor.motor_asyncio

class UtilityBot(commands.Bot):
    def __init__(self, command_prefix="/"): 
        super().__init__(command_prefix=command_prefix, intents=discord.Intents.all())
        self.load_token()
        self.setup_mongo()
        

    def load_token(self):
        
        self.token = decouple.config('TOKEN')  

    def setup_mongo(self):
        mongo_connection_string = decouple.config('CONNECTION_URI')
        database_name = decouple.config('DB_NAME')
        self.mongo_client = motor.motor_asyncio.AsyncIOMotorClient(mongo_connection_string)
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

    @commands.command(name='locktime')
    async def locktime(self, ctx, start_hour: int, duration_hours: int):
        """Set the start hour and duration for server lockdown.\nExample: //locktime 00h 8h"""
        collection = self.db['lockdown_times']
        document = {'start_hour': start_hour, 'duration_hours': duration_hours}
        await collection.replace_one({}, document, upsert=True)
        await ctx.send(f"Lockdown time set. Server will be locked down daily starting at {start_hour}:00 for {duration_hours} hours.")
        
    @tasks.loop(hours=24)  # Runs every 24 hours
    async def lockdown_task(self):
        server_id = t  
        guild = self.get_guild(server_id)
        everyone_role = guild.default_role
        collection = self.db['lockdown_times']
        document = await collection.find_one({})
        if document:
            start_hour = document.get('start_hour', 0)
            duration_hours = document.get('duration_hours', 8)
            current_hour = datetime.now().hour
            lockdown_start_time = datetime.now().replace(hour=start_hour, minute=0, second=0, microsecond=0)
            if current_hour == start_hour and datetime.now() >= lockdown_start_time:
                await everyone_role.edit(send_messages=False)
                print(f"Server locked down at {datetime.now()}")
                await asyncio.sleep(duration_hours * 3600)
                await everyone_role.edit(send_messages=True)
                print(f"Server unlocked at {datetime.now()}")

 
       

def run_bot():
    intents = discord.Intents.all()
    bot = UtilityBot(command_prefix="/") 
    bot.run(bot.token)
    bot.lockdown_task.start()

if __name__ == "__main__":
    run_bot()
