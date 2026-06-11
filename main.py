import pygame
import sys as sus
#import websearch
from rpnovel_engine import RPGNovel 
import os
#import base64
import random
import threading
pygame.init()

btn = pygame.image.load('assets/images/UI/buttonmini.png')
class Button:
    def __init__(self, x, y, w=None, h=None, text="", img=None, func=lambda: print("hi i'm button")):
        # Если img не передан, используем дефолтный (предполагается, что дефолтный btn загружен глобально)
        if img != "no":
            self.orig_img = img if img else btn 
            self.img = self.orig_img
        else:
            self.orig_img = None
            self.img = None
        
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
        if not self.enabled or self.img is None:
            return  # Просто не рисуем и не обновляем, если кнопка выключена
            
        current_time = pygame.time.get_ticks()
        
        # Эффект покачивания (поворот оригинальной картинки, без накопления искажений)
        if current_time - self.last_update >= self.speed:
            r = random.randint(-2, 2)
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
        surf.blit(self.text_surf, (self.rect.x + 25, self.rect.y + 15))

class Image:
    def __init__(self, x, y, img, animations=None, animation_speed=500,anim=False):
        self.img = img
        self.rect = pygame.Rect(x, y, img.get_width(), img.get_height())
        self.animations = animations
        self.animation = 0
        self.animation_speed = animation_speed
        self.anim = anim
        self.current_frame = 0
        self.last_update = 0

    def draw(self, surf):
        if not self.anim:
            surf.blit(self.img, (self.rect.x, self.rect.y))
        else:
            self.animation_frames = self.animations[self.animation]
            now = pygame.time.get_ticks()
            if now - self.last_update > self.animation_speed:
                self.current_frame = (self.current_frame + 1) % len(self.animation_frames) # Переходим к следующему кадру
                self.last_update = now
            surf.blit(self.animation_frames[self.current_frame], (self.rect.x, self.rect.y))
            
    def translate(self, newx, newy, time=500):
        def lerp(a: float, b: float, t: float) -> float: # larping in python 😭
            return (1 - t) * a + t * b
        def smoothstep(a: float, b: float, t: float) -> float:
            # Clamp t between 0 and 1
            t = max(0.0, min(1.0, t))
            # Apply S-curve formula: 3t^2 - 2t^3
            t = t * t * (3.0 - 2.0 * t)
            return a + t * (b - a)
        def animate():
            start_time = pygame.time.get_ticks()
            start_x, start_y = self.rect.x, self.rect.y
            while True:
                now = pygame.time.get_ticks()
                elapsed = now - start_time
                if elapsed >= time:
                    self.rect.x, self.rect.y = newx, newy
                    break
                else:
                    t = elapsed / time
                    self.rect.x = int(smoothstep(start_x, (newx), t))
                    self.rect.y = int(smoothstep(start_y , (newy), t))
        threading.Thread(target=animate, daemon=True).start()

        

class Menu:
    def __init__(self, buttons):
        self.panels = buttons
        self.enabled = True

    def draw(self, surf):
        if not self.enabled: return
        for item in self.panels:
            if isinstance(item, Button):
                item.draw(surf)
            if isinstance(item, VisualMap):
                item.draw(surf, novel.player)
            else:
                item.draw(surf)

    def click(self, mouse_pos):
        if not self.enabled: return
        for btn in self.panels:
            if isinstance(btn, Button):
                # Проверяем активность кнопки ДО проверки коллизии
                if btn.enabled and btn.rect.collidepoint(mouse_pos):
                    btn.func()
                    return True # Возвращаем True, если клик успешно обработан
            #if isinstance(btn, TextInputField):
            #    if btn.enabled and btn.rect.collidepoint(mouse_pos):
            #        self.active = True
            #    else:
            #        self.active = False
            #        #btn.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'pos': mouse_pos, 'button': 1}))
            #        return True
        return False
    def any_event(self, event):
        if not self.enabled: return

        for btn in self.panels:
            if isinstance(btn, TextInputField):
                btn.handle_event(event)

