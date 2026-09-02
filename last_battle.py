from io import BytesIO
import gc
import os
import random
from dotenv import load_dotenv
load_dotenv()
import discord
from discord.ext import commands
from discord import (ApplicationContext, Bot, ButtonStyle,
    Color, File, Interaction, SeparatorSpacingSize, User)
from discord.ui import (ActionRow, Button, Container, DesignerView,
    MediaGallery, Section, Select, Separator, TextDisplay, Thumbnail, button)

modes=("Режим строительства","Режим атаки","Режим радиации",)
rad_emj=("<:0rd:1532872671484838139>",  "<:1rd:1530616688117022800>","<:2rd:1530616711437357146>",
         "<:3rd:1530616727229173780>","<:4rd:1530616745709146184>","<:5rd:1530616774108647476>",
         "<:6rd:1530616796111966318>","<:7rd:1530616814227427388>","<:8rd:1530616829452750880>",)
obj_emj=("<:grey:1525893303898214400>", "<:ghom:1525985697612304537>", "<:gfac:1525896582036324372>", "<:glan:1529613092257005744>",)
num_emj=("<:zero:1527297606986764360>","<:one:1527003069726855270>", "<:two:1527001046713499840>",
         "<:thre:1527003085443043418>", "<:four:1527003120905883648>", "<:five:1527003139335651469>",
         "<:six:1527003153260876039>", "<:sevn:1527003167030509669>", "<:eigt:1527003185309552760>",)
sym_emj=("<:prd:1529150214764499084>", "<:atc:1529610411278733402>",)
wep_emj=("huh","<:nuke:1530907025855483994>",)

helps=(f"Это режим строительства. Тут вы можете строить объекты. На данный момент есть три типа объектов : Города, заводы и наземные"+
           "платформы. \n Города "+obj_emj[1]+" - основа игры. Уничтожение всех городов противника - обязательное и единственное условие победы. Также "+
           "города дают немного производственной мощи. \nЗаводы "+obj_emj[2]+" нужны для основной производственной мощи "+sym_emj[0]+" которая нужна "+
           "для строительства ракет и обьектов. \nПусковые установки "+obj_emj[3]+" нужны для ракетных запусков "+sym_emj[1]+" \n"+
           "Произвдоственная мощность "+sym_emj[0]+" и ракетные запуски "+sym_emj[1]+" не копятся - если они не были использованы - значит заводы и установки просто простояли этот ход.\n"+
           "Произвдоственная мощность "+sym_emj[0]+" и ракетные запуски "+sym_emj[1]+" обновляются в начале хода",
            f"Это режим атаки. Тут вы можете атаковать поле противника. Выберите координаты, тип орудия и запускайте.\n"+
            "Вам показывается радиационная карта поля противника. По ней вы можете определить местоположение вражеских обьектов.\n"+
           "Над картой показано, какой цвет показывает какой уровень радиации\n"+
           "Радиация 2 и меньше естественна - она появляется на пустых клетках спонтанно. Обьекты выделяют стабильную, неизменяемую радиацию.\n"+
           "Радиация больше 2 - следствие ваших атак. Она постепенно рассеивается, пока не уменьшается до естественных показателей.\n"+
           "Для поиска клеток с объектами ищите клетки с неменяющейся радиацией. Заводы "+obj_emj[2]+" и пусковые установки "+obj_emj[3]+" дают 2 радиации, Города "+obj_emj[1]+" - одну.\n"+
           "Для победы уничтожьте все города "+obj_emj[1]+" противника. Про функции обьектов можете прочитать на страничке помощи режима строительства\n"+
           "Радиация обновляется в конце хода. Радиация не распространяется на соседние клетки - эта механика не добавлена.\n"+
           "Радиация 8 и больше навсегда делает клетку недоступной для строительства. Используйте кобальтовые бомбы для этого.\n"+
           "Противник, как и вы, может специально выпускать радиацию, чтобы запутать вас.",
           f"Это режим радиации. Тут вам показывается радиационная карта вашего поля\n"+
           "В этом режиме вы можете специально выпускать радиацию, чтобы запутать противника. \n"+
           "Радиация 8 и больше навсегда делает клетку недоступной для строительства\n"+
           "Про свойства радиации можете прочитать на страничке помощи режима атаки\n"+
           "Про функции объектов можете прочитать на страничке помощи режима строительства")

