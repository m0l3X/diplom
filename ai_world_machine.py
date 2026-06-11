import json
import base64
import requests

# Импортируем твои классы из основного файла (замени 'game_main' на имя своего файла)
from rpnovel_engine import RPGNovel, World, Location, Item, Weapon, Potion, Enemy, nozh, palka, galo

# Настройки твоего локального сервера
SERVER_IP = "http://192.168.1.250:8080"  # Пропиши сюда свой IP и порт локальной LM
MODEL_NAME = "meta-llama-3-8b-instruct"  # Имя модели в твоем сервере (если требуется, иначе можно "local")

SYSTEM_PROMPT = """Ты — профессиональный геймдизайнер RPG-новелл и сценарист. Твоя задача — пошагово генерировать связный, интересный игровой мир по текстовому ТЗ пользователя.
Игра написана на Python (Pygame). Мир состоит из объектов Location, соединенных сторонами света (север, юг, восток, запад).

На каждом шагу генерации тебе присылают:
1. Текущую карту мира (список уже созданных ID локаций и их связей).
2. Задачу (какую локацию нужно создать или развить, какой сюжетный узел добавить).

В ответ ты ДОЛЖЕН вернуть СТРОГИЙ JSON-объект, содержащий информацию для создания ОДНОЙ новой локации, а также предметов и NPC внутри неё.

ФОРМАТ ВЫХОДНОГО JSON (Никакого лишнего текста вокруг, только валидный JSON, без разметки ```json):
{
  "target_parent_id": "ID_существующей_локации_к_которой_подключаем_новую",
  "direction_from_parent": "направление_от_старой_к_новой (север/юг/восток/запад)",
  "location": {
    "id": "уникальный_id_строкой",
    "name": "Название локации для UI",
    "description": "Атмосферное описание локации для игрока"
  },
  "items": [
    {
      "id": "item_id_1",
      "name": "Название",
      "description": "Описание предмета",
      "type": "обычный" 
    },
    {
      "id": "potion_id_1",
      "name": "Лечебное зелье",
      "description": "Восстанавливает HP",
      "type": "зелье",
      "heal_power": 50
    },
    {
      "id": "weapon_id_1",
      "name": "Ржавая арматура",
      "description": "Оружие ближнего боя",
      "type": "оружие",
      "damage": 15
    }
  ],
  "enemies": [
    {
      "name": "Имя_NPC_или_Врага",
      "hp": 50,
      "damage": 10,
      "backstory": "Системный промпт ИИ для этого персонажа. Сюда зашиваются ROLE, STAGE, FACTS, IF-THEN и GOAL, аналогично Дяде Юре и Немо.",
      "inventory": [
         {"id": "key_1", "name": "Ключ", "description": "Ключ от двери", "type": "обычный"}
      ]
    }
  ]
}

ПРАВИЛА ГЕНЕРАЦИИ:
1. Выбирай 'target_parent_id' только из тех, которые РЕАЛЬНО существуют в текущей карте.
2. Следи за балансом: предметы и враги должны подходить под атмосферу локации. Бэкстори врагов (NPC) должна быть детальной.
3. Отвечай ТОЛЬКО чистым JSON-объектом."""


def send_generation_request(prompt_message):
    """Твой метод, адаптированный под генерацию структуры без сохранения истории"""
    try:
        response = requests.post(
            f"{SERVER_IP}/v1/chat/completions",
            headers={"Content-Type": "application/json"},
            json={
                #"model": MODEL_NAME,
                "max_tokens": 1500, # Под генерацию локаций лучше взять побольше
                "temperature": 0.7,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt_message}
                ]   
            },
            timeout=30 # Для локалки генерация JSON может занять чуть больше времени, увеличим таймаут
        )
        
        if not response.ok:
            print(f"Ошибка сервера: {response.status_code} - {response.text}")
            return None
            
        reply = response.json()["choices"][0]["message"]["content"]
        return reply
    except Exception as e:
        print(f"Ошибка запроса к локальной LM: {str(e)}")
        return None


def get_current_map_state(world: World):
    """Сборщик плоской карты для контекста ИИ"""
    state = {}
    for loc in world.locations:
        state[loc.id] = {
            "name": loc.name,
            "exits": loc.exits
        }
    return state


