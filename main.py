import pygame
import sys as sus
#import websearch
from rpnovel_engine import RPGNovel 
import os
#import base64
import random
import threading
pygame.init()

weight, height = 1000, 800
screen = pygame.display.set_mode((weight, height))
pygame.display.set_caption('Gay')

clock = pygame.time.Clock()

btn = pygame.image.load('assets/images/UI/buttonmini.png').convert_alpha()
btn_next_img =  pygame.image.load('assets/images/UI/next.png').convert_alpha()
btn_prev_img = pygame.image.load('assets/images/UI/prev.png').convert_alpha()
class Button:
    def __init__(self, x, y, w=None, h=None, text="", img=None, 
                 func=lambda: print("hi i'm button"), 
                 on_hover=lambda x: print(f"hey that's my shoulder"), 
                 off_hover=lambda x: print(f"damn")):
        
        if img != "no":
            self.orig_img = img if img else btn 
            self.img = self.orig_img
        else:
            self.orig_img = None
            self.img = None
        
        width = w if w else self.img.get_width()
        height = h if h else self.img.get_height()
        self.rect = pygame.Rect(x, y, width, height)
        
        self.__text = text

        self.text_manager = PygameTextPrinter(speed_ms=50)
        self.text_manager.set_text(text)
        
        self.last_text = ""
        self.text_surf = ui_font.render(self.__text, True, (0, 0, 0))
        
        self.last_update = 0
        self.speed = 333
        
        self.enabled = True
        self.func = func
        self.on_hover = on_hover
        self.off_hover = off_hover
        self.hovered = False
        self.prevpos = (0,0)
        self.imgpos = (x, y)
        self.overlay_img = None  # Для эффекта при наведении (можно задать картинку или цветовую заливку)
        # --- КЭШИРОВАНИЕ ПОВОРОТОВ (ОПТИМИЗАЦИЯ ПОКАЧИВАНИЯ) ---
        self.rotated_imgs = {}
        if self.orig_img:
            # Заранее генерируем повернутые картинки для углов -4, -2, 0, 2, 4 градуса
            for r in range(-2, 3):
                angle = r * 2
                if angle == 0:
                    self.rotated_imgs[angle] = self.orig_img
                else:
                    self.rotated_imgs[angle] = pygame.transform.rotate(self.orig_img, angle)

        # --- ПЕРЕМЕННЫЕ ДЛЯ ОДНОПОТОЧНОГО TRANSLATE ---
        self.is_translating = False
        self.trans_start_x, self.trans_start_y = x, y
        self.trans_target_x, self.trans_target_y = x, y
        self.trans_duration = 0
        self.trans_start_time = 0

    def set_overlay_image(self, overlay_img, px,py):
        """Устанавливает картинку для эффекта при наведении мыши"""
        self.overlay_img = overlay_img
        self.overlay_img_px = px
        self.overlay_img_py = py # Отступы от границ кнопки для наложения эффекта

    def smoothstep(self, a: float, b: float, t: float) -> float:
        t = max(0.0, min(1.0, t))
        t = t * t * (3.0 - 2.0 * t)
        return a + t * (b - a)

    def draw(self, surf):
        if not self.enabled or self.img is None:
            return  
            
        current_time = pygame.time.get_ticks()
        
        # 1. СИНХРОННЫЙ ОБРАБОТЧИК ДВИЖЕНИЯ (Вместо потока)
        if self.is_translating:
            elapsed = current_time - self.trans_start_time
            if elapsed >= self.trans_duration:
                self.rect.x, self.rect.y = self.trans_target_x, self.trans_target_y
                self.is_translating = False
            else:
                t = elapsed / self.trans_duration
                self.rect.x = int(self.smoothstep(self.trans_start_x, self.trans_target_x, t))
                self.rect.y = int(self.smoothstep(self.trans_start_y, self.trans_target_y, t))

        # 2. ОПТИМИЗИРОВАННОЕ ПОКАЧИВАНИЕ (Брать из кэша, а не крутить на лету)
        if current_time - self.last_update >= self.speed:
            r = random.randint(-2, 2)
            angle = r * 2
            # Достаем готовую картинку из словаря (это мгновенно)
            self.img = self.rotated_imgs.get(angle, self.orig_img)
            self.last_update = current_time
            
        
        img_w, img_h = self.img.get_width(), self.img.get_height()
        self.imgpos = (
            self.rect.x + (self.rect.width >> 1) - (img_w >> 1), 
            self.rect.y + (self.rect.height >> 1) - (img_h >> 1)
        )
        self.prevpos = self.imgpos
        
        surf.blit(self.img, self.imgpos)
        if self.overlay_img:
            surf.blit(self.overlay_img, (self.imgpos[0] + self.overlay_img_px, self.imgpos[1] + self.overlay_img_py))
        
        surf.blit(self.text_surf, (self.rect.x + 25, self.rect.y + 15))

    def translate(self, newx, newy, time=500):
        if newx == self.rect.x and newy == self.rect.y:
            return
            
        if time <= 0:
            self.rect.x, self.rect.y = newx, newy
            self.is_translating = False
            return
            
        self.trans_start_x, self.trans_start_y = self.rect.x, self.rect.y
        self.trans_target_x, self.trans_target_y = newx, newy
        self.trans_duration = time
        self.trans_start_time = pygame.time.get_ticks()
        self.is_translating = True
    def img_translate(self,new,newy,time=500):
        pass
