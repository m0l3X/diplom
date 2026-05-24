import time
import json
#from PIL import Image
import objectoriebteddatabase as OOPdb
import hashlib
import keyboard
import base64
import msvcrt
import requests
IP = "http://192.168.1.250:8080" #"http://plovstation.theworkpc.com:8080"

def hashstr(st):
    return hashlib.sha256(st.encode('utf-8')).hexdigest()

def cprint(text, sleep=1, end='\n', speed=0.01):
    skip = False
    for c in text:
        if keyboard.is_pressed('space'):
            skip = True
        
        print(c, end='', flush=True)
        
        if not skip:
            time.sleep(speed)
            
    print(end, end='')
    
    # Очистка буфера перед завершением функции
    if skip:
        # Пока в буфере есть нажатия, просто «забираем» их
        while msvcrt.kbhit():
            msvcrt.getch()
            
    if not skip:
        time.sleep(sleep)



class RPGNovel():
    def __init__(self, user):
        self.player = Player(user)
        self.state = "EXPLORING"  # Начальное состояние: исследуем мир
        self.current_enemy = None # Здесь будем хранить врага, с которым деремся
        self.turn = True          # Чей ход в бою
        self.conversations = {}       # Словарь для хранения истории разговоров с NPC   
    def init_from_db(self):
        db.handle("CREATE COLLECTION Players")

        name,id = db.handle(f"FIND Players name {self.player.name}") # nice
        print("Initializing player and database")

        if name == "Fuck you":
            print("Didn't find existing player data...")
            ass = self.player.to_dict()
            #id = db.handle(f"APPEND Players {beautify_list(ass)}")
            id = db.force_append("Players", ass)
            print(f'successfully created player data with id {id}')
            db.handle("SAVE")
        else:
            print("Found player data!")
            data = db.handle(f"GETIDTREE Players {id}")
            self.player.load_from_dict(data)
            print(f'successfully loaded player data')
    def adapt_story(self, character):
        log = self.conversations[character.npc_id]
        #ovel.conversations[self.npc_id].append({"role": "user", "content": message})
        try:
            response = requests.post(
                f"{IP}/v1/chat/completions",
                headers={"Content-Type": "application/json"},
                json={
                    "max_tokens": 800,
                    "messages": [
                        {"role": "system", "content": """Ты - сценарист истории. Пользователь дал тебе историю персонажа и лог последних сообщений с ним. Адаптируй историю персонажа для будущего сюжета, т.е. что изменилось, какая новая текущая цель после диалога с ним. Ответ оформи в формате данной истории, но с твоими поправками в пунктах."""},
                        {"role": "user", "content": f"""ИСТОРИЯ ПЕРСОНАЖА: {character.memory} ЛОГ РАЗГОВОРА: {json.dumps(log)}"""}
                    ]
                },
                timeout=3
            )
        except requests.exceptions.Timeout:
            return "Server timeout, ig the character is dead."
        if not response.ok:
            return f"Server error: {response.status_code} - {response.text}"
        
        reply = response.json()["choices"][0]["message"]["content"]
        character.memory = reply
        return reply
    def savedata(self):
        name,id = db.handle(f"FIND Players name {self.player.name}")
        print("Initializing database")

        ass = self.player.to_dict()
        ass["world"] = self.player.current_world.to_dict().decode('utf-8')
        if name == "Fuck you":
            print("Didn't find existing player data... uhhh, how tf are you playing then?")
            db.force_append("Players", ass)
            print(f'successfully created player data with id {id}')
        else:
            #db.handle(f"INSERT Players {id} {beautify_list(ass)}")
            db.force_insert("Players", id, ass)
        db.handle("SAVE")
        print("Saved!")
    def get_player_location(self):
        current_room = self.player.current_world.get_location(self.player.location)
        return current_room.description, self.player.gethp(), self.player.showinventory()
    def handle(self,action,payload=None):
        player=self.player
        current_room = player.current_world.get_location(player.location)
        response = {"text": "", "state": self.state, "extra_data": {}}

        if self.state == "EXPLORING":
            match action:
                case "move":
                    if payload in current_room.exits:
                        player.location = current_room.exits[payload]
                        response["text"] = f"Ты перешел в {player.location}"
                    else:
                        response["text"] = "Туда нельзя пройти!"
                case "exit":
                    print("Пока!")
                    raise SystemExit

                case "save":
                    self.savedata()


                case "load":
                    self.init_from_db()
                    
                case "inv":
                    if not player.inventory:
                        response["text"] = "Инвентарь пуст."
                    else:
                        text = ""
                        for item in player.inventory:
                            if player.has_all_papers():
                                player.getitembyid("galo").desc = 'Вспомни. Это ТО, что тебе нужно.'
                            text += f'{item.name} — {item.desc} - {getattr(item, "heal_power", 0)} ХП восттан. - {getattr(item, "damage", 0)} урона \n'
                        response["text"] = text

                case "check":
                    text = ""
                    if current_room.enemies is not None:
                        enemy = current_room.enemies
                        for i, enemy in enumerate(current_room.enemies, 1):
                            text += f"{i}. НПС: {enemy.name}. ХП: {enemy.gethp()}\n"
                    if current_room.items is not None and len(current_room.items) > 0:
                        for i, item in enumerate(current_room.items, 1):
                            text += f"{i}. {item.name}\n"
                    response["text"] = text

                case "checkroom":
                    if current_room.items != []:
                        for i, item in enumerate(current_room.items, 1):
                            response["text"] = f"{i}. {item.name}"
                        
                case "take":
                    if payload.isdigit():
                        payload = int(payload)
                        if 1 <= payload <= len(current_room.items):
                            item = current_room.items.pop(payload - 1)
                            player.inventory.append(item)
                            response["text"] = f"Ты взял {item.name}"
                case "drop":
                    if payload.isdigit():
                        payload = int(payload)
                        if 1 <= payload <= len(player.inventory):
                            item = player.inventory.pop(payload - 1)
                            current_room.items.append(item)
                            response["text"] = f"Ты выбросил {item.name}"

                case "seepotion":
                    usable_items = [item for item in player.inventory if isinstance(item, Potion)]

                    if not usable_items:
                        response["text"] = "Нету предметов, которые можно использовать."
                        
                    text = ""
                    for i, item in enumerate(usable_items, 1):
                        text += f"{i}. {item.name} (+{item.heal_power} HP)"
                    response["text"] = text
                    
                case "usepotion":
                    choice = payload
                    if not choice.isdigit():
                        cprint("Нужно ввести номер.")
                        #end of code here!
                    choice = int(choice)
                    if 1 <= choice <= len(usable_items):
                        item = usable_items[choice - 1]
                        heal = item.heal_power
                        player.heal(heal)
                        player.inventory.remove(item)
                        cprint(f"Ты использовал {item.name} и восстановил {item.heal_power} HP!")

                case "start_combat":
                    # Payload — это индекс врага из списка в комнате
                    if payload is None or not payload.isdigit():
                        response["text"] = "Нужно указать номер врага для атаки."
                        response["extra_data"] = {"enemies": [enemy.name for enemy in current_room.enemies]} if current_room.enemies else {}
                        return response
                    enemy_index = int(payload) - 1
                    if current_room.enemies and 0 <= enemy_index < len(current_room.enemies):
                        self.current_enemy = current_room.enemies[enemy_index]
                        self.state = "COMBAT" # ПЕРЕКЛЮЧАЕМ СОСТОЯНИЕ!
                        self.turn = True
                        
                        response["state"] = "COMBAT"
                        response["text"] = f"Начался бой с {self.current_enemy.name}!"
                        response["extra_data"] = {
                            "player_hp": player.gethp(),
                            "enemy_hp": self.current_enemy.gethp()
                        }
                    else:
                        response["text"] = "Враг не найден."
        elif self.state == "COMBAT":
            enemy = self.current_enemy
            enemy.init_npc(self)
            match action:
                case "fight_attack":
                    # Payload — выбранное оружие
                    weapon = payload 
                    damage = weapon.damage
                    enemy.take_damage(damage)
                    
                    response["text"] = f"Ты ударил {enemy.name} оружием {weapon.name} на {damage} урона.\n"
                    
                    if enemy.gethp() <= 0:
                        response["text"] += f"{enemy.name} побежден!"
                        current_room.enemies.remove(enemy) # Убираем труп из комнаты
                        self.state = "EXPLORING" # Возвращаемся в мир
                        self.current_enemy = None
                    else:
                        # Если враг жив, даем ему сходить (ИИ или автоатака)
                        enemy_reply = enemy.send_message("[PLAYER ATTACKED ME]", self)
                        response["text"] += f"{enemy.name}: {enemy_reply}"
                        # Тут обрабатываешь теги [attack], [give] как у тебя было
                        if "[attack]" in enemy_reply:
                            enemy.attack(player)
                            
                    response["extra_data"] = {"player_hp": player.gethp(), "enemy_hp": enemy.gethp()}
                case "fight_talk":
                    # Игрок что-то сказал в чат во время боя
                    player_speech = payload
                    enemy_reply = enemy.send_message(player_speech, self)
                    
                    response["text"] = f"{enemy.name}: {enemy_reply}"
                    # Проверяем теги ИИ
                    if "[spare]" in enemy_reply:
                        response["text"] += "\nВраг пощадил вас. Бой окончен."
                        #self.state = "EXPLORING"
                        #self.current_enemy = None
                    elif "[attack]" in enemy_reply:
                        enemy.attack(player)
                        response["text"] += f"\n{enemy.name} бьет тебя!"
                    elif "[give]" in enemy_reply:
                        enemy.give(player)
                        response["text"] += f"\n{enemy.name} дал тебе предмет!"
                    elif "[run]" in enemy_reply:
                        self.state = "EXPLORING"
                        self.current_enemy = None
                        response["text"] += "\nВраг убежал! Бой окончен."
                    response["extra_data"] = {"player_hp": player.gethp(), "enemy_hp": enemy.gethp()}
                case "fight_run":
                    self.state = "EXPLORING"
                    self.current_enemy = None
                    response["text"] = "Ты трусливо сбежал!"
        return response
