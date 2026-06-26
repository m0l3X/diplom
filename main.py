import pygame
import sys as sus
#import websearch
from rpnovel_engine import RPGNovel 
import os
#import base64
import random
import threading

from frontend_classes import AssetManager, Button, Image, PygameTextPrinter, Menu, SelectableButton, TextInputField, ScrollList, VisualMap

pygame.init()
pygame.mixer.init()

weight, height = 1000, 800
screen = pygame.display.set_mode((weight, height))
pygame.display.set_caption('Gay')

clock = pygame.time.Clock()

novel = RPGNovel("Malex") 

assets = AssetManager()

display_text = PygameTextPrinter(speed_ms=25)
display_text.set_text("missingno")
last_text_string = ""

# Цвета
black = (0, 0, 0) 
white = (255, 255, 255)
ired = (205, 92, 92)
dred = (34, 3, 4)

# Диалоговое окно и шрифты
dialog_font = pygame.font.SysFont('Freeride', 27) 
ui_font = pygame.font.SysFont('Freeride', 20)
names_font = pygame.font.SysFont('Freeride', 35)

# Загрузка ассетов (код напарника)
#nemo_image = pygame.image.load('assets/images/sprites/enemy/nemo.png')
imgfile_bg = pygame.image.load('assets/images/fon.png').convert()
bgs = {}
novel.handle("load")
for location in novel.player.current_world.locations:
    if os.path.exists(f'assets/images/locations/{location.id}.png'):
        bgs[location.id] = pygame.image.load(f'assets/images/locations/{location.id}.png').convert()
imgfile_bg_menu = assets.get_image("UI", "menu_fon1")
imgfile_textbox = assets.get_image("UI", "button")

imgfile_btn_map = assets.get_image("UI", "btn_map")
imgfile_map = assets.get_image("UI", "map")


imgfile_blank = pygame.image.load('assets/images/blank.png').convert()

imgfile_close = assets.get_image("UI", "btn_close")

imgfile_proceed = assets.get_image("UI", "btn_proceed")
imgfile_btn_inspect = assets.get_image("UI", "btn_inspect")
imgfile_btn_inv = assets.get_image("UI", "btn_inv")
imgfile_btn_save = assets.get_image("UI", "btn_save")


imgfile_btn_attack = assets.get_image("UI", "btn_attack")
imgfile_btn_act = assets.get_image("UI", "btn_act")
imgfile_btn_item = assets.get_image("UI", "btn_item")
imgfile_btn_mercy = assets.get_image("UI", "btn_mercy")

imgfile_play0 = assets.get_image("UI", "Pplay") 
imgfile_play1 = assets.get_image("UI", "Pplay1")
imgfile_exit0 = assets.get_image("UI", "exit")
imgfile_exit1 = assets.get_image("UI", "exit1")
imgfile_gamename = assets.get_image("UI", "game")
cursor_img = assets.get_image("UI", "cursor")
malex_click = assets.get_image("UI", "malexclick")

#тут загружаются кадрi анимации
anim_malex_static = [
    assets.get_image("sprites", "Pmalex"),
    assets.get_image("sprites", "Pmalex01"),
]
anim_malex_thinks = [
    assets.get_image("sprites", "Pmalexthinks"),
    assets.get_image("sprites", "Pmalexthinks1"),
]
anim_malex_menu = [
    assets.get_image("UI", "malex"),
    assets.get_image("UI", "malex1"),
]

imgfile_malex_fall = assets.get_image("sprites", "Pmalexfall")
imgfile_malex_attack = assets.get_image("sprites", "Pmalexattack")

imgfile_inv = assets.get_image("UI", "inventory")


def start_game_callback():
    res = novel.handle("load") # Получаем описание локации при входе в игру
    display_text.set_text(res["text"])
    special_flags = novel.get_player_location().special_flags
    image_malex.translate(special_flags["MX"], special_flags["MY"], time=0) if "MX" in special_flags.keys()  else ""
    image_bg.translate(special_flags["BGX"], special_flags["BGY"], time=0) if "BGX" in special_flags.keys() else ""
    global current_scene
    current_scene = "intro"