class Button_old:
    def __init__(self, x, y, w=None, h=None, text="", img=None, func=lambda: print("hi i'm button"), on_hover=lambda x: print(f"hey that's my shoulder"), off_hover=lambda x: print(f"damn")):
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
        
        self.__text = text

        # Анимация текста внутри кнопки
        self.text_manager = PygameTextPrinter(speed_ms=50)
        self.text_manager.set_text(text)
        
        self.last_text = ""
        self.text_surf = None
        
        # Таймеры для визуальных эффектов (поворот)
        self.last_update = 0
        self.speed = 333
        self.text_surf = ui_font.render(self.__text, True, (0, 0, 0))
        
        self.enabled = True
        self.func = func
        self.on_hover = on_hover
        self.off_hover = off_hover
        self.hovered = False
        self.prevpos = (0,0)
        self.imgpos = (x, y)

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
        #if self.imgpos != self.prevpos:
        img_w, img_h = self.img.get_width(), self.img.get_height()
        self.imgpos = (self.rect.x + (self.rect.width >> 1) - (img_w >> 1), 
            self.rect.y + (self.rect.height >> 1) - (img_h >> 1)) # this is bitwise shift nigga
        self.prevpos = self.imgpos
        
        surf.blit(self.img, self.imgpos)
        
        ## Обновляем состояние печатного текста
        #self.text_manager.update()
        #current_text_string = self.text_manager.get_text()
        #
        ## ОПТИМИЗАЦИЯ: Рендерим текст ТОЛЬКО если строка изменилась
        #if current_text_string != self.last_text or self.text_surf is None:
        #    self.last_text = current_text_string
            
        # Отрисовка текста по центру кнопки (или с фиксированным отступом)
        surf.blit(self.text_surf, (self.rect.x + 25, self.rect.y + 15))
    def translate(self, newx, newy, time=500):
        if newx == self.rect.x and newy == self.rect.y:
            return
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

class SelectableButton:
    def __init__(self, x, y, w=None, h=None, button_array=None,next_img=btn_next_img,prev_img=btn_prev_img):
        # Задаем размеры rect
        width = w
        height = h
        self.rect = pygame.Rect(x, y, width, height)
        self.enabled = True
        self.item = 0
        self.func = lambda : self.click()
        self.array = button_array
        self.next = Button(x+100,y,60,55,img=next_img,func= lambda : self.fnext())
        self.prev = Button(x-100,y,50,55,img=prev_img,func= lambda : self.fprev())
    def click(self,mouse_pos):
        btn_cur = self.array[self.item]
        if btn_cur.rect.collidepoint(mouse_pos):
            btn_cur.func()
        if self.next.rect.collidepoint(mouse_pos):
            self.fnext()
        if self.prev.rect.collidepoint(mouse_pos):
            self.fprev()
    def fnext(self):
        self.item = min((self.item+1),len(self.array)-1)
    def fprev(self):
        self.item = max((self.item-1),0)
    def draw(self,surf):
        if not self.enabled:
            return  # Просто не рисуем и не обновляем, если кнопка выключена
        btn_cur = self.array[self.item]
        btn_cur.rect.x = self.rect.x
        btn_cur.rect.y = self.rect.y
        btn_cur.draw(surf)
        self.next.rect.x = self.rect.x+200
        self.next.rect.y = self.rect.y 
        self.next.draw(surf) if self.item != len(self.array)-1 else ""
        self.prev.rect.x = self.rect.x-200
        self.prev.rect.y = self.rect.y
        self.prev.draw(surf) if self.item != 0 else ""

        