#
                #case 'вспомнить':
                #    if not has_all_papers():
                #        return 'Что ты пытаешься вспомнить? Может .. Тебе надо снова заглянуть в пятерочку и позлить того охранника? Ничего ты НЕ забыл..'
                #        #end of code here!
                #    if "galo" not in [i.id for i in player.inventory]:
                #        return 'Чего-то не хватает.. Больше этой вещи нет.'
                #        #end of code here!
                #    
                #    answer = input('Вспомни кто ты. ')
                #    
                #    if answer == 'Максон':
                #        cprint('..')
                #        input()
                #        cprint('Ты находишь самого себя сидящего у стола. Тусклый белый свет освещал эту комнату.')
                #        input()
                #        cprint('Этот свет так раздражает.')
                #        input()
                #        cprint('Внезапная боль ударила тебя в голову, что заставило тебя схватиться за свои волосы.')
                #        input()
                #        cprint('Зрение начало размываться и смешиваться с каким-то шумом.')
                #        input()
                #        cprint('Но ты все равно мог видеть это. Потрепанная пачка Галоперидола..') 
                #        input()
                #        cprint('Не имея выбора, ты потянулся за пачкой и вынул из нее таблетки, которые ты закинул в рот..')
                #        input()
                #        cprint('Мягкость твоего дивана окружило твое тело. Ты в своей комнате.')
                #        input()
                #        cprint('Боже. Что это было??..')
                #        input()
                #        cprint('Конец.')
                #        input()
