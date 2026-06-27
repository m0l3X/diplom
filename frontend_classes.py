import pygame
import threading
import random
import os
#from main import ui_font, novel, reset_afk, image_malex
pygame.init()

weight, height = 1000, 800
screen = pygame.display.set_mode((weight, height))

btn = pygame.image.load('assets/images/UI/buttonmini.png').convert_alpha()
btn_next_img =  pygame.image.load('assets/images/UI/next.png').convert_alpha()
btn_prev_img = pygame.image.load('assets/images/UI/prev.png').convert_alpha()
ui_font = pygame.font.SysFont('Freeride', 20)
class Button:
    def __init__(self, x, y, w=None, h=None, text="", img=None, 
                 func=lambda: print("hi i'm button"), 
                 on_hover=lambda x: print(f"hey that's my shoulder"), 
                 off_hover=lambda x: print(f"damn"), wobble=True, debug_draw_hbox=False):
        
        if img != "no":
            self.orig_img = img if img else btn 
            self.img = self.orig_img
        else:
            self.orig_img = None
            self.img = None
        
        width = w if w else self.img.get_width()
        height = h if h else self.img.get_height()

        self.debug_draw_hbox = debug_draw_hbox

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
        self.wobble = wobble
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
        if current_time - self.last_update >= self.speed and self.wobble:
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
        if self.debug_draw_hbox == True:
            pygame.draw.rect(surf, (255,0,0), self.rect)

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
        self.prev = Button(x-60 ,y,60,55,img=prev_img,func= lambda : self.fprev())
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
        self.next.enabled = True if self.item != len(self.array)-1 else False
        self.next.draw(surf) 
        self.prev.rect.x = self.rect.x-60
        self.prev.rect.y = self.rect.y
        self.prev.enabled = True if self.item != 0 else False
        self.prev.draw(surf) 

        
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
    def __init__(self, x, y, img, animations=None, animation_speed=500, anim=False, w=None,h=None):
        self.img = img
        self.rect = pygame.Rect(x, y, img.get_width(), img.get_height())
        self.animations = animations
        self.animation = 0
        self.animation_speed = animation_speed
        self.anim = anim
        self.current_frame = 0
        self.last_update = 0
        self.enabled = True

        if w and h:
            self.img = pygame.transform.scale(self.img, (w,h))

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
                from main import novel
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
        from main import reset_afk
        reset_afk()
        if not self.enabled: return

        for btn in self.panels:
            if isinstance(btn, TextInputField):
                btn.handle_event(event)
            if isinstance(btn, Button):
                if event.type == pygame.MOUSEMOTION:
                    if btn.enabled and btn.rect.collidepoint(event.pos):
                        if not btn.hovered:
                            btn.on_hover(btn)
                            btn.hovered = True
                    elif btn.hovered:
                        btn.off_hover(btn)
                        btn.hovered = False
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if btn.enabled and btn.rect.collidepoint(event.pos):
                        btn.func()
            if isinstance(btn, SelectableButton):
                # Проверяем активность кнопки ДО проверки коллизии
                if btn.enabled and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    btn.click(event.pos)
                