class Image_old:
    def __init__(self, x, y, img, animations=None, animation_speed=500,anim=False):
        self.img = img
        self.rect = pygame.Rect(x, y, img.get_width(), img.get_height())
        self.animations = animations
        self.animation = 0
        self.animation_speed = animation_speed
        self.anim = anim
        self.current_frame = 0
        self.last_update = 0
        self.enabled = True

    def draw(self, surf):
        if not self.enabled or self.img is None:
            return
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
        if newx == self.rect.x and newy == self.rect.y:
            return
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
    def short_animation(self, anim_idx, duration=500):
        def animate():
            original_animation = self.animation
            self.animation = anim_idx
            pygame.time.wait(duration)
            self.animation = original_animation
        threading.Thread(target=animate, daemon=True).start()
    def shake(self, intensity=5, duration=500):
        def animate():
            original_pos = (self.rect.x, self.rect.y)
            start_time = pygame.time.get_ticks()
            while True:
                now = pygame.time.get_ticks()
                elapsed = now - start_time
                if elapsed >= duration:
                    self.rect.x, self.rect.y = original_pos
                    break
                else:
                    offset_x = random.randint(-intensity, intensity)
                    offset_y = random.randint(-intensity, intensity)
                    self.rect.x = original_pos[0] + offset_x
                    self.rect.y = original_pos[1] + offset_y
        threading.Thread(target=animate, daemon=True).start()

class Image:
    def __init__(self, x, y, img, animations=None, animation_speed=500, anim=False):
        self.img = img
        self.rect = pygame.Rect(x, y, img.get_width(), img.get_height())
        self.animations = animations
        self.animation = 0
        self.animation_speed = animation_speed
        self.anim = anim
        self.current_frame = 0
        self.last_update = 0
        self.enabled = True

        # --- НОВЫЕ ПЕРЕМЕННЫЕ ДЛЯ ТРЕНДИНГА АНИМАЦИЙ В ОДНОМ ПОТОКЕ ---
        # Переменные движения (translate)
        self.is_translating = False
        self.trans_start_x, self.trans_start_y = x, y
        self.trans_target_x, self.trans_target_y = x, y
        self.trans_duration = 0
        self.trans_start_time = 0

        # Переменные тряски (shake)
        self.is_shaking = False
        self.shake_origin_x, self.shake_origin_y = x, y
        self.shake_intensity = 0
        self.shake_duration = 0
        self.shake_start_time = 0

        # Переменные временной анимации (short_animation)
        self.has_short_anim = False
        self.original_animation_idx = 0
        self.short_anim_duration = 0
        self.short_anim_start_time = 0

    def smoothstep(self, a: float, b: float, t: float) -> float:
        t = max(0.0, min(1.0, t))
        t = t * t * (3.0 - 2.0 * t)
        return a + t * (b - a)

    def draw(self, surf):
        if not self.enabled or self.img is None:
            return

        now = pygame.time.get_ticks()

        # 1. СИНХРОННЫЙ ОБРАБОТЧИК TRANSLATE (Плавное перемещение)
        if self.is_translating:
            elapsed = now - self.trans_start_time
            if elapsed >= self.trans_duration:
                self.rect.x, self.rect.y = self.trans_target_x, self.trans_target_y
                self.is_translating = False
            else:
                t = elapsed / self.trans_duration
                self.rect.x = int(self.smoothstep(self.trans_start_x, self.trans_target_x, t))
                self.rect.y = int(self.smoothstep(self.trans_start_y, self.trans_target_y, t))

        # 2. СИНХРОННЫЙ ОБРАБОТЧИК SHAKE (Тряска экрана/персонажа)
        # Инициализируем смещения для текущего кадра
        offset_x, offset_y = 0, 0
        if self.is_shaking:
            elapsed = now - self.shake_start_time
            if elapsed >= self.shake_duration:
                self.is_shaking = False
            else:
                offset_x = random.randint(-self.shake_intensity, self.shake_intensity)
                offset_y = random.randint(-self.shake_intensity, self.shake_intensity)

        # 3. СИНХРОННЫЙ ОБРАБОТЧИК SHORT_ANIMATION (Временная смена анимации)
        if self.has_short_anim:
            elapsed = now - self.short_anim_start_time
            if elapsed >= self.short_anim_duration:
                self.animation = self.original_animation_idx
                self.has_short_anim = False

        # --- ОТРИСОВКА ---
        # Вычисляем финальную позицию рендера с учетом возможной тряски
        render_x = self.rect.x + offset_x
        render_y = self.rect.y + offset_y

        if not self.anim:
            surf.blit(self.img, (render_x, render_y))
        else:
            self.animation_frames = self.animations[self.animation]
            if now - self.last_update > self.animation_speed:
                self.current_frame = (self.current_frame + 1) % len(self.animation_frames)
                self.last_update = now
            surf.blit(self.animation_frames[self.current_frame], (render_x, render_y))
            
    def translate(self, newx, newy, time=500):
        if newx == self.rect.x and newy == self.rect.y:
            return
        # Передаем управление в draw(). Если время 0 — перемещаем мгновенно
        if time <= 0:
            self.rect.x, self.rect.y = newx, newy
            self.is_translating = False
            return
            
        self.trans_start_x, self.trans_start_y = self.rect.x, self.rect.y
        self.trans_target_x, self.trans_target_y = newx, newy
        self.trans_duration = time
        self.trans_start_time = pygame.time.get_ticks()
        self.is_translating = True

    def short_animation(self, anim_idx, duration=500):
        # Если короткая анимация уже идет, не перезапускаем её хаотично
        if not self.has_short_anim:
            self.original_animation_idx = self.animation
        
        self.animation = anim_idx
        self.short_anim_duration = duration
        self.short_anim_start_time = pygame.time.get_ticks()
        self.has_short_anim = True

    def shake(self, intensity=5, duration=500):
        # Запоминаем базовую точку, относительно которой будем трясти
        self.shake_intensity = intensity
        self.shake_duration = duration
        self.shake_start_time = pygame.time.get_ticks()
        self.is_shaking = True

