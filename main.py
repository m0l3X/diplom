import pygame
import sys as sus
#import websearch
from rpnovel_engine import RPGNovel 
#import io
#import base64
import random
import threading
pygame.init()

btn = pygame.image.load('assets/images/UI/buttonmini.png')
class Button:
    def __init__(self, x, y, w=None, h=None, text="", img=None, func=lambda: print("hi i'm button")):
        # Если img не передан, используем дефолтный (предполагается, что дефолтный btn загружен глобально)
        self.orig_img = img if img else btn 
        self.img = self.orig_img
        
        # Задаем размеры rect
        width = w if w else self.img.get_width()
        height = h if h else self.img.get_height()
        self.rect = pygame.Rect(x, y, width, height)
        
        # Анимация текста внутри кнопки
        self.text_manager = PygameTextPrinter(speed_ms=50)
        self.text_manager.set_text(text)
        
        self.last_text = ""
        self.text_surf = None
        
        # Таймеры для визуальных эффектов (поворот)
        self.last_update = 0
        self.speed = 333
        
        self.enabled = True
        self.func = func

    def draw(self, surf):
        if not self.enabled:
            return  # Просто не рисуем и не обновляем, если кнопка выключена
            
        current_time = pygame.time.get_ticks()
        
        # Эффект покачивания (поворот оригинальной картинки, без накопления искажений)
        if current_time - self.last_update >= self.speed:
            r = random.randint(-3, 3)
            self.img = pygame.transform.rotate(self.orig_img, r*2)
            self.last_update = current_time
            
        # Центрирование картинки кнопки относительно её rect
        img_w, img_h = self.img.get_width(), self.img.get_height()
        pos = (self.rect.x + self.rect.width // 2 - img_w // 2, 
               self.rect.y + self.rect.height // 2 - img_h // 2)
        
        surf.blit(self.img, pos)
        
        # Обновляем состояние печатного текста
        self.text_manager.update()
        current_text_string = self.text_manager.get_text()
        
        # ОПТИМИЗАЦИЯ: Рендерим текст ТОЛЬКО если строка изменилась
        if current_text_string != self.last_text or self.text_surf is None:
            self.last_text = current_text_string
            self.text_surf = ui_font.render(current_text_string, True, (0, 0, 0))
            
        # Отрисовка текста по центру кнопки (или с фиксированным отступом)
        surf.blit(self.text_surf, (self.rect.x + 45, self.rect.y + 8))

class Image:
    def __init__(self, x, y, img):
        self.img = img
        self.rect = pygame.Rect(x, y, img.get_width(), img.get_height())
    def draw(self, surf):
        surf.blit(self.img, (self.rect.x, self.rect.y))

class Menu:
    def __init__(self, buttons):
        self.panels = buttons
        self.enabled = True

    def draw(self, surf):
        for item in self.panels:
            if isinstance(item, Button):
                item.draw(surf)
            else:
                item.draw(surf)

    def click(self, mouse_pos):
        for btn in self.panels:
            if isinstance(btn, Button):
                # Проверяем активность кнопки ДО проверки коллизии
                if btn.enabled and btn.rect.collidepoint(mouse_pos):
                    btn.func()
                    return True # Возвращаем True, если клик успешно обработан
        return False


class PygameTextPrinter:
    def __init__(self, speed_ms=30):
        self.full_text = ""      # Весь текст, который нужно вывести
        self.current_text = ""   # Текст, который виден сейчас на экране
        self.char_index = 0      # На какой мы сейчас букве
        self.speed = speed_ms    # Скорость появления букв (в миллисекундах)
        self.last_update = 0     # Время последнего добавления буквы
        self.is_running = False  # Печатается ли текст прямо сейчас

    def set_text(self, text):
        """Загружает новый текст для анимации"""
        self.full_text = text
        self.current_text = ""
        self.char_index = 0
        self.last_update = pygame.time.get_ticks()
        self.is_running = True

    def update(self):
        """Метод обновляет строку. Должен вызываться КАЖДЫЙ кадр игры"""
        if not self.is_running:
            return

        # Проверяем, зажат ли Пробел для пропуска анимации (аналог твоего skip)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            self.current_text = self.full_text
            self.char_index = len(self.full_text)
            self.is_running = False
            return

        # Проверяем, прошло ли достаточно времени с последней буквы
        current_time = pygame.time.get_ticks()
        if current_time - self.last_update >= self.speed:
            if self.char_index < len(self.full_text):
                self.current_text += self.full_text[self.char_index]
                self.char_index += 1
                self.last_update = current_time
            else:
                self.is_running = False

    def get_text(self):
        return self.current_text


novel = RPGNovel("Mallex") 

current_room_desc, player_hp, player_inv = novel.get_player_location()
display_text = PygameTextPrinter(speed_ms=25)
display_text.set_text(current_room_desc)

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
nemo_image = pygame.image.load('assets/images/sprites/nemo.png')
background_image = pygame.image.load('assets/images/fon.png')
background_menu = pygame.image.load('assets/images/UI/menu_fon.png')
text_box_image = pygame.image.load('assets/images/UI/button.png')

button_play = pygame.image.load('assets/images/UI/play.png') 
button_playh = pygame.image.load('assets/images/UI/play1.png')

button_x, button_y = 0, 20
click_zone = pygame.Rect(350, 340, 300, 100)

# Зоны для кликов в самой игре (Кнопки действий)
# Формат: pygame.Rect(X, Y, ШИРИНА, ВЫСОТА)

#херня с анимацией ..dunno если честно куда ее вставить. так что пусть сюда.. ):
#тут загружаются кадрі анимации
malex_anim = [
    pygame.image.load('assets/images/sprites/Pmalex.png'),
    pygame.image.load('assets/images/sprites/Pmalex01.png'),
]
# переменніе для управления таймингом анимации
current_frame = 0 # индекс текущего кадра
last_update = pygame.time.get_ticks() # єто таймер для отслеживания времени между кадрами
animation_speed = 600  # скорость смені кадров в миллисекундах


btn_n = Button(100, 700, text="Север", func=lambda : display_text.set_text(novel.handle("move","север")["text"]) )
btn_s = Button(100, 660, text="Юг", func=lambda : display_text.set_text(novel.handle("move","юг")["text"]) )
btn_e = Button(100, 620, text="Восток", func=lambda : display_text.set_text(novel.handle("move","восток")["text"]) )
btn_w = Button(100, 580, text="Запад", func=lambda : display_text.set_text(novel.handle("move","запад")["text"]) )

btn_inspect = Button(300, 700, text="Осмотреться", func=lambda : open_room_items())
btn_attack = Button(500, 700, text="Атаковать", func=lambda : display_text.set_text(novel.handle("start_combat", "1")["text"]) )

btn_inv = Button(700, 700, text="Инвентарь", func=lambda : open_player_inventory())

freeroam = Menu([btn_n,btn_s,btn_e,btn_w, btn_inspect, btn_attack, btn_inv])

# Вместо подмены текста на лету внутри отрисовки, сделайте явные кнопки для боя:
btn_run = Button(100, 700, text="Сбежать", func=lambda: display_text.set_text(novel.handle("fight_run")["text"]))
btn_hit = Button(500, 700, text="Ударить", func=lambda: fight())

battle = Menu([btn_run, btn_hit])

items_menu = Menu([text_box_image]) 
items_menu.enabled = False

# Действие 1: Подобрать предмет из комнаты
def action_pick_up(item_index, item_name):
    res = novel.handle("take", str(item_index + 1))
    display_text.set_text(res["text"])
    
    # Обновляем это же меню, заново запросив шмот из комнаты
    room_data = novel.handle("checkroom_internal")["text"]
    rebuild_items_menu(room_data, action_pick_up)

def action_inspect(item_index, item_name):
    res = novel.handle("inspect", str(item_index + 1)) 
    display_text.set_text(res["text"])
    
    # Закрываем инвентарь после использования (или обновляем, если предмет исчезает)
    close_items_menu()


# Действие 2: Использовать/осмотреть предмет из личного инвентаря
def action_use_item(item_index, item_name):
    # Предположим, у тебя на бэкенде есть команда "use" или "inspect"
    res = novel.handle("usepotion", str(item_index + 1)) 
    display_text.set_text(res["text"])
    
    # Закрываем инвентарь после использования (или обновляем, если предмет исчезает)
    close_items_menu()

def rebuild_items_menu(raw_data, on_click_callback):
    """
    Принимает строку с предметами через ';' и функцию, 
    которая должна выполниться при клике на элемент.
    """
    if not raw_data: 
        items_menu.panels = [
            Image(0, 0, text_box_image), 
            Button(20, 20, text="Пусто", func=lambda: close_items_menu())
        ]
        return

    items_list = raw_data.split(";")
    new_panels = [Image(0, 0, text_box_image)]
    
    for i, item_name in enumerate(items_list):
        # Передаем в callback-функцию индекс предмета и его имя
        btn = Button(
            20, 20 + i * 50, 
            text=item_name, 
            func=lambda item_idx=i, name=item_name: on_click_callback(item_idx, name)
        )
        new_panels.append(btn)
        
    items_menu.panels = new_panels

def close_items_menu(dummy=None):
    items_menu.enabled = False

def drop_buttons(item_idx, name):
    open_player_inventory()
    items_menu.panels.append(Button(220, 20 + item_idx*50, text=f"Осмотреть {name}", func=lambda: action_inspect(item_idx, name)))
    items_menu.panels.append(Button(420, 20 + item_idx*50, text=f"Использовать {name}", func=lambda: action_use_item(item_idx, name)))


def open_room_items():
    items_menu.enabled = True
    room_data = novel.handle("checkroom_internal")["text"]
    # Строим меню предметов комнаты, при клике сработает подбор
    rebuild_items_menu(room_data, action_pick_up)

def open_player_inventory():
    items_menu.enabled = True
    inv_data = novel.handle("inv_internal")["text"]
    print("ХМПФ!! ты хочешь чтобы я открыла для тебя инвентарь??? ну уж нет!! не надейся даже! н-но, если что он открылся.. н-наверное....") # why are you so tsundere
    # Строим меню инвентаря, при клике сработает использование/осмотр
    rebuild_items_menu(inv_data, drop_buttons)

#def toggle_items(payload=novel.handle("checkroom_internal")["text"]):
#    items_menu.enabled = not items_menu.enabled
#    if items_menu.enabled:
#        rebuild_items_menu(payload) # Строим меню только при открытии
#    return payload

current_scene = "menu"
weight, height = 1000, 800
screen = pygame.display.set_mode((weight, height))
pygame.display.set_caption('Gay')

clock = pygame.time.Clock()

def fight():
    def fetch_ai_response():
        global is_loading
        
        try:
            is_loading = True
            btn_attack.enabled = False
            btn_run.enabled = False
            # Тяжелый запрос к серверу (твой novel.handle внутри делает запрос к LLM)
            res = novel.handle("fight_attack", payload=novel.player.inventory[0])
            # Передаем текст в принтер (это безопасно делать из потока)
            display_text.set_text(res["text"])
        except Exception as e:
            display_text.set_text(f"Ошибка связи с ИИ: {e}")
        finally:
            # Выключаем режим загрузки, когда поток завершил работу
            is_loading = False
            btn_attack.enabled = True
            btn_run.enabled = True
    is_loading = True
    display_text.set_text(f"{novel.current_enemy.name} думает...")
    threading.Thread(target=fetch_ai_response, daemon=True).start() 

while True:
    mouse_pos = pygame.mouse.get_pos()
    clock.tick(60) # Ограничиваем FPS, чтобы проц не умирал
    
    #тут херня с обновлением кадров анимации
    now = pygame.time.get_ticks()
    if now - last_update > animation_speed:
        current_frame = (current_frame + 1) % len(malex_anim) # Переходим к следующему кадру
        last_update = now
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sus.exit()
            
        # ОБРАБОТКА КЛИКОВ МЫШКИ
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            
            # Клик в Главном Меню
            if current_scene == "menu":
                if click_zone.collidepoint(mouse_pos):
                    res = novel.handle("load") # Получаем описание локации при входе в игру
                    display_text.set_text(res["text"])
                    current_scene = "game"
                    
                    
            # КЛИКИ ВНУТРИ ИГРЫ (Связь с бэкендом)
            elif current_scene == "game":
                if(items_menu.enabled):
                    items_menu.click(mouse_pos)
                else:
                    
                    # Если мы в обычном режиме исследования
                    if novel.state == "EXPLORING":
                        freeroam.click(mouse_pos)
                        

                    # Если движок переключился в режим боя
                    elif novel.state == "COMBAT":
                        battle.click(mouse_pos)

    # --- ОТРИСОВКА ЭКРАНОВ ---
    if current_scene == "menu":
        screen.blit(background_menu, (0, 0))
        if click_zone.collidepoint(mouse_pos):
            screen.blit(button_playh, (button_x, button_y)) 
        else:
            screen.blit(button_play, (button_x, button_y))  
            
    elif current_scene == "game":
        screen.fill((0, 0, 0))
        display_text.update()
        # Рисуем фон локации
        screen.blit(background_image, (0.5 * weight - background_image.get_width() // 2, 0.5 * height - background_image.get_height() // 2 ))
        
        # Рисуем Спрайты персонажей
        screen.blit(malex_anim[current_frame], (0.5 * weight - malex_anim[current_frame].get_width() // 2, 0.5 * height - malex_anim[current_frame].get_height() // 2 + 30))

        if novel.state == "COMBAT":
            screen.blit(nemo_image, (0.5 * weight - nemo_image.get_width() // 2 + 20, 0.5 * height - nemo_image.get_height() // 2 + 30))
        # --- ДИНАМИЧЕСКИЙ ТЕКСТ ИЗ ДВИЖКА ---

        screen.blit(text_box_image, (0.5 * weight - text_box_image.get_width() // 2 - 10, 0.5 * height - text_box_image.get_height() // 2 + 30)) # Рисуем текстуру плашки поверх
        # Рендерим текущий текст, полученный из novel.handle()
        text_surface = dialog_font.render(display_text.get_text(), True, black, wraplength=700) 
        screen.blit(text_surface, (120, 560))
        
        # --- ИНТЕРФЕЙС И КНОПКИ ДЕЙСТВИЙ ---
        # Выводим ХП игрока сверху
        hp_text = names_font.render(f"Малекс HP: {novel.player.gethp()}", True, black)
        screen.blit(hp_text, (30, 145))
        
        # Рисуем кнопки в зависимости от состояния движка (EXPLORING или COMBAT)
        if novel.state == "EXPLORING":
            freeroam.draw(screen)
            
        elif novel.state == "COMBAT":
            battle.draw(screen)
            # Показываем ХП врага, если идет бой
            if novel.current_enemy:
                enemy_hp_text = names_font.render(f"{novel.current_enemy.name} HP: {novel.current_enemy.gethp()}", True, dred)
                screen.blit(enemy_hp_text, (780, 160))
        if items_menu.enabled:
            items_menu.draw(screen)

    pygame.display.flip()