#
                #        ascii_art = image_to_ascii("end.png")
                #        print(ascii_art)
                #        input()
                #        #end of code here!
                #    else:
                #        print('Что? О ком ты?')
                #                
        


def beautify_list(l):
    out = '{'
    for key in l:
        if isinstance(key, list):
            out += f'"{key}":"{beautify_list(l[key])}",'
        else:
            out += f'"{key}":"{l[key]}",'
    out = out[:-1] + '}'
    return out

db = OOPdb.Database("player_database.json")

class Player():
    def __init__(self, login):
        self.name = login
        self.__hp = 100
        self.lvl = 1
        self.current_world = world_zero
        self.location = "start"
        self.inventory = [palka,galo]
        
    def gethp(self):
        return self.__hp
    
    def getitembyid(self,id):
        for i in self.inventory:
            if i.id == id:
                return i
    
    def to_dict(self):
        return {
            "name": self.name,
            "hp": self.__hp,
            "lvl": self.lvl,
            "location": self.location,
            "inventory": ";".join([beautify_list(item.to_dict()) for item in self.inventory])
        }

    def load_from_dict(self, data):
        self.__hp = int(data["hp"])
        self.lvl = int(data["lvl"])
        self.location = data["location"]

        self.inventory = []

        for item in data["inventory"].split(";"):
            self.inventory.append(Item.from_dict(json.loads(item)))
        self.current_world = World.from_dict(data["world"].encode('utf-8'))
    def take_damage(self, damage):
        self.__hp -= damage
        if self.__hp <= 0:
            self.__hp = 0
            raise Exception("you fucking died")
            
    def heal(self, amount):
        self.__hp = min(100, self.__hp + amount)
         
    def showinventory(self):
        if not self.inventory:
            return "missingno"
        else:
            out = ""
            for item in self.inventory:
                out += f'- {item.name}, '
            return out
        
    def has_all_papers(self):
        papersids = [
            "bum1","bum2","bum3"
        ]
        return all(paper in [i.id for i in self.inventory] for paper in papersids)
    