class Menu:
    def __init__(self, buttons):
        self.panels = buttons
        self.enabled = True

    def draw(self, surf):
        if not self.enabled: return
        for item in self.panels:
            if isinstance(item, VisualMap):
                item.draw(surf, novel.player)
                continue
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
            if isinstance(btn, SelectableButton):
                # Проверяем активность кнопки ДО проверки коллизии
                if btn.enabled:
                    btn.click(mouse_pos)
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
        reset_afk()
        if not self.enabled: return

        for btn in self.panels:
            if isinstance(btn, TextInputField):
                btn.handle_event(event)
            if isinstance(btn, Button) and event.type == pygame.MOUSEMOTION:
                if btn.enabled and btn.rect.collidepoint(event.pos):
                    if not btn.hovered:
                        btn.on_hover(btn)
                        btn.hovered = True
                elif btn.hovered:
                    btn.off_hover(btn)
                    btn.hovered = False
                

class TextInputField:
    def __init__(self, x, y, w, h, font, text_color=(0, 0, 0), img=None, max_chars=500, on_submit=None):
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
                image_malex.animation = 2
            else:
                self.active = False
                image_malex.animation = 0

        # Если поле «в фокусе», перехватываем клавиатуру
        if self.active and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                # Если нажали Enter и текст не пустой — отправляем данные в callback
                if self.text.strip() and self.on_submit:
                    image_malex.animation = 0
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
        
        #if text_width > max_visible_width:
        #    # Отрезаем кусок поверхности текста, который не влезает
        #    sub_rect = pygame.Rect(text_width - max_visible_width, 0, max_visible_width, self.rect.height)
        #    text_draw_surf = text_surf.subsurface(sub_rect)
        #    text_x = self.rect.x + 10
        #else:
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
class ScrollList:
    def __init__(self, x, y, width, height, item_height=50):
        self.x = x
        self.y = y
        self.width = width
        self.height = height          # Высота видимого окошка инвентаря
        self.item_height = item_height  # Высота одной строчки/кнопки (у тебя это 50)
        
        self.items = []               # Сюда складываем созданные объекты Button
        self.scroll_y = 0             # Текущий сдвиг прокрутки (в пикселях)
        self.max_scroll = 0           # Максимальный предел прокрутки вверх

    def set_items(self, items_list):
        """Заполняет список элементами и пересчитывает максимальный скролл"""
        self.items = items_list
        # Считаем полную высоту всего списка
        total_height = len(self.items) * self.item_height
        # Максимально скроллить можно только если контент длиннее, чем экран
        self.max_scroll = max(0, total_height - self.height)
        # Принудительно сбрасываем скролл, чтобы не сломать отображение при пересборке
        self.scroll_y = 0 
        self.update_positions()

    def update_positions(self):
        """Динамически пересчитывает Y-координату для каждой кнопки с учетом скролла"""
        for i, item in enumerate(self.items):
            # Базовая позиция (внутри списка) минус сдвиг скролла
            item.rect.y = self.y + (i * self.item_height) - self.scroll_y
            item.rect.x = self.x

    def handle_event(self, event):
        """Вставь вызов этого метода в свой главный цикл обработки событий Pygame"""
        if not self.items:
            return

        # 1. Прокрутка колесиком мыши (работает, если курсор над областью списка)
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            # Проверяем, что мышка находится внутри границ скролл-листа
            if (self.x <= mouse_pos[0] <= self.x + self.width and 
                self.y <= mouse_pos[1] <= self.y + self.height):
                
                if event.button == 4: # Колесико ВВЕРХ
                    self.scroll_y = max(0, self.scroll_y - self.item_height)
                    self.update_positions()
                elif event.button == 5: # Колесико ВНИЗ
                    self.scroll_y = min(self.max_scroll, self.scroll_y + self.item_height)
                    self.update_positions()

        # 2. Прокрутка стрелочками клавиатуры
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.scroll_y = max(0, self.scroll_y - self.item_height)
                self.update_positions()
            elif event.key == pygame.K_DOWN:
                self.scroll_y = min(self.max_scroll, self.scroll_y + self.item_height)
                self.update_positions()

    def get_visible_panels(self):
        """
        Возвращает только те кнопки, которые попадают в видимую зону экрана.
        Предотвращает клики по невидимым кнопкам, улетевшим вверх или вниз.
        """
        visible = []
        for item in self.items:
            # Если верхняя граница кнопки внутри окна инвентаря
            if self.y <= item.rect.y <= (self.y + self.height - 10): # -10 для запаса
                visible.append(item)
        return visible