btn_play = Button(65, 290, 255, 90, img=imgfile_play0, func=start_game_callback,
                  on_hover=lambda b: setattr(b, 'img', imgfile_play1),
                  off_hover=lambda b: setattr(b, 'img', b.orig_img),wobble=False)

btn_exit = Button(65, 410, 255, 90, img=imgfile_exit0, func=lambda: [pygame.quit(), sus.exit()],
                  on_hover=lambda b: setattr(b, 'img', imgfile_exit1),
                  off_hover=lambda b: setattr(b, 'img', b.orig_img),wobble=False)
# Зоны для кликов в самой игре (Кнопки действий)
# Формат: pygame.Rect(X, Y, ШИРИНА, ВЫСОТА)

#херня с анимацией ..dunno если честно куда ее вставить. так что пусть сюда.. ):
# переменніе для управления таймингом анимации

image_malex = Image(0, 0, anim_malex_static[0], animations=[anim_malex_static, [imgfile_malex_fall, imgfile_malex_fall], anim_malex_thinks, [imgfile_malex_attack,imgfile_malex_attack]], animation_speed=600, anim=True)
image_bg = Image(0, 0, bgs[novel.player.location] if novel.player.location in bgs.keys() else imgfile_bg)
image_malex_menu = Image(0, 0, anim_malex_menu[0], animations=[anim_malex_menu,[malex_click,malex_click]], animation_speed=800, anim=True) #какая тут ошибка гайс

# --- КЛИКАБЕЛЬНЫЙ СПРАЙТ В МЕНЮ ---
# Здесь лежат параметры хитбокса клика по спрайту Малекс в главном меню.


btn_malex_menu_click = Button(590,180,210,200, func=lambda: image_malex_menu.short_animation(1,700))

menu_main = Menu([btn_play,btn_exit,btn_malex_menu_click,image_malex_menu])

image_ui_cross = Image(0,0, pygame.image.load('assets/images/UI/cross.png'))
start_time = 0

def uicross_shatter():
    def animate():
        btn_n.enabled = False
        btn_s.enabled = False
        btn_w.enabled = False
        btn_e.enabled = False
        image_ui_cross.shake(5,5300)
        image_ui_cross.translate(-50,-100,300)
        pygame.time.wait(300)
        image_ui_cross.translate(-300,1000,1000)
        pygame.time.wait(1000)
        image_malex.translate(1000,0,3000)
        pygame.time.wait(3000)
        res = novel.handle("tp","intro19")
        display_text.set_text(res["text"])
        btn_n.enabled = True
        btn_s.enabled = True
        btn_w.enabled = True
        btn_e.enabled = True
        image_ui_cross.translate(0,0,0)
        image_bg.img = bgs[novel.player.location] if novel.player.location in bgs.keys() else imgfile_bg

    threading.Thread(target=animate,daemon=True).start()

######## TODO: это очень захардкоденая хрень сейчас. что я бы сделал в будущем, сделал бы свой язык составления анимаций по кейфреймам, чтобы потом хранить их в файле
# также, возникает вопрос, а как мы в файл запишем какие переменные в коде хранят нам нужные объекты которые мы будем анимировать?
# просто делаем таблицу где каждый объект в анимации имеет свой id
# anim_table = {
#   "malex":image_malex
#   "nemo":image_nemo
#   "button1":btn_button1 
# } и так далее
# потом передаём этому методу таблицу
# execute_animation("path/to/anim/file.anim", anim_table)
# и он составляет код по типу того что выше и выполняет его
#
#
#
anim_table = {
    "malex":image_malex,
    "bg": image_bg
}