blac = "<:black:1527003711849631855>"
prd_cst = (30, 20, 10,)
obj_prd = (5, 10)
rck_cst = (10, 20)
rad_rck = (4, 8)
rad_cst = 10
rad_obj = (1, 2, 2,)
rad_shw = (0,) * 8 + (1,) * 2 + (2,)
rad_add = (1,)
fusers={}
min_cost = 10

class MyGame:
    def __init__(self):
        self.users = [None, None]
        self.views = [None, None]
        self.grounds = [[[0] * 8 for i in range(8)], [[0] * 8 for i in range(8)]]
        self.rads = [[[0] * 8 for i in range(8)], [[0] * 8 for i in range(8)]]
        self.counts = [[2, 2, 1], [2, 2, 1]]
        self.reses = [[30, 1], [30, 1]]
        self.moveof = False
    def __del__(self): print("game session deleted")
    async def create(self, player1, player2):
        self.users= [player1, player2]
        self.views = [self.users[0].view, self.users[1].view]
        self.views[0].game = self
        self.views[1].game = self
        self.users[0].game = self
        self.users[1].game = self
        fusers.pop(self.users[0].id, None)
        fusers.pop(self.users[1].id, None)
        self.users[0].number = False
        self.users[1].number = True
        for i in range(2):
            for j in range(8):
                for k in range(8): self.rads[i][j][k]=rad_shw[random.randint(0,10)]
            for j in range(len(self.counts[i])):
                k=0
                while k != self.counts[i][j]:
                    r1 = random.randint(0, 7)
                    r2 = random.randint(0, 7)
                    if not self.grounds[i][r1][r2]:
                        self.grounds[i][r1][r2] = j+1
                        self.rads[i][r1][r2] = rad_obj[j]
                        k+=1
        self.views[0].status.content="Ваш ход"
        await self.users[1].temp_msg("# ИГРА НАЧАЛАСЬ", "Ход противника. Удачной игры")
        await self.users[0].temp_msg("# ИГРА НАЧАЛАСЬ", "Ваш ход. Удачной игры")
        self.views[1].status.content="Ход противника"
        for i in range(2):
            self.views[1].selects[i].disabled = True
            self.views[1].table.items[i+4].items[0].disabled = True
        await self.views[0].show_game()
        await self.views[1].show_game()
    async def user_lost(self, user):
        loser_v = user
        winner_v = self.views[(loser_v.user.number+1)%2]
        await winner_v.ending()
        await loser_v.ending()
        self.views[0].game = None
        self.views[1].game = None
        self.users[0].game = None
        self.users[1].game = None
    async def proceed(self):
        bder=self.views[self.moveof]
        ask = bder.g_set
        num=self.moveof
        match bder.g_set[3]:
            case 1:
                self.grounds[num][ask[1]-1][ask[2]-1]=ask[0]
                self.reses[num][0]-=prd_cst[ask[0]-1]
                self.counts[num][ask[0]-1]+=1
            case 2:
                if self.grounds[(num+1)%2][ask[1]-1][ask[2]-1]!=0:
                    self.counts[(num+1)%2][self.grounds[(num+1)%2][ask[1]-1][ask[2]-1]-1]-=1
                    t="Координаты: h=" + str(ask[1]) + ", w=" + str(ask[2])
                    await self.users[(num+1)%2].temp_msg("# ВАШ ОБЪЕКТ БЫЛ УНИЧТОЖЕН",t)
                    self.grounds[(num+1)%2][ask[1]-1][ask[2]-1]=0
                    if self.counts[(num+1)%2][0]==0:
                        await self.users[num].temp_msg("# ПОБЕДА","Вы уничтожили все города противника.")
                        await self.users[(num+1)%2].temp_msg("# ПОРАЖЕНИЕ","Противник уничтожил все ваши города")
                        await self.user_lost(self.views[(num+1)%2])
                        return  
                self.reses[num][0]-=rck_cst[ask[0]-1]
                self.reses[num][1]-=1
                if self.rads[(num+1)%2][ask[1]-1][ask[2]-1]<rad_rck[ask[0]-1]: self.rads[(num+1)%2][ask[1]-1][ask[2]-1]=rad_rck[ask[0]-1]
                await self.views[(num+1)%2].sh_map(self.views[(num+1)%2].g_set[3]-1)
                await self.users[(num+1)%2].message.edit(view=self.views[(num+1)%2])
                await self.views[num].sh_map(1)
            case 3:
                self.reses[num][0]-=rad_cst
                self.rads[num][ask[1]-1][ask[2]-1]+=rad_add[ask[0]-1]
                if self.rads[num][ask[1]-1][ask[2]-1]>=8:
                    self.rads[num][ask[1]-1][ask[2]-1]=8
                    await self.users[num].temp_msg("#ВЫ ПОДНЯЛИ РАДИАЦИЮ ВЫШЕ КРИТИЧЕСКОГО ПРЕДЕЛА","Данное место более недоступно для жизни и работы")
                    self.grounds[num][ask[1]-1][ask[2]-1]=0
                await self.views[(num+1)%2].sh_map(self.views[(num+1)%2].g_set[3]-1)
                await self.views[num].sh_map(2)
                await self.users[(num+1)%2].message.edit(view=self.views[(num+1)%2])
        if self.reses[num][0]<min_cost:
            await self.users[num].temp_msg("# ВАШ ХОД ОКОНЧЕН","У вас закончились ресурсы, поэтому ход передается противнику")
            await self.next_user()
    async def next_user(self):
        num=self.moveof
        for j in range(2):
            for i in range(2):
                self.views[j].selects[i].disabled = (num==j)
                self.views[j].table.items[i+4].items[0].disabled = (num==j)
        self.views[num].status.content = "Ход противника"
        for i in range(8):
            for j in range(8):
                if self.rads[num][i][j]==8: pass
                elif self.grounds[num][i][j]!=0:
                    if self.rads[num][i][j]<=rad_obj[self.grounds[num][i][j]-1]: self.rads[num][i][j]=rad_obj[self.grounds[num][i][j]-1]
                    else: self.rads[num][i][j]-=1
                elif self.rads[num][i][j]>2: self.rads[num][i][j]-=1
                else: self.rads[num][i][j]=rad_shw[random.randint(0,10)]
        await self.views[num].sh_map(self.views[num].g_set[3]-1)
        await self.users[num].message.edit(view=self.views[num])
        self.moveof=(num+1)%2
        num=self.moveof
        await self.users[num].temp_msg("# ВАШ ХОД","противник закончил ход")
        self.views[num].status.content = "Ваш ход"
        self.reses[num][0]=self.counts[num][0]*obj_prd[0]+self.counts[num][1]*obj_prd[1]
        self.reses[num][1]=self.counts[num][2]
        await self.views[num].sh_map(self.views[num].g_set[3]-1)
        await self.users[num].message.edit(view=self.views[num])