novel = RPGNovel("Malex") 


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

imgfile_bg_menu = pygame.image.load('assets/images/UI/menu_fon1.png').convert()
imgfile_textbox = pygame.image.load('assets/images/UI/button.png').convert_alpha()

imgfile_play0 = pygame.image.load('assets/images/UI/Pplay.png') 
imgfile_play1 = pygame.image.load('assets/images/UI/Pplay1.png')
imgfile_exit0 = pygame.image.load('assets/images/UI/exit.png')
imgfile_exit1 = pygame.image.load('assets/images/UI/exit1.png')
imgfile_gamename = pygame.image.load('assets/images/UI/game.png').convert_alpha()
cursor_img = pygame.image.load('assets/images/UI/cursor.png').convert_alpha()
malex_click = pygame.image.load('assets/images/UI/malexclick.png').convert_alpha()

button_x, button_y = 0, 0
click_zone = pygame.Rect(65, 290, 255, 90)

exit_button_x, exit_button_y = 0, 0
exit_click_zone = pygame.Rect(65, 410, 255, 90)

# Зоны для кликов в самой игре (Кнопки действий)
# Формат: pygame.Rect(X, Y, ШИРИНА, ВЫСОТА)

#херня с анимацией ..dunno если честно куда ее вставить. так что пусть сюда.. ):
#тут загружаются кадрі анимации
anim_malex_static = [
    pygame.image.load('assets/images/sprites/Pmalex.png').convert_alpha(),
    pygame.image.load('assets/images/sprites/Pmalex01.png').convert_alpha(),
]
anim_malex_thinks = [
    pygame.image.load('assets/images/sprites/Pmalexthinks.png').convert_alpha(),
    pygame.image.load('assets/images/sprites/Pmalexthinks1.png').convert_alpha(),
]
anim_malex_menu = [
    pygame.image.load('assets/images/UI/malex.png').convert_alpha(),
    pygame.image.load('assets/images/UI/malex1.png').convert_alpha(),
]

