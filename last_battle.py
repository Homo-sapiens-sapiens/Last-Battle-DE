import discord
import os 
from dotenv import load_dotenv
load_dotenv() 
bot = discord.Bot()

users = {}

class emb:
    discord.Embed(title="LAST BATTLE", description="Survive", color=discord.Colour.light_grey())

class User:
    def __init__(self):
        self.id = None
        self.free = None
        self.thread = None
        self.name = None
        self.embed = None
          
    @classmethod
    async def create(cls, ctx: discord.ApplicationContext):
        global users
        self = cls()
        self.name = ctx.author.name
        self.id = ctx.author.id
        self.thread = await ctx.channel.create_thread(name=f"{ctx.author.name}'s game",
                                                      type=discord.ChannelType.private_thread, invitable=False)
        await self.thread.add_user(ctx.author)
        await self.thread.send(f"The new game thread for {self.name} was created")
        self.embed = discord.Embed(title="LAST BATTLE", description="Survive", color=discord.Colour.light_grey())
        await self.thread.send("good luck", embed=self.embed)
        await ctx.send(f"{self.thread.mention} thread for {self.name} created")
        return self

@bot.event
async def on_ready():
    global events
    print(f"{bot.user} is ready and online!")
    
@bot.slash_command(name="start", description="start the game (not ready yet)")
async def new_game(ctx: discord.ApplicationContext):
    await ctx.respond("creating the thread...",ephemeral=True)
    global users
    user=await User.create(ctx)
    users[str(user.id)]=user

bot.run(os.getenv('TOKEN'))