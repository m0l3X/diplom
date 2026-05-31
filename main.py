import pygame
import sys
#import websearch
from rpnovel_engine import RPGNovel 
#import io
#import base64
import random
import threading
pygame.init()

btn = pygame.image.load('assets/images/UI/buttonmini.png')
class Button:
    def __init__(self, x, y, w=None, h=None, text="", img=btn):
        self.rect = pygame.Rect(x,y,w,h) if w and h else pygame.Rect(x,y,img.get_width(), img.get_height())
        self.__w = self.rect.width
        self.img = img
        self.orig_img = img
        self.text = PygameTextPrinter(speed_ms=50)
        self.text.set_text(text)
        self.last_update = 0
        self.speed = 333
        self.enabled = True
    def draw(self, surf):
        if self.enabled == False: 
            self.rect.width = 0 if self.rect.width != 0 else 0
            return
        self.rect.width = self.__w if self.rect.width == 0 else self.rect.width
        pos = (self.rect.x +self.rect.width//2 - self.img.width//2, self.rect.y + self.rect.height//2 - self.img.height//2)
        self.text_surf = ui_font.render(self.text.get_text(), True, black)
        self.text.update()
        surf.blit(btn, pos)
        surf.blit(self.text_surf, (self.rect.x + 45, self.rect.y + 8))
        current_time = pygame.time.get_ticks()
        if current_time - self.last_update >= self.speed:
            r = random.randint(-10,10)
            self.img = pygame.transform.rotate(self.orig_img, r)
            self.last_update = current_time


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


novel = RPGNovel("Maxon") 

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


btn_move = Button(100, 700, text="Идти")
btn_move = Button(100, 700, text="Идти")
btn_move = Button(100, 700, text="Идти")
btn_move = Button(100, 700, text="Идти")
btn_inspect = Button(300, 700, text="Осмотреться")
btn_attack = Button(500, 700, text="Атаковать")

current_scene = "menu"
weight, height = 1000, 800
screen = pygame.display.set_mode((weight, height))
pygame.display.set_caption('Gay')

clock = pygame.time.Clock()

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
            sys.exit()
            
        # ОБРАБОТКА КЛИКОВ МЫШКИ
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            
            # Клик в Главном Меню
            if current_scene == "menu":
                if click_zone.collidepoint(mouse_pos):
                    res = novel.handle("load") # Получаем описание локации при входе в игру
                    display_text.update()
                    current_scene = "game"
                    
                    
            # КЛИКИ ВНУТРИ ИГРЫ (Связь с бэкендом)
            elif current_scene == "game":
                
                # Если мы в обычном режиме исследования
                if novel.state == "EXPLORING":
                    if btn_move.rect.collidepoint(mouse_pos):
                        # Игрок нажал "Идти в Пятерочку"
                        res = novel.handle("move", "север")
                        display_text.set_text(res["text"]) 
                        
                    elif btn_inspect.rect.collidepoint(mouse_pos):
                        res = novel.handle("check")
                        display_text.set_text("Малекс внимательно осматривается вокруг...\n"+res["text"]) 
                        items = res["text"].split("\n")
                        
                        
                    elif btn_attack.rect.collidepoint(mouse_pos):
                        # Игрок нажал "Атаковать врага под номером 1"
                        res = novel.handle("start_combat", "1")
                        display_text.set_text(res["text"]) 

                # Если движок переключился в режим боя
                elif novel.state == "COMBAT":
                    if btn_attack.rect.collidepoint(mouse_pos): # Переиспользуем кнопку для удара
                        #res = novel.handle("fight_attack", payload=novel.player.inventory[0])
                        def fetch_ai_response():
                            global is_loading
                            
                            try:
                                is_loading = True
                                btn_attack.enabled = False
                                btn_move.enabled = False
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
                                btn_move.enabled = True
                        is_loading = True
                        display_text.set_text(f"{novel.current_enemy.name} думает...")
                        threading.Thread(target=fetch_ai_response, daemon=True).start() 
                        
                    elif btn_move.rect.collidepoint(mouse_pos): # Переиспользуем кнопку для побега
                        res = novel.handle("fight_run")
                        display_text.set_text(res["text"]) 

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
            # Кнопка Идти
            btn_move.draw(screen)
            
            # Кнопка Осмотреться
            btn_inspect.draw(screen)
            
            # Кнопка Атака
            btn_attack.draw(screen)
            
        elif novel.state == "COMBAT":
            

            # Во время боя кнопки меняют свое назначение и цвет!
            # Кнопка Побег (на месте кнопки Идти)
            btn_move.text.current_text = "Сбежать"
            btn_move.draw(screen)
            # Кнопка Ударить (на месте кнопки Атака)
            btn_attack.text.current_text = "Ударить"
            btn_attack.draw(screen)
            # Показываем ХП врага, если идет бой
            if novel.current_enemy:
                enemy_hp_text = names_font.render(f"{novel.current_enemy.name} HP: {novel.current_enemy.gethp()}", True, dred)
                screen.blit(enemy_hp_text, (780, 160))

    pygame.display.flip()