imgfile_malex_fall = pygame.image.load('assets/images/sprites/Pmalexfall.png').convert_alpha()
imgfile_malex_attack = pygame.image.load('assets/images/sprites/Pmalexattack.png').convert_alpha()
# переменніе для управления таймингом анимации

image_malex = Image(0, 0, anim_malex_static[0], animations=[anim_malex_static, [imgfile_malex_fall, imgfile_malex_fall], anim_malex_thinks, [imgfile_malex_attack,imgfile_malex_attack]], animation_speed=600, anim=True)
image_bg = Image(0, 0, bgs[novel.player.location] if novel.player.location in bgs.keys() else imgfile_bg)
malex_menu = Image(0, 0, anim_malex_menu[0], animations=[anim_malex_menu], animation_speed=800, anim=True) #какая тут ошибка гайс

# --- КЛИКАБЕЛЬНЫЙ СПРАЙТ В МЕНЮ ---
# Здесь лежат параметры хитбокса клика по спрайту Малекс в главном меню.
# Если надо подогнать область клика, меняем только эти 4 значения.
malex_menu_click_hitbox_x = 590
malex_menu_click_hitbox_y = 180
malex_menu_click_hitbox_w = 210
malex_menu_click_hitbox_h = 200

# Сам прямоугольник для проверки клика по спрайту.
# Его не правим напрямую, он строится из 4 чисел выше.
malex_menu_click_hitbox = pygame.Rect(
    malex_menu_click_hitbox_x,
    malex_menu_click_hitbox_y,
    malex_menu_click_hitbox_w,
    malex_menu_click_hitbox_h,
)

# Сколько миллисекунд спрайт должен оставаться в состоянии клика, прежде чем вернуться к обычной анимации меню.
malex_menu_click_duration_ms = 700

# Если True, вокруг хитбокса будет рисоваться зелёная рамка для отладки.
show_malex_menu_hitbox = False
# Отладочная рамка для кнопки выхода. Можно удалить вместе с блоком отрисовки ниже, если она больше не нужна.
show_exit_hitbox = False


# Храним момент клика. Когда значение None, значит спрайт сейчас в обычном режиме.
malex_menu_click_started_at = None


def start_malex_menu_click():
    """Переключает спрайт меню в статичный клик-спрайт и запускает таймер возврата."""
    global malex_menu_click_started_at

    # Останавливаем анимацию, подменяем картинку на спрайт клика и фиксируем время.
    malex_menu.anim = False
    malex_menu.img = malex_click
    malex_menu_click_started_at = pygame.time.get_ticks()


def update_malex_menu_click_state():
    """Каждый кадр проверяет, не пора ли вернуть обычный анимированный спрайт."""
    global malex_menu_click_started_at

    # Если клика не было, ничего делать не нужно.
    if malex_menu_click_started_at is None:
        return

    now = pygame.time.get_ticks()

    # Когда таймер истёк, возвращаем исходную анимацию меню.
    if now - malex_menu_click_started_at >= malex_menu_click_duration_ms:
        malex_menu.anim = True
        malex_menu.animation = 0
        malex_menu.current_frame = 0
        malex_menu.last_update = now
        malex_menu.img = anim_malex_menu[0]
        malex_menu_click_started_at = None


image_ui_cross = Image(0,0, pygame.image.load('assets/images/UI/cross.png'))
start_time = 0
def action_move(direction):
    res = novel.handle("move", direction)
    special_flags = novel.get_player_location().special_flags
    image_malex.translate(special_flags["MX"], special_flags["MY"], time=300) if "MX" in special_flags.keys()  else image_malex.translate(0, 0, time=300)
    global start_time
    start_time = pygame.time.get_ticks()
    display_text.set_text(res["text"])

def action_start_combat(enemy_idx=1):
    res = novel.handle("start_combat", enemy_idx)
    display_text.set_text(res["text"])
    global cur_enemy_imgfile
    enemy_id = res["extra_data"]["enemy"].id if "extra_data" in res.keys() and "enemy" in res["extra_data"].keys() else "missingno"
    try:
        cur_enemy_imgfile = pygame.image.load(f'assets/images/sprites/enemies/{enemy_id}.png').convert_alpha()
    except:
        cur_enemy_imgfile = pygame.image.load(f'assets/images/sprites/enemies/missingno.png').convert_alpha()
imgfile_inv = pygame.image.load('assets/images/UI/inventory.png').convert_alpha()