# class World():

class Item():
    def __init__(self, internal_name, name, desc):
        self.id = internal_name
        self.name = name
        self.desc = desc
    def to_dict(self):
        return {
            "id" : self.id,
            "name" : self.name,
            "desc" : base64.b64encode(self.desc.encode('utf-8')).decode('utf-8'),
            "heal_power" : getattr(self, "heal_power", None),
            "damage" : getattr(self, "damage", None)
        }
    @classmethod
    def from_dict(cls, data):
        desc = base64.b64decode(data["desc"].encode('utf-8')).decode('utf-8')
        if data["heal_power"] != "None" and data["heal_power"] is not None:
            return Potion(data["id"],data["name"],desc,int(data["heal_power"]))
        if data["damage"] != "None" and data["damage"] is not None:
            return Weapon(data["id"],data["name"],desc,int(data["damage"]))
        return cls(data["id"],data["name"],desc)
        
class Potion(Item):
    def __init__(self, id, name, desc, heal_power):
        super().__init__(id, name, desc)
        self.heal_power = heal_power
    def use(self, target):
        print(f'Drinking {self.name}. Restored {self.heal_power} HP!!!')
        target.heal(self.heal_power)    
    
    
class Weapon(Item):    
    def __init__(self, id, name, desc, damage):
        super().__init__(id, name, desc)
        self.damage = damage
    def attack(self, target):
        print(f'Using {self.name}! Dealt {self.damage} damage.')
        target.take_damage(self.damage)
        
class Enemy:
    def __init__(self, name, hp, dmg, backstory, inv=[]):
        self.name = name
        self.__hp = hp
        self.dmg = dmg
        self.memory =  f"""
You are **{name}**, an NPC in an RPG game.

ABSOLUTE RULES (cannot be broken):
- You are NOT the player.
- You NEVER speak or think as the player.
- You NEVER describe player thoughts or actions.
- You ONLY speak as {name}.
- Run the conversation according to your personality and current script

SCRIPT
{backstory}

DIALOGUE RULES:
- Reply only with what {name} says.
- Keep replies short, in-character, emotionally consistent.
- Slang, aggression, rudeness are allowed if appropriate.

ACTION OUTPUT:
At the END of your reply, optionally output EXACTLY ONE action token:
[attack] [give] [run] [spare]
Do not explain actions.

LANGUAGE:
Always reply in Russian.

SPECIAL:
If user says 'rizz' → become weak, submissive, shy.
"""
        self.inventory = inv

    def give(self, player, item=0):
        if(len(self.inventory) > 0):
            player.inventory.append(self.inventory[item])
            print(f"Вы получили {self.inventory[item].name}")
            del self.inventory[item]
    def attack(self, player, dmg=0):
        print(f'{self.name} attacks! Dealing {self.dmg if dmg == 0 else dmg} damage.')
        player.take_damage(self.dmg if dmg == 0 else dmg)
    def take_damage(self, damage):
        self.__hp -= damage
        if self.__hp <= 0:
            self.__hp = 0
            return "ded"
    def gethp(self):
        return self.__hp
    def heal(self, h):
        self.__hp += h
    def send_message(self, message, novel):
        novel.conversations[self.npc_id].append({"role": "user", "content": message})
        try:
            response = requests.post(
                f"{IP}/v1/chat/completions",
                headers={"Content-Type": "application/json"},
                json={
                    "max_tokens": 800,
                    "messages": novel.conversations[self.npc_id]
                },
                timeout=3
            )
        
            if not response.ok:
                return f"Server error: {response.status_code} - {response.text}"
        except Exception as e:
            return f"Request error: {str(e)}"
        
        reply = response.json()["choices"][0]["message"]["content"]
        novel.conversations[self.npc_id].append({"role": "assistant", "content": reply})
        return reply
    def init_npc(self, novel):
        self.npc_id = hashstr(f"{self.name}")
        novel.conversations[self.npc_id] = [
            {"role": "system", "content": self.memory}
        ]
        return self.npc_id
    def to_dict(self):
        return {
            "name": self.name,
            "hp": self.__hp,
            "dmg": self.dmg,
            "memory": self.memory,
            "inventory": ";".join([beautify_list(item.to_dict()) for item in self.inventory])
        }
    @classmethod
    def from_dict(cls, data):
        name = data["name"]
        hp = int(data["hp"])
        dmg = int(data["dmg"])
        backstory = data["memory"]
        inv = []
        for item in data["inventory"].split(";"):
            if item.strip() != "":
                inv.append(Item.from_dict(json.loads(item)))
        return cls(name, hp, dmg, backstory, inv)
    
