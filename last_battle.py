from io import BytesIO
import os 
from dotenv import load_dotenv
load_dotenv()
import discord
from discord import (ApplicationContext, Bot, ButtonStyle,
    Color, File, Interaction, SeparatorSpacingSize, User)
from discord.ui import (ActionRow, Button, Container, DesignerView,
    MediaGallery, Section, Select, Separator, TextDisplay, Thumbnail, button)

users = {}
fusers = {}

class MyGame:
    def __init__(self):
        self.player1 = None
        self.player2 = None
        self.view1 = None
        self.view2 = None
    @classmethod
    async def create(self, user1, user2, pot1, pot2):
        global fusers
        self.player1 = user1
        self.player2 = user2
        self.view1 = pot1
        self.view2 = pot2
        fusers.pop(player1.id)
        fusers.pop(player2.id)

class MyView(DesignerView):
    def __init__(self, user: MyUser):
        global users, fusers
        self.user = user
        self.container = None
        super().__init__(timeout=30)
        text1 = TextDisplay("LAST BATTLE")
        text2 = TextDisplay("Survive by destroing the enemy")
        thumbnail = Thumbnail(bot.user.display_avatar.url)
        section = Section(text1, text2, accessory=thumbnail)
        section.add_text("-# Good luck")
        self.container = Container(section, color=Color.from_rgb(180, 180, 180))
        async def delete_callback(interaction: Interaction): await self.user.thread.delete()
        async def play_callback(interaction: Interaction):
            self.container.add_item(TextDisplay(f"There's {len(users)} players and {len(fusers)} are avaiable"))
            gamestart()
            await interaction.response.edit_message(view=self)
        delete_button = Button(label="Delete Thread", style=ButtonStyle.red, id=0)
        delete_button.callback = delete_callback
        play_button = Button(label="Start the game", style=ButtonStyle.green, id=0)
        play_button.callback = play_callback
        row = ActionRow()
        row.add_item(delete_button)
        row.add_item(play_button)
        self.container.add_item(row)
        self.add_item(self.container)

class MyUser:
    def __init__(self):
        self.id = None
        self.thread = None
        self.name = None
        self.view = None 
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
        self.view = MyView(self)
        await self.thread.send(view=self.view)
        await ctx.send(f"{self.thread.mention} thread for {self.name} created")
        return self

bot = Bot()

@bot.event
async def on_ready():
    global events
    print(f"{bot.user} is ready and online!")

@bot.slash_command(name="start", description="start the game (not ready yet)")
async def new_game(ctx: discord.ApplicationContext):
    await ctx.respond("creating the thread...",ephemeral=True)
    global users, fusers
    user=await MyUser.create(ctx)
    fusers[str(user.id)]=user
    users[str(user.id)]=user
    print(len(fusers))
    print(len(users))

async def gamestart():
    print("keep going, everything is alright")
    

bot.run(os.getenv('TOKEN'))