btn_n = Button(865, 257, 60, 55, text="Север", func=lambda : action_move("север"), img="no" ) #display_text.set_text(novel.handle("move","север")["text"])
btn_s = Button(865, 368, 60, 55, text="Юг", func=lambda : action_move("юг"), img="no" )
btn_e = Button(924, 312, 60, 55, text="Восток", func=lambda : action_move("восток"), img="no" )
btn_w = Button(812, 312, 60, 55, text="Запад", func=lambda : action_move("запад"), img="no" )

btn_inspect = Button(300, 700, text="Осмотреться", func=lambda : open_room_items())
btn_attack = Button(500, 700, text="Атаковать", func=lambda : action_start_combat() )

btn_save = Button(900, 20, text="Сохранить", func=lambda : display_text.set_text(novel.handle("save")["text"]) )

btn_inv = Button(700, 700, text="Инвентарь", func=lambda : open_player_inventory())

btn_map = Button(800, 700, text="Карта", func=lambda: setattr(map_menu, 'enabled', True))

freeroam = Menu([btn_n,btn_s,btn_e,btn_w, btn_inspect, btn_attack, btn_inv, btn_save, btn_map, image_ui_cross])

# Вместо подмены текста на лету внутри отрисовки, сделайте явные кнопки для боя:
point=200
offset = 80
btn_hit = Button(220, point, text="Ударить", func=lambda: open_player_weapons())
input_field = TextInputField(220, point + offset, 200, 50, font=ui_font, max_chars=60, on_submit=lambda x: fight(text=x))
btn_item = Button(220, point + offset*2, text="Предмет", func=lambda: battle_player_inventory())
btn_mercy = Button(220, point + offset*3, text="ПОЩАДА", func=lambda: open_mercy_buttons())
btn_array = SelectableButton(220, point-offset, 50, 60, [])
btn_array.enabled = False


battle = Menu([btn_hit, input_field, btn_item, btn_mercy, btn_array])

btn_close_items = Button(700, 20, text="X", func=lambda: close_items_menu())
# Создаем окно скролла шириной 500px и высотой 300px в координатах (60, 40)
inv_scroll_list = ScrollList(x=60, y=40, width=150, height=100, item_height=50)

imgfile_item = pygame.image.load('assets/images/UI/item.png').convert_alpha()

items_menu = Menu([btn_close_items,inv_scroll_list]) 
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
    image_bg.img = bgs[novel.player.location] if novel.player.location in bgs.keys() else imgfile_bg
    if "MX" in special_flags.keys():
        image_malex.translate(special_flags["MX"], special_flags["MY"], time=special_flags["MT"]) if "MT" in special_flags.keys()  else image_malex.translate(special_flags["MX"], special_flags["MY"], time=1000)
        
    image_malex.animation = special_flags["MANIM"] if "MANIM" in special_flags.keys() else 0
    if "BGX" in special_flags.keys():
        image_bg.translate(special_flags["BGX"], special_flags["BGY"], time=special_flags["BGT"]) if "BGT" in special_flags.keys()  else image_bg.translate(special_flags["BGX"], special_flags["BGY"], time=1000)

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

def rebuild_items_menu(raw_data, on_click_callback, keep_idx=-1,inv_img=True):
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
                100, 70 + i * 50, 
                200, 70,
                func=lambda item_idx=i, name=item_name: on_click_callback(item_idx, name),
                img=imgfile_item
            )
        else:
            btn = Button(
                -20, 70 + i * 50, 
                200, 70,
                func=lambda item_idx=i, name=item_name: on_click_callback(item_idx, name),
                on_hover=lambda btn: btn.translate(100, btn.rect.y, time=200), 
                off_hover=lambda btn: btn.translate(-20, btn.rect.y, time=200),
                img=imgfile_item
            )
        try:
            file = pygame.transform.scale(pygame.image.load(f'assets/images/items/{item_name}.png'),(70,70))
        except:
            file = pygame.image.load(f'assets/images/blank.png')
            print(f"not found {item_name}")
        btn.set_overlay_image(file,30,30)
        new_panels.append(btn)
        
    items_menu.panels = new_panels


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
    # Строим меню предметов комнаты, при клике сработает подбор
    image_malex.translate(100, 0, time=200)
    
    rebuild_items_menu(room_data, action_pick_up)

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
    rebuild_items_menu(inv_data, battle_drop_buttons,keep_idx,inv_img=False)