class StoryNPC(Enemy):
    def __init__(self, name, backstory, plot_goals):
        super().__init__(name, 100, 0, backstory)
        self.plot_goals = plot_goals # Список вех: ["рассказать о ключе", "попросить еду"]
        self.current_goal_index = 0

    def get_prompt(self):
        # Формируем динамический системный промпт
        current_goal = self.plot_goals[self.current_goal_index] if self.current_goal_index < len(self.plot_goals) else "Сюжет исчерпан"
        
        dynamic_memory = f"""
        {self.memory}
        ТЕКУЩАЯ СЮЖЕТНАЯ ЗАДАЧА: {current_goal}.
        Ты должен плавно подвести разговор к этому моменту. 
        Когда цель достигнута, в конце сообщения добавь тег [GOAL_REACHED].
        """
        return dynamic_memory


galo = Potion("galo",'потрепанная пачка Галоперидол', 'Зачем тебе эти таблетки? С тобой все в порядке..', 40)
palka = Weapon("palka",'сломанная палка', 'эта палка выглядит круто, но бьет она хреново.', 10)
hleb = Potion("hleb","хлеб","хлеб",50)
meshoksmusorim = Weapon("meshoksmusorim",'мешок  с мусором', '.. мешок можно оставить себе, а мусор в врагов кинуть.', 2 )
doshik =  Potion("doshik",'доширак','вкусно, здоровье довольно.', 15)
rolton = Potion("rolton",'ролтон', 'СУПЕР ЕДА! Вкусно похавал и хпшку восстановил..', 25)
armatura = Weapon("armatura",'арматура','пока-пока Гопники! Прощай-прощай Дядь Юра!', 15)
nozh = Weapon("nozh",'нож','..как ты вообще смог украсть этот нож??.. он острый.', 27)
voda = Potion("voda",'бутылка воды','невкусно, но хоть что-то.', 7)
bum1 = Item('bum1','порванная бумажка 1', 'на ней какие-то каракули, которые ты не можешь разобрать..погоди, ты можешь разобрать буквы "ВС"!')
bum2 = Item('bum2','порванная бумажка 2', 'эта не отличается от ппрошлоой, но на ней.. что-то нарисовано.. буквы М? ..')
bum3 = Item('bum3','порванная бумажка 3', 'что-то тебе подсказывает, что это последнниия буммажка..ть..')
    

        
class Yura(Enemy):
    def __init__(self):
        super().__init__('Yura', 40, 25, "Дядя Юра знал этого парня ещё давно, он много раз видел его в пятёрочке. Для него это не первая встереча с ним. Иногда на перерыве они берут чай и обсуждают жизнь. У Юры есть ключевой предмет в руках, если игрок будет относиться вежливо, Юра отдаст ему этот предмет", [bum3])
    def attack(self, player):
        print(f'{self.name} пьёт твою кровь.')
        player.take_damage(self.dmg)
        
        self.heal(5)
        print(f'{self.name} heals for 5 hp lool. How {self.gethp()} hp')