class TextInputField:
    def __init__(self, x, y, w, h, font, text_color=(0, 0, 0), img=None, active_image=None, max_chars=2000, on_submit=None):
        self.orig_img = img if img else btn 
        self.img = self.orig_img
        self.orig_active_img = active_image if active_image else btn

        #self.img = pygame.transform.scale(self.img, (w,h))
        self.active_img = self.orig_active_img
        self.active_img = pygame.transform.scale(self.active_img, (w,h))
        
        self.last_update = 0
        self.speed = 333
        self.rect = pygame.Rect(x, y, w, h)
        self.font = font
        self.text_color = text_color
        self.max_chars = max_chars
        self.on_submit = on_submit  # Функция, которая вызовется при нажатии Enter
        
        self.text = ""              # Текущий введенный текст
        self.active = False         # Выбрано ли поле кликом мышки
        self.enabled = True         # Видимо/активно ли поле в текущей сцене
        
        self.text_surf = self.font.render(self.text, True, self.text_color)
        # Для мигающего курсора
        self.cursor_visible = True
        self.last_cursor_toggle = pygame.time.get_ticks()
        self.cursor_speed = 500     # Интервал мигания (в мс)

    
        

    def handle_event(self, event):
        """Метод обрабатывает события ввода. Вызывать внутри for event in pygame.event.get()"""
        if not self.enabled:
            return
        from main import image_malex
        # Проверяем клик мыши для активации фокуса
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.active = True
                #self.text = "" if self.text == "Сказать..." else self.text
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
            self.text_surf = self.font.render(self.text, True, self.text_color)
            text_width = self.text_surf.get_width()
            max_visible_width = self.rect.width - 20
            if text_width > max_visible_width:
                self.active_img = pygame.transform.scale(self.active_img, (text_width+30,self.rect.height))
            else:
                self.active_img = self.orig_active_img



    def draw(self, surf):
        """Отрисовка поля. Вызывать в блоке отрисовки экрана"""
        if not self.enabled:
            return
        def cool_box(current_time):
            if not self.active:
                if current_time - self.last_update >= self.speed:
                    r = random.randint(-2, 2)
                    self.img = pygame.transform.rotate(self.orig_img, r*2)
                    self.last_update = current_time
                    
                # Центрирование картинки кнопки относительно её rect
                img_w, img_h = self.img.get_width(), self.img.get_height()
                pos = (self.rect.x + self.rect.width // 2 - img_w // 2, 
                self.rect.y + self.rect.height // 2 - img_h // 2)
                surf.blit(self.img, pos)
            else:
                img_w, img_h = self.img.get_width(), self.img.get_height()
                pos = (self.rect.x + self.rect.width // 2 - img_w // 2, 
                self.rect.y + self.rect.height // 2 - img_h // 2)
                surf.blit(self.active_img, pos)
        # Меняем цвет рамки в зависимости от того, активен фокус или нет
        box_color = (34, 3, 4) if self.active else (150, 150, 150) # dred или серый
        
        # Рисуем подложку (белый прямоугольник) и рамку
        #pygame.draw.rect(surf, (255, 255, 255), self.rect)
        #pygame.draw.rect(surf, box_color, self.rect, 2) # Толщина рамки 2 пикселя

        current_time = pygame.time.get_ticks()
        cool_box(current_time)
        # Рендерим текст
        
        
        # Ограничиваем область отображения текста, чтобы он не вылезал за рамку поля
        # Если текст длиннее поля, сдвигаем его влево (показываем конец строки)
        text_width = self.text_surf.get_width()
        max_visible_width = self.rect.width - 20
        
        text_x = self.rect.x + 10

        # Рисуем текст на экране
        text_y = self.rect.y + (self.rect.height // 2 - self.text_surf.get_height() // 2) -5
        surf.blit(self.text_surf, (text_x, text_y))

        # Логика мигания и отрисовки курсора (каретки)
        if current_time - self.last_cursor_toggle >= self.cursor_speed:
            self.cursor_visible = not self.cursor_visible
            self.last_cursor_toggle = current_time

        if self.active and self.cursor_visible:
            # Считаем координату X для палочки курсора
            cursor_x = text_x + text_width + 2
            cursor_y_start = text_y
            cursor_y_end = text_y + self.text_surf.get_height()
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
    def __init__(self, x, y, w, h,img=None):
        self.rect = pygame.Rect(x, y, w, h)
        self.enabled = True
        self.img = img
        # Настройки отображения нод (комнат)
        self.node_radius = 20
        self.grid_size = 120  # Расстояние между комнатами в пикселях

    def draw(self, surf, player):
        if not self.enabled:
            return
        if self.img == None:
            # 1. Рисуем подложку карты
            pygame.draw.rect(surf, (240, 230, 200), self.rect) # Песочный цвет
            pygame.draw.rect(surf, (100, 80, 60), self.rect, 3) # Рамка
        else:
            surf.blit(self.img,(0,0))
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

class AssetManager:
    def __init__(self, images_path='assets/images/',blank_path='assets/images/enemies/missingno.png'):
        self.images_path = images_path
        # Сразу загружаем дефолтную заглушку, чтобы не делать этого в try/except
        self.blank_img = pygame.image.load(blank_path)
        # Наш оперативный кэш: { "id_предмета": Surface }
        self.__cache = {}
        self.__enemies_cache = {}

    def get_image(self, path, item_name: str) -> pygame.Surface:
        # Если предмет уже есть в кэше — возвращаем моментально
        if path not in self.__cache:
            self.__cache[path] = {}
        if item_name in self.__cache[path]:
            return self.__cache[path][item_name]

        # Если предмета нет, загружаем ОДИН РАЗ с диска
        full_path = os.path.join(self.images_path, path, f"{item_name}.png")
        
        if os.path.exists(full_path):
            try:
                img = pygame.image.load(full_path).convert_alpha()
                self.__cache[path][item_name] = img
                return img
            except Exception as e:
                print(f"[AssetManager] Error reading file {item_name}: {e}")
        else:
            print(f"[AssetManager] Not found: {full_path}")

        # Если файла нет или он сломан — кэшируем заглушку, чтобы больше не долбиться в диск
        self.__cache[path][item_name] = self.blank_img
        return self.blank_img
    def get_enemy_image(self,enemy_name):
        if enemy_name in self.__enemies_cache:
            return self.__enemies_cache[enemy_name]