def apply_ai_commands_to_novel(novel: RPGNovel, ai_json: dict):
    """Автоматический парсинг JSON с защитой от геометрических конфликтов"""
    world = novel.player.current_world
    
    loc_data = ai_json["location"]
    loc_id = loc_data["id"]
    parent_id = ai_json["target_parent_id"]
    requested_dir = ai_json["direction_from_parent"].lower().strip()
    
    # 1. Проверяем существование родительской локации
    parent_loc = world.get_location(parent_id)
    if not parent_loc:
        print(f">> [WorldMachine][Ошибка]: Родительская локация '{parent_id}' не найдена. Пропуск.")
        return

    # Все доступные направления в игре
    ALL_DIRECTIONS = ["север", "восток", "юг", "запад"]
    
    counterpart_dirs = {
        "север": "юг",
        "юг": "север",
        "восток": "запад",
        "запад": "восток"
    }
    
    # Сдвиги координат для проверки наложений на сетке
    DIR_OFFSETS = {
        "север": (0, -1),
        "юг": (0, 1),
        "восток": (1, 0),
        "запад": (-1, 0)
    }

    # Считаем текущую карту координат (передаем все локации как посещенные, чтобы просчитать весь мир)
    all_loc_ids = set([loc.id for loc in world.locations])
    grid_positions = world.generate_map_positions(all_loc_ids)
    
    # Координаты родительской комнаты
    parent_x, parent_y = grid_positions.get(parent_id, (0, 0))
    
    final_dir = requested_dir
    
    # --- АЛГОРИТМ ПРОВЕРКИ И РАЗРЕШЕНИЯ КОНФЛИКТОВ ---
    
    # Функция для проверки: свободны ли координаты на сетке и свободен ли физический выход у родителя
    def is_direction_conflicting(direction):
        # Проверка 1: Занят ли этот выход у родителя текстовой ссылкой?
        if direction in parent_loc.exits:
            return True
            
        # Проверка 2: Будет ли наложение на сетке (координаты уже заняты другой комнатой)?
        dx, dy = DIR_OFFSETS.get(direction, (0, 0))
        target_coords = (parent_x + dx, parent_y + dy)
        if target_coords in grid_positions.values():
            return True
            
        return False

    # Если ИИ запросил направление с конфликтом, ищем замену
    if is_direction_conflicting(final_dir):
        print(f">> [WorldMachine][Конфликт]: Направление '{final_dir}' от комнаты '{parent_id}' занято или вызовет наложение нод!")
        
        found_backup = False
        # Перебираем направления по часовой стрелке, начиная с севера
        for backup_dir in ALL_DIRECTIONS:
            if not is_direction_conflicting(backup_dir):
                final_dir = backup_dir
                found_backup = True
                print(f">> [WorldMachine][Фикс]: Автоматически перенаправлено на свободное направление: '{final_dir}'")
                break
                
        if not found_backup:
            print(f">> [WorldMachine][Варнинг]: У комнаты '{parent_id}' вообще нет свободных выходов! Пропуск генерации.")
            return

    # --- КОНЕЦ ПРОВЕРКИ ---

    # 2. Строим комнату с уже подтвержденным безопасным направлением final_dir
    new_location = Location(
        id=loc_id, 
        name=loc_data["name"], 
        description=loc_data["description"], 
        exits={counterpart_dirs[final_dir]: parent_id}
    )
    world.locations.append(new_location)
    
    # Связываем родителя с новой комнатой
    parent_loc.exits[final_dir] = loc_id

    # 3. Наполняем шмотом (с учетом твоего фикса на None в конструкторе)
    for item in ai_json.get("items", []):
        i_type = item["type"]
        if i_type == "оружие":
            new_item = Weapon(item["id"], item["name"], item["description"], item["damage"])
        elif i_type == "зелье":
            new_item = Potion(item["id"], item["name"], item["description"], item["heal_power"])
        else:
            new_item = Item(item["id"], item["name"], item["description"])
        new_location.items.append(new_item)

    # 4. Сажаем NPC
    for enemy_data in ai_json.get("enemies", []):
        new_enemy = Enemy(
            enemy_data["name"], 
            enemy_data["hp"], 
            enemy_data["damage"], 
            enemy_data["backstory"]
        )
        for e_item in enemy_data.get("inventory", []):
            ei_type = e_item["type"]
            if ei_type == "оружие":
                new_e_item = Weapon(e_item["id"], e_item["name"], e_item["description"], e_item["damage"])
            elif ei_type == "зелье":
                new_e_item = Potion(e_item["id"], e_item["name"], e_item["description"], e_item["heal_power"])
            else:
                new_e_item = Item(e_item["id"], e_item["name"], e_item["description"])
            new_enemy.inventory.append(new_e_item)
            
        new_location.enemies.append(new_enemy)

    print(f">> [WorldMachine]: Локация '{new_location.name}' ({loc_id}) успешно добавлена на {final_dir} от '{parent_id}'.")


if __name__ == "__main__":
    novel = RPGNovel("Максон")
    novel.player.inventory.extend([palka, galo])
    novel.player.location = "start"
    
    world = World([Location("start", "Старт", "Старт твоего приключения!", {}, [])])
    novel.player.current_world = world
    
    print("=" * 50)
    print(" WORLD MACHINE СВЯЗАНА С ЛОКАЛЬНЫМ СЕРВЕРОМ")
    print("=" * 50)
    
    theme = input("Задай сеттинг (например: Киберпанк-Шанырак или Метро 2033): ")
    steps_count = int(input("Сколько комнат вырастить автоматически? \n > "))
    
    for step in range(steps_count):
        print(f"\nГенерируем комнату {step + 1}/{steps_count}...")
        
        current_map = get_current_map_state(world)
        
        user_prompt = f"""
        Общий сеттинг мира: {theme}
        Текущая карта мира: {json.dumps(current_map, ensure_ascii=False)}
        
        Задание: Выбери один существующий ID из карты, найди у него свободное направление и сгенерируй туда новую локацию в формате JSON.
        """
        
        raw_response = send_generation_request(user_prompt)
        
        if not raw_response:
            print("Локальная LM выдала пустой ответ или упала в таймаут. Пропускаем.")
            continue
            
        try:
            # Защита от дебила: некоторые локалки всё равно могут обернуть ответ в ```json ... ```
            clean_json = raw_response.strip()
            if clean_json.startswith("```"):
                clean_json = clean_json.split("\n", 1)[1].rsplit("```", 1)[0].strip()
                
            ai_data = json.loads(clean_json)
            apply_ai_commands_to_novel(novel, ai_data)
            
        except Exception as e:
            print(f"Крит при парсинге ответа ИИ: {e}")
            print(f"Что выдала модель:\n{raw_response}")
            continue

    print("\n=== ВСЁ ГОТОВО ===")
    print("Лови base64 дамп сгенерированного мира для сейва:")
    print(world.to_dict())
    
    with open("generated_world.txt", "w", encoding="utf-8") as f:
        f.write(world.to_dict())
    print("Сейв также улетел в 'generated_world.txt'")