def execute_room_flags(direction):
    res = novel.handle("move", direction)
    special_flags = novel.get_player_location().special_flags
    print(special_flags)
    for flag in special_flags.keys():
        match flag:
            case "trls":
                for thing in special_flags["trls"].keys():
                    table = special_flags["trls"][thing]
                    gamething = anim_table.get(thing, None)
                    if gamething:
                        gamething.translate(table.get("X",0),table.get("Y",0),table.get("T",0))
                        gamething.animation = table.get("ANIM",0)
                        
    image_bg.img = bgs[novel.player.location] if novel.player.location in bgs.keys() else imgfile_bg
    return res

def action_move(direction):
    res = execute_room_flags(direction)
    display_text.set_text(res["text"])
            

    if "uicross_shatter" in res["extra_data"]:
        image_ui_cross.shake(res["extra_data"]["uicross_shatter"]*2,200)
        if res["extra_data"]["uicross_shatter"] == 5:
            uicross_shatter()
    print(res["extra_data"])

def action_start_combat(enemy_idx=1):
    res = novel.handle("start_combat", enemy_idx)
    display_text.set_text(res["text"])
    global cur_enemy_imgfile
    enemy_id = res["extra_data"]["enemy"].id if "extra_data" in res.keys() and "enemy" in res["extra_data"].keys() else "missingno"
    cur_enemy_imgfile = assets.get_image("enemies",enemy_id)
    close_items_menu()

def action_special():
    
    res = execute_room_flags("spec")
    display_text.set_text(res["text"])
    


# Действие 1: Подобрать предмет из комнаты
def action_pick_up(item_index, item_name):
    res = novel.handle("take", item_index)
    display_text.set_text(res["text"])
    
    close_items_menu()
    # Обновляем это же меню, заново запросив шмот из комнаты
    #room_data = novel.handle("checkroom_internal")["text"]
    #rebuild_items_menu(room_data, action_pick_up)

def action_inspect(item_index, item_name):
    res = novel.handle("inspect", item_index) 
    display_text.set_text(res["text"])
    # Закрываем инвентарь после использования (или обновляем, если предмет исчезает)
    close_items_menu()

def action_drop_item(item_index, item_name):
    # Предположим, у тебя на бэкенде есть команда "use" или "inspect"
    res = novel.handle("drop", item_index) 
    display_text.set_text(res["text"])
    
    # Закрываем инвентарь после использования (или обновляем, если предмет исчезает)
    close_items_menu()

# Действие 2: Использовать/осмотреть предмет из личного инвентаря
def action_use_item(item_index, item_name):
    # Предположим, у тебя на бэкенде есть команда "use" или "inspect"
    res = novel.handle("usepotion", item_index) 
    display_text.set_text(res["text"])
    
    # Закрываем инвентарь после использования (или обновляем, если предмет исчезает)
    close_items_menu()

def rebuild_items_menu(raw_data, on_click_callback, keep_idx=-1,inv_img=True, x=-20, y=70):
    """
    Принимает строку с предметами через ';' и функцию, 
    которая должна выполниться при клике на элемент.
    """
    image_malex.animation = 2
    if not raw_data: 
        items_menu.panels = [
            Image(0, 0, imgfile_inv) if inv_img else Image(1000, 0, imgfile_inv),
            btn_close_items,
            Button(60, 40, text="Пусто", func=lambda: close_items_menu())
        ]
        return

    items_list = raw_data.split(";")
    new_panels = [Image(0, 0, imgfile_inv),btn_close_items] if inv_img else [btn_close_items]
    for i, item_name in enumerate(items_list):
        # Передаем в callback-функцию индекс предмета и его имя
        if i == keep_idx:
            btn = Button(
                x+120, y + i * 50, 
                200, 70,
                func=lambda item_idx=i, name=item_name: on_click_callback(item_idx, name),
                img=imgfile_item
            )
        else:
            btn = Button(
                x, y + i * 50, 
                200, 70,
                func=lambda item_idx=i, name=item_name: on_click_callback(item_idx, name),
                on_hover=lambda btn: btn.translate(100, btn.rect.y, time=200), 
                off_hover=lambda btn: btn.translate(-20, btn.rect.y, time=200),
                img=imgfile_item
            )
        file = pygame.transform.scale(assets.get_image("items",item_name),(70,70))
        btn.set_overlay_image(file,30,30)
        new_panels.append(btn)
        
    items_menu.panels = new_panels