class MyView(DesignerView):
    def __init__(self, user):
        self.user = user
        self.game = None
        self.menu = None
        self.table = None
        self.screen = TextDisplay("PLACEHOLDER")
        self.status = TextDisplay("Добро пожаловать. Нажмите СТАРТ чтобы запустить игру")
        self.selects = []
        self.rovv = None
        self.g_set = [0, 0, 0, 1]
        self.message = None
        super().__init__(timeout=None)
    def __del__(self): print("game view deleted")
    async def create_menu(self):
        text1 = TextDisplay("# LAST BATTLE")
        thumbnail = Thumbnail(bot.user.display_avatar.url)
        section = Section(text1, self.status, accessory=thumbnail)
        self.menu = Container(section, color=Color.from_rgb(180, 180, 180))
        #KILL VIEW AND USER
        async def delete_callback(interaction: Interaction): 
            fusers.pop(self.user.id, None)
            self.clear_items()
            self.status = None
            self.selects = None
            self.rovv = None
            self.g_set = None
            self.message = None
            self.cont=[]
            self.menu = None
            self.table = None
            self.screen = None
            await interaction.message.delete()
            self.user = None
            self.stop()
            self.id = None
            return
        async def play_callback(interaction: Interaction):
            if self.user.id in fusers: await interaction.response.send_message("Пожалуйста, подождите",ephemeral=True)
            elif len(fusers) == 0:
                fusers[self.user.id] = self.user
                await interaction.response.send_message("Подождите, мы ищем вам соперника",ephemeral=True)
            else:
                opponent = next(iter(fusers.values()))
                game = MyGame()
                await game.create(self.user, opponent)
        delete_button = Button(label="ВЫХОД", style=ButtonStyle.red)
        delete_button.callback = delete_callback
        play_button = Button(label="СТАРТ", style=ButtonStyle.green)
        play_button.callback = play_callback
        row = ActionRow()
        row.add_item(delete_button)
        row.add_item(play_button)
        self.menu.add_item(row)
        return
    async def show_menu(self): #SHOW MENU
        self.clear_items()
        self.add_item(self.menu)
        await self.message.edit(view=self)
        return
    async def create_table(self):
        self.table = Container(color=Color.from_rgb(180, 180, 180))
        thumbnail1 = Thumbnail(bot.user.display_avatar.url)
        text3 = TextDisplay("# LAST BATTLE")
        section1 = Section(text3, self.status, accessory=thumbnail1)
        self.table.add_item(section1)
        self.add_item(self.table)
        self.screen = TextDisplay(f"Wait a bit...")
        self.table.add_item(self.screen)
        m_input = Select(placeholder = modes[0], min_values = 1, max_values = 1, id=101,
            options = [
                discord.SelectOption(label = modes[0], value="0"),
                discord.SelectOption(label = modes[1], value="1"),
                discord.SelectOption(label = modes[2], value="2")])
        self.selects.append(
            Select(placeholder = "Обьект", min_values = 1, max_values = 1, id=102,
                options = [
                    discord.SelectOption(
                        label="Наземный город. Цена: 30 п.м, доход: 5.п.м.",
                        value="1",
                        emoji=discord.PartialEmoji(name="ghom",id=1525985697612304537)),
                    discord.SelectOption(
                        label="Наземный завод. Цена: 20 п.м, доход: 10 п.м.",
                        value="2",
                        emoji=discord.PartialEmoji(name="gfac",id=1525896582036324372)),
                    discord.SelectOption(
                        label="Пусковая платформа. Цена:10 п.м, дает 1 запуск в ход",
                        value="3",
                        emoji=discord.PartialEmoji(name="glan",id=1529613092257005744))]))
        self.selects.append(
            Select(placeholder = "Орудие", min_values = 1, max_values = 1, id = 103,
                options = [
                    discord.SelectOption(
                        label="Обычная ядерная бомба. 10 п.м.",
                        value="1",
                        emoji=discord.PartialEmoji(name="nuke",id=1530907025855483994)),
                    discord.SelectOption(
                        label="Кобальтовая ядерная бомба. 20 п.м, навсегда делает клетку недоступной",
                        value="2")]))
        self.selects.append(
            Select(placeholder = "Действие", min_values = 1, max_values = 1, id = 104,
                   options = [
                       discord.SelectOption(
                        label="Выпустить радиацию. 10 п.м, +1 еденица радиации",
                        value="1",)]))
        y_input = Select(placeholder = "Координата по вертикали", min_values = 1, max_values = 1, id = 105,
            options = [discord.SelectOption(label=str(i), value=str(i))for i in range(1, 9)])
        x_input = Select(placeholder = "Координата по горизонтали", min_values = 1, max_values = 1, id = 106,
            options = [discord.SelectOption(label=str(i), value=str(i))for i in range(1, 9)])
        prc_but = Button(label="ПОДТВЕРДИТЬ", style=ButtonStyle.green)
        pas_but = Button(label="Закончить ход", style=ButtonStyle.grey)
        hel_but = Button(label="Помощь", style=ButtonStyle.grey)
        sur_but = Button(label="Сдаться", style=ButtonStyle.red)
        async def m_set(interaction: Interaction):
            mod = int(m_input.values[0])
            m_input.placeholder = modes[mod]
            await self.sh_map(mod)
            self.rovv.remove_item(self.selects[self.g_set[3]-1])
            self.rovv.add_item(self.selects[mod])
            self.g_set[0] = 0
            self.g_set[3]=mod+1
            await interaction.response.edit_message(view=self)
        async def b_set(interaction: Interaction):
            await interaction.response.defer()
            self.g_set[0]=int(self.selects[0].values[0])
        async def r_set(interaction: Interaction):
            await interaction.response.defer()
            self.g_set[0]=int(self.selects[1].values[0])
        async def a_set(interaction: Interaction):
            await interaction.response.defer()
            self.g_set[0]=int(self.selects[2].values[0])
        async def y_set(interaction: Interaction):
            await interaction.response.defer()
            self.g_set[1]=int(y_input.values[0])
        async def x_set(interaction: Interaction):
            await interaction.response.defer()
            self.g_set[2]=int(x_input.values[0])
        async def act_ask(interaction: Interaction):
            await interaction.response.defer()
            if self.game.moveof != self.user.number: await interaction.followup.send("Сейчас не ваш ход",ephemeral=True)
            elif 0 in self.g_set: await interaction.followup.send("Вы не выбрали координаты или тип объекта/орудия",ephemeral=True)
            else:
                match self.g_set[3]:
                    case 1:
                        if self.game.grounds[self.user.number][self.g_set[1]-1][self.g_set[2]-1]!=0: await interaction.followup.send("У вас уже есть обьект на данных координатах",ephemeral=True)
                        elif prd_cst[self.g_set[0]-1]>self.game.reses[self.user.number][0]: await interaction.followup.send("У вас недостаточно производственной мощи",ephemeral=True)
                        elif self.game.rads[self.user.number][self.g_set[1]-1][self.g_set[2]-1]>7: await interaction.followup.send("На данных координатах слишком высокая радиация для строительства",ephemeral=True)
                        else:
                            await self.game.proceed()
                            await self.sh_map(int(self.g_set[3]-1))
                            x_input.value=[]
                            y_input.value=[]
                            self.g_set=[0, 0, 0, self.g_set[3]]
                            await interaction.message.edit(view=self)
                    case 2:
                        if not self.game.reses[self.user.number][1]: await interaction.followup.send("У вас нет свободных пусковых платформ",ephemeral=True)
                        elif rck_cst[self.g_set[0]-1]>self.game.reses[self.user.number][0]: await interaction.followup.send("У вас недостаточно производственной мощи",ephemeral=True)
                        else:
                            await self.game.proceed()
                            await self.sh_map(int(self.g_set[3]-1))
                            x_input.value=[]
                            y_input.value=[]
                            self.g_set=[0, 0, 0, self.g_set[3]]
                            await interaction.message.edit(view=self)
                    case 3:
                        if rad_cst > self.game.reses[self.user.number][0]: await interaction.followup.send("У вас недостаточно производственной мощи",ephemeral=True)
                        elif self.game.rads[self.user.number][self.g_set[1]-1][self.g_set[2]-1] >=8: await interaction.followup.send("Нельзя повышать радиацию больше 8",ephemeral=True)
                        else:
                            await self.game.proceed()
                            await self.sh_map(int(self.g_set[3]-1))
                            x_input.value=[]
                            y_input.value=[]
                            self.g_set=[0, 0, 0, self.g_set[3]]
                            await interaction.message.edit(view=self)
        async def pass_move(interaction: Interaction):
            if self.game.moveof != self.user.number: await interaction.followup.send("Сейчас не ваш ход",ephemeral=True)
            else:
                await interaction.response.defer()
                await self.game.next_user()
        async def hint(interaction: Interaction):
            try:await interaction.response.send_message(helps[self.g_set[3]-1],ephemeral=True)
            except: await interaction.response.send_message("Ошибка",ephemeral=True)
        async def surrender(interaction: Interaction):
            await interaction.response.defer()
            await self.game.users[(self.user.number + 1)%2].temp_msg("# ПОБЕДА","Противник сдался")
            await self.game.user_lost(self)
            await self.user.temp_msg("# ПОРАЖЕНИЕ","Вы сдались")
        m_input.callback = m_set
        self.selects[0].callback = b_set
        self.selects[1].callback = r_set
        self.selects[2].callback = a_set
        x_input.callback = x_set
        y_input.callback = y_set
        prc_but.callback = act_ask
        hel_but.callback = hint
        pas_but.callback = pass_move
        sur_but.callback = surrender
        row0=ActionRow(m_input)
        self.rovv=ActionRow(self.selects[0])
        row2=ActionRow(x_input)
        row3=ActionRow(y_input)
        row4=ActionRow(prc_but, hel_but, pas_but, sur_but)
        self.table.add_item(row0)
        self.table.add_item(self.rovv)
        self.table.add_item(row2)
        self.table.add_item(row3)
        self.table.add_item(row4)
        #for i in self.table.items:
            #print(i)
        #print(self.table.items)
    async def sh_map(self, mode):
        num = self.user.number
        self.screen.content=f""
        match mode:
            case 0:
                    ground = self.game.grounds[num]
                    emj_set = obj_emj
            case 1:
                    ground = self.game.rads[(num+1)%2]
                    emj_set = rad_emj
                    for i in range(9): self.screen.content += rad_emj[i]
                    self.screen.content+="\n"
            case 2:
                    ground = self.game.rads[num]
                    emj_set = rad_emj
                    for i in range(9): self.screen.content += rad_emj[i]
                    self.screen.content+="\n"
        res = self.game.reses[num]
        for i in range(9): self.screen.content += num_emj[i]
        self.screen.content+=blac
        for i in range(2):
            self.screen.content+="\n"+num_emj[i+1]
            for j in range(8): self.screen.content+=emj_set[ground[i][j]]
            self.screen.content+=sym_emj[i]
            for j in str(res[i]): self.screen.content+=num_emj[int(j)]
        for i in range(2,8):
            self.screen.content+="\n"+num_emj[i+1]
            for j in range(8): self.screen.content+=emj_set[ground[i][j]]
    async def show_game(self):
        self.clear_items()
        self.add_item(self.table)
        await self.sh_map(0)
        await self.message.edit(view=self) 
    async def ending(self):
        await self.show_menu()
        self.status = TextDisplay("Игра окончена. Нажмите СТАРТ чтобы запустить игру снова")
        await self.user.message.edit(view=self)