def open_player_inventory(keep_idx=None):
    items_menu.enabled = True
    inv_data = novel.handle("inv_internal")["text"]
    print("ХМПФ!! ты хочешь чтобы я открыла для тебя инвентарь??? ну уж нет!! не надейся даже! н-но, если что он открылся.. н-наверное....") # why are you so tsundere
    # Строим меню инвентаря, при клике сработает использование/осмотр
    rebuild_items_menu(inv_data, drop_buttons, keep_idx,inv_img=False)

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

def reset_battle_panels():
    battle.panels = [btn_hit, input_field, btn_item, btn_mercy, btn_array]
    btn_array.enabled = False
    input_field.text = "Сказать..."

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
            file = pygame.image.load(f'assets/images/items/{novel.handle("get_weapon_id",item_idx)["text"]}.png')
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
            
        # ОБРАБОТКА КЛИКОВ МЫШКИ
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            
            # Клик в Главном Меню
            if current_scene == "menu":
                # Сначала проверяем клик по спрайту Malex.
                # Если он попал в хитбокс, запускаем временную реакцию спрайта.
                if exit_click_zone.collidepoint(mouse_pos):
                    pygame.quit()
                    sus.exit()
                elif malex_menu_click_hitbox.collidepoint(mouse_pos):
                    start_malex_menu_click()
                elif click_zone.collidepoint(mouse_pos):
                    res = novel.handle("load") # Получаем описание локации при входе в игру
                    display_text.set_text(res["text"])
                    special_flags = novel.get_player_location().special_flags
                    image_malex.translate(special_flags["MX"], special_flags["MY"], time=0) if "MX" in special_flags.keys()  else ""
                    image_bg.translate(special_flags["BGX"], special_flags["BGY"], time=0) if "BGX" in special_flags.keys() else ""
                    current_scene = "intro"
                    
            elif current_scene == "intro":
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

                    # Если движок переключился в режим боя
                    elif novel.state == "COMBAT":
                        battle.click(mouse_pos)
        # ОБРАБОТКА КЛАВИАТУРЫ (для текстового ввода в бою)
        if items_menu.enabled:
            items_menu.any_event(event)
        if novel.state == "COMBAT":
            battle.any_event(event)
            #if items_menu.enabled:  ### OBSOLETE: uncomment this shit if you are using new rebuild items menu (with scroll things)
            #    items_menu.any_event(event)

    # --- ОТРИСОВКА ЭКРАНОВ ---
    if current_scene == "menu":
        # Перед отрисовкой проверяем, не закончился ли эффект клика по Malex.
        update_malex_menu_click_state()

        screen.blit(imgfile_bg_menu, (0, 0))
        screen.blit(imgfile_gamename, (0, 0))
        malex_menu.draw(screen)

        if exit_click_zone.collidepoint(mouse_pos):
            screen.blit(imgfile_exit1, (exit_button_x, exit_button_y))
        else:
            screen.blit(imgfile_exit0, (exit_button_x, exit_button_y))

        # Отладочная зелёная рамка помогает увидеть реальную область клика.
        # Если она больше не нужна, просто поставь show_malex_menu_hitbox = False.
        if show_malex_menu_hitbox:
            pygame.draw.rect(
                screen,
                (0, 255, 0),
                malex_menu_click_hitbox,
                2,
            )

        # Отладочная зелёная рамка для кнопки выхода.
        if show_exit_hitbox:
            pygame.draw.rect(
                screen,
                (0, 255, 0),
                exit_click_zone,
                2,
            )

        if click_zone.collidepoint(mouse_pos):
            screen.blit(imgfile_play1, (button_x, button_y))
        else:
            screen.blit(imgfile_play0, (button_x, button_y))  
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
        
        # Рисуем фон локации
        if novel.player.location not in bgs:
            screen.blit(imgfile_bg, (0,0))
        else:
            screen.blit(bgs[novel.player.location], (0,0 ))
        
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
                screen.blit(enemy_hp_text, (780, 160))
        if items_menu.enabled:
            items_menu.draw(screen)
        if map_menu.enabled:
            map_menu.draw(screen)
        if "intro" in novel.player.location:
            current_scene = "intro"

    screen.blit(cursor_img, pygame.mouse.get_pos())

    pygame.display.flip()
    