def horizontal_items_menu(raw_data, on_click_callback, keep_idx=-1,inv_img=True, x=300, y=400):
    """
    Принимает строку с предметами через ';' и функцию, 
    которая должна выполниться при клике на элемент.
    """
    image_malex.animation = 2
    if not raw_data: 
        items_menu.panels = [
            Image(0, 0, imgfile_inv) if inv_img else Image(1000, 0, imgfile_inv),
            btn_close_items,
            Button(x, y, text="Пусто", func=lambda: close_items_menu())
        ]
        return

    items_list = raw_data.split(";")
    new_panels = [Image(0, 0, imgfile_inv),btn_close_items] if inv_img else [btn_close_items]
    for i, item_name in enumerate(items_list):
        # Передаем в callback-функцию индекс предмета и его имя
        if i == keep_idx:
            btn = Button(
                x + i * 50, y - 120, 
                20, 200,
                func=lambda item_idx=i, name=item_name: on_click_callback(item_idx, name),
                img=imgfile_item
            )
        else:
            btn = Button(
                x + i * 50, y, 
                70, 200,
                func=lambda item_idx=i, name=item_name: on_click_callback(item_idx, name),
                on_hover=lambda btn: btn.translate(btn.rect.x, y - 120, time=200), 
                off_hover=lambda btn: btn.translate(btn.rect.x, y, time=200),
                img=imgfile_item
            )
        file = pygame.transform.scale(assets.get_image("items",item_name),(70,70))
        btn.set_overlay_image(file,30,30)
        new_panels.append(btn)
        
    items_menu.panels = new_panels

def draw_enemies_panels(raw_data, on_click_callback):
    """
    Always called AFTER rebuild_enemy_items()
    """
    if not raw_data: 
        return
    items_list = raw_data.split(";")
    new_panels = []
    for i, item_name in enumerate(items_list):
        # Передаем в callback-функцию индекс предмета и его имя
        btn = Button(
            600+i * 50, 120, 
            100, 400,
            func=lambda item_idx=i, name=item_name: on_click_callback(item_idx),
            img=imgfile_blank,
            #debug_draw_hbox = True
        )
        file = pygame.transform.scale(assets.get_image("enemies",item_name),(700,700))
        btn.set_overlay_image(file,-600,-300)
        new_panels.append(btn)
        
    items_menu.panels.extend(new_panels)


def close_items_menu(dummy=None):
    image_malex.translate(0, 0, time=500)
    items_menu.enabled = False
    image_malex.animation = 0

def drop_buttons(item_idx, name):
    open_player_inventory(keep_idx=item_idx)
    text = ui_font.render(name, True, (0, 0, 0))
    des_y = 70 + item_idx*50
    btn1 = Button(220, des_y, text=f"Осмотреть", func=lambda: action_inspect(item_idx, name))
    btn2 = Button(220, des_y, text=f"Использовать", func=lambda: action_use_item(item_idx, name))
    btn3 = Button(220, des_y, text=f"Выбросить", func=lambda: action_drop_item(item_idx, name))

    btn1.translate(320,des_y,200)
    btn2.translate(520,des_y,200)
    btn3.translate(720,des_y,200)
    items_menu.panels.extend([btn1,btn2,btn3])
    

def battle_drop_buttons(item_idx, name):
    battle_player_inventory(keep_idx=item_idx)
    btn = Button(280, 70 + item_idx*50, text=f"Использовать", func=lambda: battle_use_item(item_idx, name))
    btn2 = Button(480, 70 + item_idx*50, text=f"Осмотреть", func=lambda: action_inspect(item_idx, name))
    items_menu.panels.append(btn)
    items_menu.panels.append(btn2)

    