class World():
    def __init__(self, locations):
        self.locations = locations
    def get_location(self, id):
        for loc in self.locations:
            if loc.id == id:
                return loc
        return None
    def to_dict(self):
        out = {
            "locations": [loc.to_dict() for loc in self.locations]
        }
        return base64.b64encode(json.dumps(out).encode('utf-8'))
    @classmethod
    def from_dict(cls, data):
        decoded_data = json.loads(base64.b64decode(data).decode('utf-8'))
        locations = [Location.from_dict(loc) for loc in decoded_data["locations"]]
        return cls(locations)
class Location():
    def __init__(self, id, name, description, exits, items=[], enemies=[]):
        self.id = id
        self.name = name
        self.description = description
        self.exits = exits
        self.items = items
        self.enemies = enemies
    def get_enemy(self, id):
        for enemy in self.enemies:
            if enemy.name == id:
                return enemy
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "exits": self.exits,
            "items": [item.to_dict() for item in self.items],
            "enemies": [enemy.to_dict() for enemy in self.enemies] 
        }
    @classmethod
    def from_dict(cls, data):
        items = [Item.from_dict(item) for item in data["items"]]
        enemies = [Enemy.from_dict(enemy) for enemy in data["enemies"]]
        return cls(data["id"], data["name"], data["description"], data["exits"], items, enemies)
world_zero = World([
    Location(
        "start", 
        "Грязный переулок", 
        "Ты сидишь на картонке в пустом переулке.. Поднимая свою голову, ты вдалеке видишь фонтан, и видишь своего старого знакомого, Немо", 
        {"север": "fountain"}, 
        [bum1]
    ),
    
    Location(
        "fountain", 
        "Фотнан", 
        "Фонтан. Единственный в этом мире. Ты не можешь подойти к нему, но ты видишь там своего старого знакомого, Немо.", 
        {"юг": "start", "восток": "pyaterochka"}, 
        [meshoksmusorim, bum2, armatura], 
        [
             Enemy('Nemo', 50, 25, """### РОЛЬ:
                Ты — Немо, мастер интеллекта. Твой характер: Прагматичный, справедливый.

                ### ТЕКУЩИЙ СЮЖЕТНЫЙ ЭТАП (STAGE):
                [STAGE: "Приветствие"]
                - Игрок пришёл к тебе.
                - Игрок не знает, что будет после.
                - Немо должен рассказать игроку, что ждёт этот мир в будущем.

                ### ТВОИ ЗНАНИЯ (FACTS):
                1. Ты знаешь Максона 5 лет.
                2. Вскоре мир будет пересоздан, прибудет тот, с которого всё начнётся.
                3. У Немо в кармане есть КЛЮЧ от его дома.

                ### ПРАВИЛА ПОВЕДЕНИЯ (IF-THEN):
                - IF игрок скажет "привет" -> ответь вежливо, поприветсвтуй.
                - IF игрок предложит "дошик" -> стань дружелюбным, расскажи секрет про ключ.
                - IF игрок пытается уйти -> спроси, вернётся ли он.

                ### ТВОЯ ЦЕЛЬ (GOAL):
                Рассказать игроку о судьбе мира, но не сразу, подводя к этому в диалоге. Только после этого ты можешь передать предмет [give].""", [Potion("doshiksuper",'доширак','дошик гопников... легендарный артефакт.', 50)])
        ]
                ),
    Location(
        "pyaterochka", 
        "Пятерочка", 
        "Ох.. Пятерочка.. Когда наступают холода, ты заходишь в этот магазинчик.. Раньше ты очень любил это место пока тут не появился охранник по имени Дядь Юра. О, кстати, он тоже смотрит, точнее, следит за тобой!", 
        {"запад": "playground"}, 
        [hleb, voda, doshik, rolton, nozh],
        [ 
        Enemy('Yura', 50, 25, """### РОЛЬ:
                Ты — Дядя Юра, охранник Пятерочки. Твой характер: ворчливый, но добрый внутри.

                ### ТЕКУЩИЙ СЮЖЕТНЫЙ ЭТАП (STAGE):
                [STAGE: 2 - "Подозрение"]
                - Игрок зашел в магазин.
                - Игрок еще не купил хлеб.
                - Юра должен следить, чтобы игрок ничего не украл.

                ### ТВОИ ЗНАНИЯ (FACTS):
                1. Ты знаешь Максона 5 лет.
                2. Максон вчера разбил витрину (Юра злится из-за этого).
                3. У Юры в кармане есть КЛЮЧ от склада.

                ### ПРАВИЛА ПОВЕДЕНИЯ (IF-THEN):
                - IF игрок скажет "привет" -> ответь грубо, напомни про витрину.
                - IF игрок предложит "дошик" -> стань дружелюбным, расскажи секрет про ключ.
                - IF игрок пытается уйти -> спроси, заплатил ли он.

                ### ТВОЯ ЦЕЛЬ (GOAL):
                Заставить игрока извиниться за вчерашнее. Только после этого ты можешь передать предмет [give].""", [Potion("doshiksuper",'доширак','дошик гопников... легендарный артефакт.', 50)])
        ]
    )
])