class TextInputField:
    def __init__(self, x, y, w, h, font, text_color=(0, 0, 0), img=None, max_chars=50, on_submit=None):
        self.orig_img = img if img else btn 
        self.img = self.orig_img
        self.last_update = 0
        self.speed = 333
        self.rect = pygame.Rect(x, y, w, h)
        self.font = font
        self.text_color = text_color
        self.max_chars = max_chars
        self.on_submit = on_submit  # Функция, которая вызовется при нажатии Enter
        
        self.text = "Сказать..."              # Текущий введенный текст
        self.active = False         # Выбрано ли поле кликом мышки
        self.enabled = True         # Видимо/активно ли поле в текущей сцене
        
        # Для мигающего курсора
        self.cursor_visible = True
        self.last_cursor_toggle = pygame.time.get_ticks()
        self.cursor_speed = 500     # Интервал мигания (в мс)

    
        

    def handle_event(self, event):
        """Метод обрабатывает события ввода. Вызывать внутри for event in pygame.event.get()"""
        if not self.enabled:
            return

        # Проверяем клик мыши для активации фокуса
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.active = True
                self.text = "" if self.text == "Сказать..." else self.text
            else:
                self.active = False

        # Если поле «в фокусе», перехватываем клавиатуру
        if self.active and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                # Если нажали Enter и текст не пустой — отправляем данные в callback
                if self.text.strip() and self.on_submit:
                    self.on_submit(self.text)
                    self.text = ""  # Очищаем поле после отправки
            elif event.key == pygame.K_BACKSPACE:
                # Удаляем последний символ
                self.text = self.text[:-1]
            else:
                # Добавляем символ, если не превышен лимит
                if len(self.text) < self.max_chars:
                    # event.unicode содержит символ с учетом раскладки и Shift
                    if event.unicode.isprintable() and event.unicode != "":
                        self.text += event.unicode

    def draw(self, surf):
        """Отрисовка поля. Вызывать в блоке отрисовки экрана"""
        if not self.enabled:
            return
        def cool_box(current_time):
            if current_time - self.last_update >= self.speed:
                r = random.randint(-2, 2)
                self.img = pygame.transform.rotate(self.orig_img, r*2)
                self.last_update = current_time
                
            # Центрирование картинки кнопки относительно её rect
            img_w, img_h = self.img.get_width(), self.img.get_height()
            pos = (self.rect.x + self.rect.width // 2 - img_w // 2, 
                self.rect.y + self.rect.height // 2 - img_h // 2)
            
            surf.blit(self.img, pos)
        # Меняем цвет рамки в зависимости от того, активен фокус или нет
        box_color = (34, 3, 4) if self.active else (150, 150, 150) # dred или серый
        
        # Рисуем подложку (белый прямоугольник) и рамку
        pygame.draw.rect(surf, (255, 255, 255), self.rect)
        pygame.draw.rect(surf, box_color, self.rect, 2) # Толщина рамки 2 пикселя

        current_time = pygame.time.get_ticks()

        # Рендерим текст
        text_surf = self.font.render(self.text, True, self.text_color)
        
        # Ограничиваем область отображения текста, чтобы он не вылезал за рамку поля
        # Если текст длиннее поля, сдвигаем его влево (показываем конец строки)
        text_width = text_surf.get_width()
        max_visible_width = self.rect.width - 20
        
        if text_width > max_visible_width:
            # Отрезаем кусок поверхности текста, который не влезает
            sub_rect = pygame.Rect(text_width - max_visible_width, 0, max_visible_width, self.rect.height)
            text_draw_surf = text_surf.subsurface(sub_rect)
            text_x = self.rect.x + 10
        else:
            text_draw_surf = text_surf
            text_x = self.rect.x + 10

        # Рисуем текст на экране
        text_y = self.rect.y + (self.rect.height // 2 - text_draw_surf.get_height() // 2)
        surf.blit(text_draw_surf, (text_x, text_y))

        # Логика мигания и отрисовки курсора (каретки)
        if current_time - self.last_cursor_toggle >= self.cursor_speed:
            self.cursor_visible = not self.cursor_visible
            self.last_cursor_toggle = current_time

        if self.active and self.cursor_visible:
            # Считаем координату X для палочки курсора
            cursor_x = text_x + min(text_width, max_visible_width) + 2
            cursor_y_start = text_y
            cursor_y_end = text_y + text_draw_surf.get_height()
            pygame.draw.line(surf, self.text_color, (cursor_x, cursor_y_start), (cursor_x, cursor_y_end), 2)

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

class VisualMap:
    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)
        self.enabled = True
        
        # Настройки отображения нод (комнат)
        self.node_radius = 20
        self.grid_size = 120  # Расстояние между комнатами в пикселях

    def draw(self, surf, player):
        if not self.enabled:
            return

        # 1. Рисуем подложку карты
        pygame.draw.rect(surf, (240, 230, 200), self.rect) # Песочный цвет
        pygame.draw.rect(surf, (100, 80, 60), self.rect, 3) # Рамка
        
        # Получаем сетку позиций комнат
        world = player.current_world
        positions = world.generate_map_positions(player.visited_locations)
        
        # Центр нашего окна карты на экране
        center_x = self.rect.x + self.rect.width // 2
        center_y = self.rect.y + self.rect.height // 2
        
        # Сдвиг всей карты, чтобы текущая комната игрока ВСЕГДА была по центру экрана
        player_grid_x, player_grid_y = positions.get(player.location, (0, 0))
        offset_x = center_x - player_grid_x * self.grid_size
        offset_y = center_y - player_grid_y * self.grid_size

        # Словарь для хранения экранных координат (нужен для отрисовки линий связи)
        screen_coords = {}
        for loc_id, (gx, gy) in positions.items():
            screen_coords[loc_id] = (offset_x + gx * self.grid_size, offset_y + gy * self.grid_size)

        # 2. ПЕРВЫЙ ПРОХОД: Рисуем линии связи (дороги) между комнатами
        for loc_id, coords in screen_coords.items():
            loc = world.get_location(loc_id)
            if loc_id not in player.visited_locations:
                continue # Скрываем дороги из неизведанных мест
                
            for direction, exit_id in loc.exits.items():
                if exit_id in screen_coords:
                    # Рисуем линию от текущей комнаты к соседней
                    pygame.draw.line(surf, (139, 69, 19), coords, screen_coords[exit_id], 4)

        # 3. ВТОРОЙ ПРОХОД: Рисуем сами кружочки комнат и текст
        for loc_id, coords in screen_coords.items():
            # Определяем цвет ноды
            if loc_id == player.location:
                color = (200, 50, 50)  # Красный — тут стоит Максон
            elif loc_id in player.visited_locations:
                color = (50, 150, 50)  # Зеленый — тут мы уже были
            else:
                color = (120, 120, 120) # Серый — туман войны (видим выход, но не были там)

            # Рисуем кружок локации
            pygame.draw.circle(surf, color, coords, self.node_radius)
            pygame.draw.circle(surf, (0, 0, 0), coords, self.node_radius, 2) # Обводка

            # Выводим название локации
            if loc_id in player.visited_locations:
                loc_name = world.get_location(loc_id).name
            else:
                loc_name = "???"

            # Рендер текста названия (используй свой шрифт, например ui_font)
            text_surf = ui_font.render(loc_name, True, (0, 0, 0))
            surf.blit(text_surf, (coords[0] - text_surf.get_width() // 2, coords[1] - self.node_radius - 20))


novel = RPGNovel("Mallex") 


display_text = PygameTextPrinter(speed_ms=25)
display_text.set_text("missingno")

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
bgs = {}
novel.handle("load")
for location in novel.player.current_world.locations:
    if os.path.exists(f'assets/images/locations/{location.id}.png'):
        bgs[location.id] = pygame.image.load(f'assets/images/locations/{location.id}.png')
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
malex_anim_static = [
    pygame.image.load('assets/images/sprites/Pmalex.png'),
    pygame.image.load('assets/images/sprites/Pmalex01.png'),
]
malex_fall = pygame.image.load('assets/images/sprites/Pmalexfall.png')
# переменніе для управления таймингом анимации

malex_img = Image(0, 0, malex_anim_static[0], animations=[malex_anim_static, [malex_fall,malex_fall]], animation_speed=600, anim=True)
bg_img = Image(0, 0, bgs[novel.player.location] if novel.player.location in bgs.keys() else background_image)


ui_cross = Image(0,0, pygame.image.load('assets/images/UI/cross.png'))

def action_move(direction):
    res = novel.handle("move", direction)
    special_flags = novel.get_player_location().special_flags
    malex_img.translate(special_flags["MX"], special_flags["MY"], time=300) if "MX" in special_flags.keys()  else malex_img.translate(0, 0, time=300)
    display_text.set_text(res["text"])

btn_n = Button(865, 257, 60, 55, text="Север", func=lambda : action_move("север"), img="no" ) #display_text.set_text(novel.handle("move","север")["text"])
btn_s = Button(865, 368, 60, 55, text="Юг", func=lambda : action_move("юг"), img="no" )
btn_e = Button(924, 312, 60, 55, text="Восток", func=lambda : action_move("восток"), img="no" )
btn_w = Button(812, 312, 60, 55, text="Запад", func=lambda : action_move("запад"), img="no" )

btn_inspect = Button(300, 700, text="Осмотреться", func=lambda : open_room_items())
btn_attack = Button(500, 700, text="Атаковать", func=lambda : display_text.set_text(novel.handle("start_combat", "1")["text"]) )

btn_save = Button(900, 20, text="Сохранить", func=lambda : display_text.set_text(novel.handle("save")["text"]) )

btn_inv = Button(700, 700, text="Инвентарь", func=lambda : open_player_inventory())

btn_map = Button(800, 700, text="Карта", func=lambda: setattr(map_menu, 'enabled', True))

freeroam = Menu([btn_n,btn_s,btn_e,btn_w, btn_inspect, btn_attack, btn_inv, btn_save, btn_map, ui_cross])

# Вместо подмены текста на лету внутри отрисовки, сделайте явные кнопки для боя:
btn_run = Button(100, 700, text="Сбежать", func=lambda: display_text.set_text(novel.handle("fight_run")["text"]))
btn_hit = Button(500, 700, text="Ударить", func=lambda: open_player_weapons())
input_field = TextInputField(300, 700, 200, 50, font=ui_font, max_chars=60, on_submit=lambda x: fight(text=x))

battle = Menu([btn_run, btn_hit, input_field])

btn_close_items = Button(700, 20, text="X", func=lambda: close_items_menu())
items_menu = Menu([text_box_image,btn_close_items]) 
items_menu.enabled = False

ingame_map = VisualMap(x=200, y=150, w=600, h=400)
btn_close_map = Button(20, 20, text="X", func=lambda: setattr(map_menu, 'enabled', False))
map_menu = Menu([ingame_map,btn_close_map])
map_menu.enabled = False

btn_spec = Button(120, 700, text="==>", func=lambda: action_special())
intro_menu = Menu([btn_spec])

def action_special():
    res = novel.handle("move", "spec")
    display_text.set_text(res["text"])
    special_flags = novel.get_player_location().special_flags
    bg_img.img = bgs[novel.player.location] if novel.player.location in bgs.keys() else background_image
    if "MX" in special_flags.keys():
        malex_img.translate(special_flags["MX"], special_flags["MY"], time=special_flags["MT"]) if "MT" in special_flags.keys()  else malex_img.translate(special_flags["MX"], special_flags["MY"], time=1000)
        
    malex_img.animation = special_flags["MANIM"] if "MANIM" in special_flags.keys() else 0
    bg_img.translate(special_flags["BGX"], special_flags["BGY"], time=1000) if "BGX" in special_flags.keys() else ""

# Действие 1: Подобрать предмет из комнаты
def action_pick_up(item_index, item_name):
    res = novel.handle("take", str(item_index))
    display_text.set_text(res["text"])
    
    close_items_menu()
    # Обновляем это же меню, заново запросив шмот из комнаты
    #room_data = novel.handle("checkroom_internal")["text"]
    #rebuild_items_menu(room_data, action_pick_up)

def action_inspect(item_index, item_name):
    res = novel.handle("inspect", str(item_index)) 
    display_text.set_text(res["text"])
    # Закрываем инвентарь после использования (или обновляем, если предмет исчезает)
    close_items_menu()

def action_drop_item(item_index, item_name):
    # Предположим, у тебя на бэкенде есть команда "use" или "inspect"
    res = novel.handle("drop", str(item_index )) 
    display_text.set_text(res["text"])
    
    # Закрываем инвентарь после использования (или обновляем, если предмет исчезает)
    close_items_menu()

# Действие 2: Использовать/осмотреть предмет из личного инвентаря
def action_use_item(item_index, item_name):
    # Предположим, у тебя на бэкенде есть команда "use" или "inspect"
    res = novel.handle("usepotion", str(item_index)) 
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
            Button(20, 20, text="Пусто", func=lambda: close_items_menu()),
            btn_close_items
        ]
        return

    items_list = raw_data.split(";")
    new_panels = [Image(0, 0, text_box_image),btn_close_items]
    
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
    malex_img.translate(0, 0, time=500)
    items_menu.enabled = False

def drop_buttons(item_idx, name):
    open_player_inventory()
    items_menu.panels.append(Button(220, 20 + item_idx*50, text=f"Осмотреть", func=lambda: action_inspect(item_idx, name)))
    items_menu.panels.append(Button(420, 20 + item_idx*50, text=f"Использовать", func=lambda: action_use_item(item_idx, name)))
    items_menu.panels.append(Button(620, 20 + item_idx*50, text=f"Выбросить", func=lambda: action_drop_item(item_idx, name)))


    

def open_room_items():
    items_menu.enabled = True
    room_data = novel.handle("checkroom_internal")["text"]
    # Строим меню предметов комнаты, при клике сработает подбор
    malex_img.translate(100, 0, time=200)

    rebuild_items_menu(room_data, action_pick_up)

###################### МОЛЕКС ТУТ БЛЯТЬ ФУНКЦИЯ АТАКИ

def open_player_weapons():
    battle.panels = [btn_run, btn_hit, input_field]
    #items_menu.enabled = True
    raw_data = novel.handle("get_weapons")["text"]
    items_list = raw_data.split(";")
    for i, item_name in enumerate(items_list):
        # Передаем в callback-функцию индекс предмета и его имя
        btn = Button(
            500, 650 + i * -50, 
            text=item_name, 
            func=lambda item_idx=i, name=item_name: fight(item_idx, name)
        )
        battle.panels.append(btn)
    
    print("Оружия???? Зачем тебе оружия, бака!! Ты кого убить там собрался???????? Н-но, держи, будь аккуратнее, с-семпай...") # why are you so tsundere
    

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

def fight(item_idx=None, name=None, text=""):
    battle.panels = [btn_run, btn_hit, input_field]
    def fetch_ai_response():
        global is_loading
        
        try:
            is_loading = True
            battle.enabled = False
            # Тяжелый запрос к серверу (твой novel.handle внутри делает запрос к LLM)
            if(text == "" and item_idx != None):
                res = novel.handle("fight_attack", payload=item_idx)
            else:
                res = novel.handle("fight_talk", payload=text)
            # Передаем текст в принтер (это безопасно делать из потока)
            display_text.set_text(res["text"])
        except Exception as e:
            display_text.set_text(f"Ошибка связи с ИИ: {e}")
        finally:
            # Выключаем режим загрузки, когда поток завершил работу
            is_loading = False
            battle.enabled = True
    is_loading = True
    display_text.set_text(f"{novel.current_enemy.name} думает...")
    threading.Thread(target=fetch_ai_response, daemon=True).start() 

while True:
    mouse_pos = pygame.mouse.get_pos()
    clock.tick(60) # Ограничиваем FPS, чтобы проц не умирал
    
    #тут херня с обновлением кадров анимации
    
    
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
                    special_flags = novel.get_player_location().special_flags
                    malex_img.translate(special_flags["MX"], special_flags["MY"], time=0) if "MX" in special_flags.keys()  else ""
                    bg_img.translate(special_flags["BGX"], special_flags["BGY"], time=0) if "BGX" in special_flags.keys() else ""
                    current_scene = "intro"
                    
            elif current_scene == "intro":
                intro_menu.click(mouse_pos)

            # КЛИКИ ВНУТРИ ИГРЫ (Связь с бэкендом)
            elif current_scene == "game":
                if(items_menu.enabled):
                    items_menu.click(mouse_pos)
                if(map_menu.enabled):
                    map_menu.click(mouse_pos)
                else:
                    
                    # Если мы в обычном режиме исследования
                    if novel.state == "EXPLORING":
                        freeroam.click(mouse_pos)
                        if btn_spec.enabled:
                            intro_menu.click(mouse_pos)
                        

                    # Если движок переключился в режим боя
                    elif novel.state == "COMBAT":
                        battle.click(mouse_pos)
        # ОБРАБОТКА КЛАВИАТУРЫ (для текстового ввода в бою)
        
        if novel.state == "COMBAT":
            battle.any_event(event)

    # --- ОТРИСОВКА ЭКРАНОВ ---
    if current_scene == "menu":
        screen.blit(background_menu, (0, 0))
        if click_zone.collidepoint(mouse_pos):
            screen.blit(button_playh, (button_x, button_y)) 
        else:
            screen.blit(button_play, (button_x, button_y))  
    elif current_scene == "intro":
        screen.fill((0, 0, 0))
        display_text.update()
        bg_img.draw(screen)
        malex_img.draw(screen)
        
        screen.blit(text_box_image, (0.5 * weight - text_box_image.get_width() // 2 - 10, 0.5 * height - text_box_image.get_height() // 2 + 30)) # Рисуем текстуру плашки поверх
        intro_menu.draw(screen)
        text_surface = dialog_font.render(display_text.get_text(), True, black, wraplength=700) 
        screen.blit(text_surface, (120, 560))  
        if novel.player.location == "start":
            current_scene = "game"
    elif current_scene == "game":
        screen.fill((0, 0, 0))
        display_text.update()
        # Рисуем фон локации
        if novel.player.location not in bgs:
            screen.blit(background_image, (0.5 * weight - background_image.get_width() // 2, 0.5 * height - background_image.get_height() // 2 ))
        else:
            screen.blit(bgs[novel.player.location], (0.5 * weight - bgs[novel.player.location].get_width() // 2, 0.5 * height - bgs[novel.player.location].get_height() // 2 ))
        
        # Рисуем Спрайты персонажей
        malex_img.draw(screen)

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
            if "special" in novel.get_player_location().special_flags.keys():
                btn_spec.draw(screen)
                btn_spec.enabled = True
            else: 
                btn_spec.enabled = False
            
        elif novel.state == "COMBAT":
            battle.draw(screen)
            # Показываем ХП врага, если идет бой
            if novel.current_enemy:
                enemy_hp_text = names_font.render(f"{novel.current_enemy.name} HP: {novel.current_enemy.gethp()}", True, dred)
                screen.blit(enemy_hp_text, (780, 160))
        items_menu.draw(screen)
        map_menu.draw(screen)
        if "intro" in novel.player.location:
            current_scene = "intro"

    pygame.display.flip()