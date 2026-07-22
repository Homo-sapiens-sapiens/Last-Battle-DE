from io import BytesIO
import os
import random
from dotenv import load_dotenv
load_dotenv()
import discord
from discord import (ApplicationContext, Bot, ButtonStyle,
    Color, File, Interaction, SeparatorSpacingSize, User)
from discord.ui import (ActionRow, Button, Container, DesignerView,
    MediaGallery, Section, Select, Separator, TextDisplay, Thumbnail, button)

fusers = {}
rad_emj=["<:grey:1525893303898214400>", "<:gren:1497928981188575232>"]
obj_emj=["<:grey:1525893303898214400>", "<:gfac:1525896582036324372>", "<:ghom:1525985697612304537>", "<:glan:1529613092257005744>"]
num_emj=["<:zero:1527297606986764360>","<:one:1527003069726855270>", "<:two:1527001046713499840>",
         "<:thre:1527003085443043418>", "<:four:1527003120905883648>", "<:five:1527003139335651469>",
         "<:six:1527003153260876039>", "<:sevn:1527003167030509669>", "<:eigt:1527003185309552760>"]
sym_emj=["<:job:1529150229193035917>","<:cog:1529150214764499084>", "<:shot:1529610411278733402>"]
blac = "<:blac:1527003711849631855>"

class MyGame:
    def __init__(self):
        self.users = [None, None]
        self.views = [None, None]
        self.grounds = [[[0] * 8 for i in range(8)], [[0] * 8 for i in range(8)]]
        self.rads = [[[0] * 8 for i in range(8)], [[0] * 8 for i in range(8)]]
        self.counts = [[2, 3, 1], [2, 3, 1]]
        self.reses = [[20, 20, 1], [20, 20, 1]]
    def __del__(self):
        print("MyGame deleted")

    async def create(self, player1, player2):
        self.users= [player1, player2]
        self.views = [self.users[0].view, self.users[1].view]
        self.views[0].game = self
        self.views[1].game = self
        self.users[0].game = self
        self.users[1].game = self
        
        fusers.pop(self.users[0].id, None)
        fusers.pop(self.users[1].id, None)
        self.users[0].number = 0
        self.users[1].number = 1
        for i in range(2):
            for j in range(len(self.counts[i])):
                k=0
                while k != self.counts[i][j]:
                    r1 = random.randint(0, 7)
                    r2 = random.randint(0, 7)
                    if not self.grounds[i][r1][r2]:
                        self.grounds[i][r1][r2] = j+1
                        k+=1
        await self.views[0].show_game()
        await self.views[1].show_game()
        
    async def user_lost(self, user):
        loser_v = user
        winner_v = self.views[(loser_v.user.number+1)%2]
        await winner_v.victory()
        await loser_v.defeat()
        self.views[0].game = None
        self.views[1].game = None
        self.users[0].game = None
        self.users[1].game = None
    async def build(self, bder):
        ask = bder.b_set
        self.grounds[bder.user.number][ask[1]-1][ask[2]-1]=ask[0]
            
class MyView(DesignerView):
    def __init__(self, user):
        self.user = user
        self.game = None
        self.menu = None
        self.table = None
        self.screen = None
        self.b_set = [0, 0, 0]
        super().__init__(timeout=None)
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
                await game.create(self.user, opponent)
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

        b_input = Select(placeholder = "Object", min_values = 1, max_values = 1,
            options = [
                discord.SelectOption(
                    label="Overground factory",
                    value="1",
                    emoji=discord.PartialEmoji(name="up_fac",id=1525896582036324372)),
                discord.SelectOption(
                    label="Overground city",
                    value="2",
                    emoji=discord.PartialEmoji(name="up_hom",id=1525985697612304537))])
        y_input = Select(placeholder = "Vertical", min_values = 1, max_values = 1,
            options = [discord.SelectOption(label=str(i), value=str(i))for i in range(1, 9)])
        x_input = Select(placeholder = "Horizontal", min_values = 1, max_values = 1,
            options = [discord.SelectOption(label=str(i), value=str(i))for i in range(1, 9)])
        bul_button = Button(label="Proceed Building", style=ButtonStyle.grey)
        sur_button = Button(label="Surrender", style=ButtonStyle.red)
        
        async def b_set(interaction: Interaction):
            await interaction.response.defer()
            self.b_set[0]=int(b_input.values[0])
        async def y_set(interaction: Interaction):
            await interaction.response.defer()
            self.b_set[1]=int(y_input.values[0])
        async def x_set(interaction: Interaction):
            await interaction.response.defer()
            self.b_set[2]=int(x_input.values[0])
        async def build_ask(interaction: Interaction):
            if 0 in self.b_set: await interaction.response.send_message("You did not chosed the object or the coordinates",ephemeral=True)
            elif self.game.grounds[self.user.number][self.b_set[1]-1][self.b_set[2]-1]==0:
                await self.game.build(self)
                await self.ground()
                b_input.value=[]
                x_input.value=[]
                y_input.value=[]
                self.b_set=[0, 0, 0]
                await interaction.response.edit_message(view=self)
            else:
                await interaction.response.send_message("It is already object in this spot",ephemeral=True)
        async def surrender(interaction: Interaction):
            await interaction.response.defer()
            await self.game.user_lost(self)
            
        b_input.callback = b_set
        x_input.callback = x_set
        y_input.callback = y_set
        bul_button.callback = build_ask
        sur_button.callback = surrender
        
        row1=ActionRow(b_input)
        row2=ActionRow(x_input)
        row3=ActionRow(y_input)
        row4=ActionRow(bul_button, sur_button)
        
        self.table.add_item(row1)
        self.table.add_item(row2)
        self.table.add_item(row3)
        self.table.add_item(row4)
    async def ground(self):
        num = self.user.number
        ground = self.game.grounds[num]
        res = self.game.reses[num]
        self.screen.content=f""+blac
        for i in range(1,9): self.screen.content += num_emj[i]
        for i in range(3):
            self.screen.content+="\n"+num_emj[i+1]
            for j in range(8):self.screen.content+=obj_emj[ground[i][j]]
            self.screen.content+=sym_emj[i]
            for j in str(res[i]):
                self.screen.content+=num_emj[int(j)]
        for i in range(3,8):
            self.screen.content+="\n"+num_emj[i+1]
            for j in range(8):self.screen.content+=obj_emj[ground[i][j]]
        self.screen.content+="\n"
        self.screen.content+="\n"

        print(len(self.screen.content))
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