def open_room_items():
    items_menu.enabled = True
    room_data = novel.handle("checkroom_internal")["text"]
    room_data2 = novel.handle("start_combat","hey")["text"]
    # Строим меню предметов комнаты, при клике сработает подбор
    image_malex.translate(100, 0, time=200)
    
    horizontal_items_menu(room_data, action_pick_up, inv_img=False)
    draw_enemies_panels(room_data2, action_start_combat)
###################### МОЛЕКС ТУТ БЛЯТЬ ФУНКЦИЯ АТАКИ

def open_player_weapons():
    reset_battle_panels()
    #items_menu.enabled = True
    raw_data = novel.handle("get_weapons")["text"]
    items_list = raw_data.split(";")
    btns = []
    for i, item_name in enumerate(items_list):
        # Передаем в callback-функцию индекс предмета и его имя
        btn = Button(
            220, point-offset + i * -50, 
            text=item_name, 
            func=lambda item_idx=i, name=item_name: fight(item_idx, name)
        )
        btns.append(btn)
    btn_array.array = btns
    btn_array.enabled = True
    print("Оружия???? Зачем тебе оружия, бака!! Ты кого убить там собрался???????? Н-но, держи, будь аккуратнее, с-семпай...") # why are you so tsundere

def open_mercy_buttons():
    reset_battle_panels()
    btn_spare = Button(
            220, point+offset*3,  #420
            text="Пощадить", 
            func=lambda : spare()
        )
    btn_run = Button(
            220, point+offset*3,  #620
            text="Сбежать", 
            func=lambda : run()
        )
    btn_spare.translate(420,btn_spare.rect.y,200)
    btn_run.translate(620,btn_run.rect.y,200)
    battle.panels.append(btn_spare)
    battle.panels.append(btn_run)


def battle_player_inventory(keep_idx=None):
    reset_battle_panels()
    items_menu.enabled = True
    inv_data = novel.handle("inv_internal")["text"]
    print("ЧТО?? Уже и зелья собрался пить?? Ты настолько глупый что уже потерял столько ХП???? ХАХА, н-но вот смотри твой инвентарь, используй что хочешь..") # why are you so tsundere
    # Строим меню инвентаря, при клике сработает использование/осмотр
    rebuild_items_menu(inv_data, battle_drop_buttons,keep_idx)

def open_player_inventory(keep_idx=None):
    items_menu.enabled = True
    inv_data = novel.handle("inv_internal")["text"]
    print("ХМПФ!! ты хочешь чтобы я открыла для тебя инвентарь??? ну уж нет!! не надейся даже! н-но, если что он открылся.. н-наверное....") # why are you so tsundere
    # Строим меню инвентаря, при клике сработает использование/осмотр
    rebuild_items_menu(inv_data, drop_buttons, keep_idx) #,inv_img=False

def reset_battle_panels():
    battle.panels = [btn_hit, input_field, btn_item, btn_mercy, btn_array]
    btn_array.enabled = False
    input_field.text = ""

def run(item_idx=None, name=None):
    reset_battle_panels()
    def fetch_ai_response():
        global is_loading
        
        try:
            hp = novel.player.gethp()
            is_loading = True
            battle.enabled = False
            
            res = novel.handle("fight_run")
            # Передаем текст в принтер (это безопасно делать из потока)
            display_text.set_text(res["text"])
            if novel.player.gethp() < hp:
                image_malex.short_animation(1,300)
                image_malex.shake()
        except Exception as e:
            display_text.set_text(f"Ошибка связи с ИИ: {e}")
        finally:
            # Выключаем режим загрузки, когда поток завершил работу
            is_loading = False
            battle.enabled = True
    is_loading = True
    display_text.set_text(f"Ты попытался сбежать, но это безуспешно... \n Ждём ответа...")
    threading.Thread(target=fetch_ai_response, daemon=True).start() 

