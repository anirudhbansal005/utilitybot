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
        self.active_locks = {}  # Dictionary to store active lock tasks

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

        
    @commands.command(name="lock")
    async def lock_server(self, ctx, duration=None):
        server_id = ctx.guild.id  # Get the server ID from the context
        guild = self.get_guild(server_id)
        everyone_role = guild.default_role

        # Check permission before modifying role
        if not ctx.author.guild_permissions.manage_roles:
            await ctx.send("You don't have permission to use this command.")
            return
        # Validate duration if provided
        if duration:
            try:
                minutes = int(duration)
            except ValueError:
                await ctx.send(f"Invalid duration format. Please specify a number of minutes.")
                return

            if minutes <= 0:
                await ctx.send("Please specify a positive duration.")
                return
        try:
            await everyone_role.edit(send_messages=False)
            await ctx.send(f"Server locked down by {ctx.author.mention} for {duration} minutes" if duration else f"Server locked down by {ctx.author.mention}")

            # Start a task to unlock after duration (if provided)
            if duration:
                task = self.loop.create_task(self.unlock_after(server_id, minutes))
                self.active_locks[server_id] = task

        except discord.HTTPException as e:
            await ctx.send(f"Failed to lock server: {e}")

    @commands.command(name="unlock")
    async def unlock_server(self, ctx):
        server_id = ctx.guild.id  

        
        if not ctx.author.guild_permissions.manage_roles:
            await ctx.send("You don't have permission to use this command.")
            return

        
        if server_id in self.active_locks:
            task = self.active_locks[server_id]
            task.cancel()
            del self.active_locks[server_id]

            guild = self.get_guild(server_id)
            everyone_role = guild.default_role
            try:
                await everyone_role.edit(send_messages=True)
                await ctx.send(f"Unlock scheduled by {ctx.author.mention} has been cancelled and server is unlocked.")
            except discord.HTTPException as e:
                await ctx.send(f"Failed to unlock server (server_id: {server_id}): {e}")
        elif not everyone_role.permissions.send_messages:
            
            guild = self.get_guild(server_id)
            everyone_role = guild.default_role
            try:
                await everyone_role.edit(send_messages=True)
                await ctx.send(f"Server unlocked by {ctx.author.mention}.")
            except discord.HTTPException as e:
                await ctx.send(f"Failed to unlock server (server_id: {server_id}): {e}")
        else:
            await ctx.send("No scheduled unlock found and server is already unlocked.")

     async def unlock_after(self, server_id, minutes):
        await asyncio.sleep(minutes * 60)  # Convert minutes to seconds
        guild = self.get_guild(server_id)
        everyone_role = guild.default_role

        try:
            await everyone_role.edit(send_messages=True)
            await self.get_channel(YOUR_ANNOUNCEMENT_CHANNEL_ID).send(f"Server automatically unlocked after {minutes} minutes.") 
        except discord.HTTPException as e:
            print(f"Failed to unlock server (server_id: {server_id}): {e}")


def run_bot():
    intents = discord.Intents.all()
    bot = UtilityBot(command_prefix="//") 
    bot.run(bot.token)

if __name__ == "__main__":
    run_bot()