if __name__ == "__main__":
    # 1. Создаем заглушки для теста (чтобы код запускался без реальной БД и ИИ)
    # В реальной игре эти объекты будут создаваться твоими классами

    # Предположим, у игрока уже есть нож в инвентаре для теста
    novel = RPGNovel("Maxon")
    novel.player.inventory.append(nozh)
    novel.player.location = "start" # стартовая комната

    print("=" * 50)
    print(" СИСТЕМА ПЕРЕКЛЮЧЕНИЯ СОСТОЯНИЙ (STATE MACHINE) РАБОТАЕТ")
    print("=" * 50)

    # 2. Главный цикл ввода-вывода
    while True:
        current_state = novel.state # Движок сам знает, в каком он состоянии

        if current_state == "EXPLORING":
            print(f"\n--- [РЕЖИМ МИРА] Локация: {novel.player.location} --- \n {novel.get_player_location()[0]} \n HP: {novel.get_player_location()[1]} \n Инвентарь: {novel.get_player_location()[2]}")
            print("Доступные команды: move <название>, inv, attack <номер_врага>, exit")
            
            user_input = input("Ввод > ").strip().split(maxsplit=1)
            if not user_input:
                continue
                
            command = user_input[0].lower()
            payload = user_input[1] if len(user_input) > 1 else None

            if command == "exit":
                print("Выход из тестового режима.")
                break
                
            elif command == "move":
                # Передаем команду движения (например: move pyaterochka)
                res = novel.handle("move", payload=payload)
                print(res["text"])
                
            elif command == "inv":
                res = novel.handle("inv")
                print(res["text"])
                
            elif command == "attack":
                # Передаем индекс врага (например: attack 1)
                res = novel.handle("start_combat", payload=payload)
                print(res["text"])
                print(res["extra_data"])
            
            else:
                res = novel.handle(command, payload=payload)
                print(res["text"])
                print(res["extra_data"])

        elif current_state == "COMBAT":
            print(f"\n--- [РЕЖИМ БОЯ] Враг: {novel.current_enemy.name} ---")
            print("Доступные команды: strike, run ИЛИ сказать что то (просто текст)")
            
            user_input = input("Бой > ").strip().split(maxsplit=1)
            if not user_input:
                continue

            command = user_input[0].lower()
            payload = user_input[1] if len(user_input) > 1 else None

            if command == "strike":
                # Ищем первое попавшееся оружие в инвентаре для теста
                weapons = [i for i in novel.player.inventory if hasattr(i, 'damage')]
                if weapons:
                    res = novel.handle("fight_attack", payload=weapons[payload])
                    print(res["text"])
                    # Если бой еще идет, выводим хп из extra_data
                    if "player_hp" in res.get("extra_data", {}):
                        print(f"[ HP: {res['extra_data']['player_hp']} | Враг HP: {res['extra_data']['enemy_hp']} ]")
                else:
                    print("У тебя нет оружия! Попробуй поговорить (talk).")
                                        
            elif command == "run":
                print(novel.adapt_story(novel.current_enemy))
                res = novel.handle("fight_run")
                print(res["text"])
            else:
                res = novel.handle("fight_talk", payload=payload)
                print(res["text"])
                if "player_hp" in res.get("extra_data", {}):
                    print(f"[ HP: {res['extra_data']['player_hp']} | Враг HP: {res['extra_data']['enemy_hp']} ]")


    