def spare(item_idx=None, name=None):
    reset_battle_panels()
    def fetch_ai_response():
        global is_loading
        
        try:
            is_loading = True
            battle.enabled = False
            hp = novel.player.gethp()
            res = novel.handle("fight_spare")
            # Передаем текст в принтер (это безопасно делать из потока)
            display_text.set_text(res["text"])
            if novel.player.gethp() < hp:
                image_malex.short_animation(1,300)
                image_malex.shake()
        except Exception as e:
            display_text.set_text(f"Ошибка связи с ИИ: {e}")
        finally:
            # Выключаем режим загрузки, когда поток завершил работу
            is_loading = False
            battle.enabled = True
    is_loading = True
    display_text.set_text(f"Ты попытался пощадить врага... \n Ждём ответа...")
    threading.Thread(target=fetch_ai_response, daemon=True).start()

def battle_use_item(item_idx=None, name=None):
    reset_battle_panels()
    close_items_menu()
    def fetch_ai_response():
        global is_loading
        
        try:
            hp = novel.player.gethp()
            is_loading = True
            battle.enabled = False
            res = novel.handle("fight_usepotion", payload=item_idx)
            # Передаем текст в принтер (это безопасно делать из потока)
            display_text.set_text(res["text"])
            if novel.player.gethp() < hp:
                image_malex.short_animation(1,300)
                image_malex.shake()
        except Exception as e:
            display_text.set_text(f"Ошибка связи с ИИ: {e}")
        finally:
            # Выключаем режим загрузки, когда поток завершил работу
            is_loading = False
            battle.enabled = True
            
    is_loading = True
    display_text.set_text(f"Ты попытался использовать предмет... \n Ждём ответа...")
    threading.Thread(target=fetch_ai_response, daemon=True).start()
