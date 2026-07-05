from io import BytesIO
import os 
from dotenv import load_dotenv
load_dotenv()
import discord
from discord import (ApplicationContext, Bot, ButtonStyle,
    Color, File, Interaction, SeparatorSpacingSize, User)
from discord.ui import (ActionRow, Button, Container, DesignerView,
    MediaGallery, Section, Select, Separator, TextDisplay, Thumbnail, button)

fusers = {}

class MyGame:
    def __init__(self, player1, player2):
        self.user1 = None
        self.user2 = None
        self.view1 = None
        self.view2 = None
    async def create(self, player1, player2):
        self.user1 = player1
        self.user2 = player2
        self.view1 = self.user1.view
        self.view2 = self.user2.view
        self.view1.game = self
        self.view2.game = self
        self.user1.game = self
        self.user2.game = self
        fusers.pop(self.user1.id, None)
        fusers.pop(self.user2.id, None)
        await self.view1.show_game()
        await self.view2.show_game()

class MyView(DesignerView):
    def __init__(self, user):
        self.user = user
        self.game = None
        self.menu = None
        self.table = None
        super().__init__(timeout=30)
        text1 = TextDisplay("# LAST BATTLE")
        text2 = TextDisplay("Main menu")
        thumbnail = Thumbnail(bot.user.display_avatar.url)
        section = Section(text1, text2, accessory=thumbnail)
        section.add_text("-# Good luck")
        self.menu = Container(section, color=Color.from_rgb(180, 180, 180))
        async def delete_callback(interaction: Interaction):
            fusers.pop(self.user.id, None)
            self.stop()
            await interaction.response.defer()
            await self.user.thread.delete()
        async def play_callback(interaction: Interaction):
            if self.user.id in fusers:
                await interaction.response.send_message("You already are waiting for opponent",ephemeral=True)
                return
            if len(fusers) == 0:
                fusers[self.user.id] = self.user
                self.menu.add_item(TextDisplay("Waiting for the opponent"))
                await interaction.response.edit_message(view=self)
                return
            opponent = next(iter(fusers.values()))
            game = MyGame(opponent, self.user)
            await interaction.response.defer()
            await game.create(opponent, self.user)
        delete_button = Button(label="Delete Thread", style=ButtonStyle.red, id=0)
        delete_button.callback = delete_callback
        play_button = Button(label="Start the game", style=ButtonStyle.green, id=0)
        play_button.callback = play_callback
        row = ActionRow()
        row.add_item(delete_button)
        row.add_item(play_button)
        self.menu.add_item(row)
        self.add_item(self.menu)
    async def show_game(self):
        self.clear_items()
        self.table = Container(color=Color.from_rgb(180, 180, 180))
        thumbnail1 = Thumbnail(bot.user.display_avatar.url)
        text3 = TextDisplay("# LAST BATTLE")
        text4 = TextDisplay("Game interface")
        section1 = Section(text3, text4, accessory=thumbnail1)
        self.table.add_item(section1)
        self.add_item(self.table)
        await self.user.message.edit(view=self)

class MyUser:
    def __init__(self):
        self.id = None
        self.thread = None
        self.name = None
        self.view = None
        self.game = None
        self.message = None
    @classmethod
    async def create(cls, ctx: discord.ApplicationContext):
        global users
        self = cls()
        self.name = ctx.author.name
        self.id = ctx.author.id
        self.thread = await ctx.channel.create_thread(name=f"{ctx.author.name}'s game",)
            #type=discord.ChannelType.private_thread, invitable=False)
        await self.thread.add_user(ctx.author)
        await self.thread.send(f"The new game thread for {self.name} was created")
        self.view = MyView(self)
        self.message = await self.thread.send(view=self.view)
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
    global fusers
    user=await MyUser.create(ctx)
    

bot.run(os.getenv('TOKEN'))