class T_mes(DesignerView):
    def __init__(self, t1, t2):
        self.txt1 = t1
        self.txt2 = t2
        super().__init__(timeout=None)
        text1 = TextDisplay(self.txt1)
        text2 = TextDisplay(self.txt2)
        okay = Button(label="OK", style=ButtonStyle.grey)
        async def ok(interaction: Interaction):
            await interaction.message.delete()
            self.clear_items()
            self.stop()
            self.id = None
            self._message = None
            self.author = None
            self.flags = None
            self.txt1 = None
            self.txt2 = None
            self.children = None
            return
        okay.callback = ok
        row = ActionRow(okay)
        window = Container(text1, text2, row, color=Color.from_rgb(255, 0, 0))
        self.add_item(window)
    def __del__(self): print("temporal message deleted")
    
class MyUser:
    def __init__(self):
        self.id = None
        self.thread = None
        self.name = None
        self.view = None
        self.game = None
        self.message = None
        self.number = None
        self.dm = None
    def __del__(self):
        print("game user deleted")
    @classmethod
    async def create(cls, ctx: discord.ApplicationContext):
        self = cls()
        self.name = ctx.author.name
        self.id = ctx.author.id
        self.dm = await ctx.author.create_dm()
        async for message in self.dm.history(limit=None):
            if message.author == bot.user:
                try: await message.delete()
                except: pass
        self.view = MyView(self)
        await self.view.create_menu()
        self.message = await self.dm.send(content=f"Menu for {self.name}",view=self.view)
        self.view.clear_items()
        self.view.add_item(self.view.menu)
        await self.message.edit(content=None, view=self.view)
        await self.view.create_table()
        return self
    async def temp_msg(self, t1, t2):
        temp = T_mes(t1, t2)
        await self.dm.send(view=temp)
        
bot = Bot()

from invite_cog import InviteCog
bot.add_cog(InviteCog(bot))

@bot.event
async def on_ready():
    global events
    print(f"{bot.user} is ready and online!")
    return

@bot.slash_command(name="start", description="Начать игру в личном чате")
async def new_game(ctx: discord.ApplicationContext):
    if ctx.guild is None:
        await ctx.respond("Эта команда доступна только на сервере.",ephemeral=True)
        return
    try:
        await ctx.respond("Создаем меню",ephemeral=True)
        user=await MyUser.create(ctx)
        global fusers
        await ctx.followup.send("Меню для вас создано в личном чате",ephemeral=True)
        return
    except discord.Forbidden as e: await ctx.followup.send(f"Не удалось отправить сообщение. Попробуйте открыть личные сообщения и использовать команду снова. В случае успеха вы можете снова закрыть личные сообщения",ephemeral=True)
    
bot.run(os.getenv('TOKEN'))