weapon_img = Image(1000, 0, pygame.image.load(f'assets/images/sprites/main.png'))
weapon_img.enabled = False
def fight(item_idx=None, name=None, text=""):
    reset_battle_panels()
    global weapon_img
    try:
        if item_idx != None:
            file = assets.get_image("items",novel.handle("get_weapon_id",item_idx)["text"])
            weapon_img = Image(300-file.get_width()//2, 270-file.get_height()//2, file) # факэсс я не могу придумать как это реализовать нормально пусть пока так
        else:
            weapon_img = Image(1000, 0, pygame.image.load(f'assets/images/sprites/main.png'))
    except:
        pass
    def fetch_ai_response():
        global is_loading
        image_malex.animation = 3
        try:
            hp = novel.player.gethp()
            is_loading = True
            battle.enabled = False
            weapon_img.enabled = True
            # Тяжелый запрос к серверу (твой novel.handle внутри делает запрос к LLM)
            if(text == "" and item_idx != None):
                res = novel.handle("fight_attack", payload=item_idx)
            else:
                res = novel.handle("fight_talk", payload=text)
            # Передаем текст в принтер (это безопасно делать из потока)
            display_text.set_text(res["text"])
            image_malex.animation = 0
            weapon_img.enabled = False
            if novel.player.gethp() < hp:
                image_malex.short_animation(1,300)
                image_malex.shake()
        except Exception as e:
            display_text.set_text(f"Ошибка связи с ИИ: {e}")
        finally:
            # Выключаем режим загрузки, когда поток завершил работу
            is_loading = False
            battle.enabled = True
    is_loading = True
    display_text.set_text(f"Ты атаковал {novel.current_enemy.name} оружием {name}! \n Ждём ответа...") if item_idx != None else display_text.set_text(f"Ты сказал {novel.current_enemy.name}: '{text}' \n Ждём ответа...")
    threading.Thread(target=fetch_ai_response, daemon=True).start() 

btn_n = Button(865, 257, 60, 55, text="Север", func=lambda : action_move("север"), img="no" ) #display_text.set_text(novel.handle("move","север")["text"])
btn_s = Button(865, 368, 60, 55, text="Юг", func=lambda : action_move("юг"), img="no" )
btn_e = Button(924, 312, 60, 55, text="Восток", func=lambda : action_move("восток"), img="no" )
btn_w = Button(812, 312, 60, 55, text="Запад", func=lambda : action_move("запад"), img="no" )

btn_inspect = Button(300, 700, text="", func=lambda : open_room_items(), img=imgfile_btn_inspect)
btn_attack = Button(500, 700, text="Атаковать", func=lambda : action_start_combat() ) ### Obsolete meat

btn_save = Button(900, 20, text="", func=lambda : display_text.set_text(novel.handle("save")["text"]), img=imgfile_btn_save)

btn_inv = Button(500, 700, text="", func=lambda : open_player_inventory(), img=imgfile_btn_inv)

btn_map = Button(700, 700, text="", func=lambda: setattr(map_menu, 'enabled', True), img=imgfile_btn_map)

freeroam = Menu([btn_n,btn_s,btn_e,btn_w, btn_inspect, btn_inv, btn_save, btn_map, image_ui_cross])

# Вместо подмены текста на лету внутри отрисовки, сделайте явные кнопки для боя:
point=200
offset = 80
btn_hit = Button(220, point, text="", func=lambda: open_player_weapons(), img=imgfile_btn_attack)
input_field = TextInputField(220, point + offset, 183, 60, font=ui_font, max_chars=2000, on_submit=lambda x: fight(text=x), img=imgfile_btn_act)
btn_item = Button(220, point + offset*2, text="", func=lambda: battle_player_inventory(), img=imgfile_btn_item)
btn_mercy = Button(220, point + offset*3, text="", func=lambda: open_mercy_buttons(), img=imgfile_btn_mercy)
btn_array = SelectableButton(220, point-offset, 50, 60, [])
btn_array.enabled = False



battle = Menu([btn_hit, input_field, btn_item, btn_mercy, btn_array])

btn_close_items = Button(700, 20, text="", func=lambda: close_items_menu(), img=imgfile_close)
# Создаем окно скролла шириной 500px и высотой 300px в координатах (60, 40)
inv_scroll_list = ScrollList(x=60, y=40, width=150, height=100, item_height=50)

imgfile_item = pygame.image.load('assets/images/UI/item.png').convert_alpha()

items_menu = Menu([btn_close_items,inv_scroll_list]) 
items_menu.enabled = False

ingame_map = VisualMap(x=200, y=150, w=600, h=400, img = imgfile_map)
btn_close_map = Button(20, 20, text="", func=lambda: setattr(map_menu, 'enabled', False), img=imgfile_close)
map_menu = Menu([ingame_map,btn_close_map])
map_menu.enabled = False

btn_spec = Button(120, 700, text="", func=lambda: action_special(), img=imgfile_proceed)
intro_menu = Menu([btn_spec])


#def toggle_items(payload=novel.handle("checkroom_internal")["text"]):
#    items_menu.enabled = not items_menu.enabled
#    if items_menu.enabled:
#        rebuild_items_menu(payload) # Строим меню только при открытии
#    return payload

current_scene = "menu"

def reset_afk():
    global yo
    yo = False
    global start_time
    start_time = pygame.time.get_ticks()



yo = True
text_surface = dialog_font.render(display_text.get_text(), True, black, wraplength=700) 

# Скрываем стандартный системный курсор
pygame.mouse.set_visible(False)
while True:
    mouse_pos = pygame.mouse.get_pos()
    clock.tick(60) # Ограничиваем FPS, чтобы проц не умирал
    #тут херня с обновлением кадров анимации
    
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sus.exit()
            
        if current_scene == "menu":
            menu_main.any_event(event)
        # ОБРАБОТКА КЛИКОВ МЫШКИ
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

            if current_scene == "intro":
                intro_menu.click(mouse_pos)

            # КЛИКИ ВНУТРИ ИГРЫ (Связь с бэкендом)
            elif current_scene == "game":
                if(items_menu.enabled):
                    items_menu.click(mouse_pos)
                elif(map_menu.enabled):
                    map_menu.click(mouse_pos)
                else:
                    
                    # Если мы в обычном режиме исследования
                    if novel.state == "EXPLORING":
                        freeroam.click(mouse_pos)
                        if btn_spec.enabled and btn_spec.rect.collidepoint(mouse_pos):
                            btn_spec.func()

                    
        # ОБРАБОТКА КЛАВИАТУРЫ (для текстового ввода в бою)
        if items_menu.enabled:
            items_menu.any_event(event)
        if novel.state == "COMBAT":
            battle.any_event(event)
            #if items_menu.enabled:  ### OBSOLETE: uncomment this shit if you are using new rebuild items menu (with scroll things)
            #    items_menu.any_event(event)

    # --- ОТРИСОВКА ЭКРАНОВ ---
    if current_scene == "menu":
        
        screen.blit(imgfile_bg_menu, (0, 0))
        screen.blit(imgfile_gamename, (0, 0))
        menu_main.draw(screen)
        
    elif current_scene == "intro":
        screen.fill((0, 0, 0))
        display_text.update()
        
        # ОПТИМИЗАЦИЯ: Рендерим текст ТОЛЬКО если строка изменилась
        if last_text_string != display_text.get_text():
            last_text_string = display_text.get_text()
            text_surface = dialog_font.render(display_text.get_text(), True, black, wraplength=700) 
        
        image_bg.draw(screen)
        image_malex.draw(screen)
        btn_spec.enabled = True
        screen.blit(imgfile_textbox, (-10,30)) # Рисуем текстуру плашки поверх
        intro_menu.draw(screen)
        screen.blit(text_surface, (120, 560))  
        if "intro" not in novel.player.location:
            current_scene = "game"
            
    elif current_scene == "game":
        #if yo == False:
        #    elapsed_time = pygame.time.get_ticks() - start_time
        #    #print(elapsed_time)
        #    if elapsed_time >= 60000: 
        #        display_text.set_text("Йоу?")
        #        yo = True
        screen.fill((0, 0, 0))
        display_text.update()
        
        image_bg.draw(screen)
        
        # Рисуем Спрайты персонажей
        image_malex.draw(screen)

        if novel.state == "COMBAT":
            screen.blit(cur_enemy_imgfile, (20, 30)) if cur_enemy_imgfile else ""
        # --- ДИНАМИЧЕСКИЙ ТЕКСТ ИЗ ДВИЖКА ---

        screen.blit(imgfile_textbox, (- 10, 30)) # Рисуем текстуру плашки поверх
        # Рендерим текущий текст, полученный из novel.handle()
        # ОПТИМИЗАЦИЯ: Рендерим текст ТОЛЬКО если строка изменилась
        if last_text_string != display_text.get_text():
            last_text_string = display_text.get_text()
            text_surface = dialog_font.render(display_text.get_text(), True, black, wraplength=700)
        #text_surface = dialog_font.render(display_text.get_text(), True, black, wraplength=700) 
        screen.blit(text_surface, (120, 560))
        
        # --- ИНТЕРФЕЙС И КНОПКИ ДЕЙСТВИЙ ---
        # Выводим ХП игрока сверху
        hp_text = names_font.render(f"Малекс HP: {novel.player.gethp()}", True, black)
        screen.blit(hp_text, (30, 145))
        
        # Рисуем кнопки в зависимости от состояния движка (EXPLORING или COMBAT)
        if novel.state == "EXPLORING":
            freeroam.draw(screen)
            if "spec" in novel.get_player_location().special_flags.keys():
                btn_spec.draw(screen)
                btn_spec.enabled = True
            else: 
                btn_spec.enabled = False
            
        elif novel.state == "COMBAT":
            battle.draw(screen)
            weapon_img.draw(screen)
            # Показываем ХП врага, если идет бой
            if novel.current_enemy:
                enemy_hp_text = names_font.render(f"{novel.current_enemy.name} HP: {novel.current_enemy.gethp()}", True, dred)
                screen.blit(enemy_hp_text, (720, 120))
        if items_menu.enabled:
            items_menu.draw(screen)
        if map_menu.enabled:
            map_menu.draw(screen)
        if "intro" in novel.player.location:
            current_scene = "intro"

    screen.blit(cursor_img, pygame.mouse.get_pos())

    pygame.display.flip()
    