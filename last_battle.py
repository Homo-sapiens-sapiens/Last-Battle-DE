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
emoji=["<:all_grey:1524562050477461635>", "<:all_green:1497928981188575232>"]

class MyGame:
    def __init__(self):
        self.user1 = None
        self.user2 = None
        self.view1 = None
        self.view2 = None
        self.ground1 = [[0] * 8 for i in range(8)]
        self.ground2 = [[0] * 8 for i in range(8)]
        self.rad1 = [[0] * 8 for i in range(8)]
        self.rad2 = [[0] * 8 for i in range(8)]
    def __del__(self):
        print("MyGame deleted")
    async def create(self, player1, player2):
        self.user1 = player1
        self.user2 = player2 #!!!
        self.view1 = self.user1.view
        self.view2 = self.user2.view
        self.view1.game = self
        self.view2.game = self
        self.user1.game = self
        self.user2.game = self
        fusers.pop(self.user1.id, None)
        fusers.pop(self.user2.id, None)
        self.user1.number = 1
        self.user2.number = 2
        await self.view1.show_game()
        await self.view2.show_game()
    async def user_lost(self, user):
        if self.view1 == user:
            loser_v = self.view1
            winner_v = self.view2
        else:
            loser_v = self.view2
            winner_v = self.view1
        await winner_v.victory()
        await loser_v.defeat()
        self.view1.game = None
        self.view2.game = None
        self.user1.game = None
        self.user2.game = None
            
class MyView(DesignerView):
    def __init__(self, user):
        self.user = user
        self.game = None
        self.menu = None
        self.table = None
        self.screen = None
        super().__init__(timeout=30)
    async def create_menu(self):
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
            elif len(fusers) == 0:
                fusers[self.user.id] = self.user
                self.menu.add_item(TextDisplay("Waiting for the opponent"))
                await interaction.response.edit_message(view=self)
                return
            else:
                opponent = next(iter(fusers.values()))
                game = MyGame()
                await interaction.response.defer()
                await game.create(opponent, self.user)
                self.user.number = 2
                opponent.number = 1
        delete_button = Button(label="Delete Thread", style=ButtonStyle.red)
        delete_button.callback = delete_callback
        play_button = Button(label="Start the game", style=ButtonStyle.green)
        play_button.callback = play_callback
        row = ActionRow()
        row.add_item(delete_button)
        row.add_item(play_button)
        self.menu.add_item(row)
    async def show_menu(self):
        self.clear_items()
        self.add_item(self.menu)
        await self.message.edit(view=self)
    async def create_table(self):
        self.table = Container(color=Color.from_rgb(180, 180, 180))
        thumbnail1 = Thumbnail(bot.user.display_avatar.url)
        text3 = TextDisplay("# LAST BATTLE")
        text4 = TextDisplay("Game interface")
        section1 = Section(text3, text4, accessory=thumbnail1)
        self.table.add_item(section1)
        self.add_item(self.table)
        self.screen = TextDisplay(f"Wait a bit...")
        self.table.add_item(self.screen)
        row1 = ActionRow()
        sur_button = Button(label="Surender", style=ButtonStyle.red)
        async def surrender(interaction: Interaction):
            await interaction.response.defer()
            await self.game.user_lost(self)
        sur_button.callback = surrender
        row1.add_item(sur_button)
        self.table.add_item(row1)
    async def ground(self):
        if self.user.number == 1:
            ground = self.game.ground1
        else:
            ground = self.game.ground2
        self.screen.content = f"\n".join("".join(emoji[cell] for cell in row)for row in ground)
    async def show_game(self):
        self.clear_items()
        self.add_item(self.table)
        await self.ground()
        await self.message.edit(view=self) 
    async def defeat(self):
        await self.show_menu()
        self.menu.add_item(TextDisplay("You lost. Better luck next time!"))
        await self.user.message.edit(view=self)
    async def victory(self):
        await self.show_menu()
        self.menu.add_item(TextDisplay("You won! Congrats with survival!"))
        await self.user.message.edit(view=self)

class MyUser:
    def __init__(self):
        self.id = None
        self.thread = None
        self.name = None
        self.view = None
        self.game = None
        self.message = None
        self.number = None
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
        await self.view.create_menu()
        await self.view.create_table()
        self.message = await self.thread.send(view=self.view)
        await self.view.show_menu()
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