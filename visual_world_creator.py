import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import json, ast

try:
    from rpnovel_engine import World, Location, Item, Potion, Weapon, Enemy
except ImportError:
    messagebox.showwarning(
        "Внимание", 
        "Не удалось найти файл rpnovel_engine.py.\n"
        "Убедитесь, что этот скрипт лежит в той же папке!"
    )
    class Item: pass
    class Potion(Item): pass
    class Weapon(Item): pass
    class Enemy: pass
    class Location: pass
    class World: pass

class VisualWorldSDK:
    def __init__(self, root):
        self.root = root
        self.root.title("Visual world creator")
        self.root.geometry("1300x850")
        
        self.active_world = World(locations=[], name="Zero")
        self.current_location_idx = None

        self.setup_styles()
        self.create_widgets()
        
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

    def create_widgets(self):
        menubar = tk.Menu(self.root)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Новый мир", command=self.new_world)
        filemenu.add_command(label="Открыть файл", command=self.load_world)
        filemenu.add_command(label="Сохранить файл", command=self.save_world)
        filemenu.add_separator()
        filemenu.add_command(label="Выход", command=self.root.quit)
        menubar.add_cascade(label="Файл", menu=filemenu)
        self.root.config(menu=menubar)

        main_pane = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_pane.pack(fill=tk.BOTH, expand=True)

        left_frame = ttk.LabelFrame(main_pane, text=" Локации ", width=260)
        main_pane.add(left_frame, weight=1)

        self.loc_listbox = tk.Listbox(left_frame, bg="#2c2c2c", fg="white", selectbackground="#4a4a4a", font=("Consolas", 11))
        self.loc_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.loc_listbox.bind("<<ListboxSelect>>", self.on_location_select)

        btn_loc_frame = ttk.Frame(left_frame)
        btn_loc_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(btn_loc_frame, text="+ Добавить", command=self.add_location).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(btn_loc_frame, text="- Удалить", command=self.delete_location).pack(side=tk.RIGHT, fill=tk.X, expand=True)

        center_notebook = ttk.Notebook(main_pane)
        main_pane.add(center_notebook, weight=4)

        self.tab_main = ttk.Frame(center_notebook)
        center_notebook.add(self.tab_main, text="Параметры и Выходы")
        self.build_tab_main()

        self.tab_items = ttk.Frame(center_notebook)
        center_notebook.add(self.tab_items, text="Предметы локации")
        self.build_tab_items()

        self.tab_enemies = ttk.Frame(center_notebook)
        center_notebook.add(self.tab_enemies, text="Враги и Инвентарь")
        self.build_tab_enemies()

        self.tab_raw_json = ttk.Frame(center_notebook)
        center_notebook.add(self.tab_raw_json, text="JSON Код")
        self.build_tab_raw_json()

    def build_tab_main(self):
        info_frame = ttk.LabelFrame(self.tab_main, text=" Свойства Location ")
        info_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(info_frame, text="ID:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.ent_loc_id = ttk.Entry(info_frame)
        self.ent_loc_id.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        self.ent_loc_id.bind("<KeyRelease>", lambda e: self.update_location_meta())

        ttk.Label(info_frame, text="Имя:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.ent_loc_name = ttk.Entry(info_frame)
        self.ent_loc_name.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        self.ent_loc_name.bind("<KeyRelease>", lambda e: self.update_location_meta())

        ttk.Label(info_frame, text="Описание:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.NW)
        self.txt_loc_desc = tk.Text(info_frame, height=4, bg="#fdfdfd", wrap=tk.WORD)
        self.txt_loc_desc.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        self.txt_loc_desc.bind("<KeyRelease>", lambda e: self.update_location_meta())

        ttk.Label(info_frame, text="Флаги (JSON):").grid(row=3, column=0, padx=5, pady=5, sticky=tk.NW)
        self.txt_loc_flags = tk.Text(info_frame, height=3, bg="#fdfdfd", wrap=tk.WORD)
        self.txt_loc_flags.grid(row=3, column=1, sticky="ew", padx=5, pady=5)
        self.txt_loc_flags.bind("<KeyRelease>", lambda e: self.update_location_meta())

        exits_frame = ttk.LabelFrame(self.tab_main, text=" Переходы (exits) ")
        exits_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        directions = ["север", "юг", "восток", "запад", "spec"]
        self.exit_entries = {}
        for i, d in enumerate(directions):
            ttk.Label(exits_frame, text=f"Направление '{d}':").grid(row=i, column=0, padx=10, pady=4, sticky=tk.W)
            ent = ttk.Entry(exits_frame)
            ent.grid(row=i, column=1, sticky="ew", padx=10, pady=4)
            ent.bind("<KeyRelease>", lambda e: self.update_location_meta())
            self.exit_entries[d] = ent

    def build_tab_items(self):
        pane = ttk.PanedWindow(self.tab_items, orient=tk.HORIZONTAL)
        pane.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        left_f = ttk.LabelFrame(pane, text=" Предметы в локации ")
        pane.add(left_f, weight=1)

        self.items_listbox = tk.Listbox(left_f, bg="#333", fg="white")
        self.items_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.items_listbox.bind("<<ListboxSelect>>", self.on_item_select)

        if_buttons = ttk.Frame(left_f)
        if_buttons.pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(if_buttons, text="+ Создать", command=self.add_item).pack(side=tk.LEFT, expand=True, fill=tk.X)
        ttk.Button(if_buttons, text="- Удалить", command=self.delete_item).pack(side=tk.RIGHT, expand=True, fill=tk.X)

        right_f = ttk.LabelFrame(pane, text=" Параметры предмета ")
        pane.add(right_f, weight=2)

        ttk.Label(right_f, text="Класс объекта:").pack(anchor=tk.W, padx=10, pady=2)
        self.cb_item_class = ttk.Combobox(right_f, values=["Item (Обычный)", "Potion (Зелье)", "Weapon (Оружие)"], state="readonly")
        self.cb_item_class.pack(fill=tk.X, padx=10, pady=4)
        self.cb_item_class.bind("<<ComboboxSelected>>", self.on_item_class_change)

        ttk.Label(right_f, text="ID:").pack(anchor=tk.W, padx=10, pady=2)
        self.ent_item_id = ttk.Entry(right_f)
        self.ent_item_id.pack(fill=tk.X, padx=10, pady=2)
        self.ent_item_id.bind("<KeyRelease>", lambda e: self.update_selected_item())

        ttk.Label(right_f, text="Имя:").pack(anchor=tk.W, padx=10, pady=2)
        self.ent_item_name = ttk.Entry(right_f)
        self.ent_item_name.pack(fill=tk.X, padx=10, pady=2)
        self.ent_item_name.bind("<KeyRelease>", lambda e: self.update_selected_item())

        ttk.Label(right_f, text="Описание:").pack(anchor=tk.W, padx=10, pady=2)
        self.ent_item_desc = ttk.Entry(right_f)
        self.ent_item_desc.pack(fill=tk.X, padx=10, pady=2)
        self.ent_item_desc.bind("<KeyRelease>", lambda e: self.update_selected_item())

        self.f_potion = ttk.Frame(right_f)
        ttk.Label(self.f_potion, text="Сила исцеления (heal_power):").pack(side=tk.LEFT, padx=10)
        self.ent_heal = ttk.Entry(self.f_potion, width=10)
        self.ent_heal.pack(side=tk.LEFT)
        self.ent_heal.bind("<KeyRelease>", lambda e: self.update_selected_item())

        self.f_weapon = ttk.Frame(right_f)
        ttk.Label(self.f_weapon, text="Урон оружия (damage):").pack(side=tk.LEFT, padx=10)
        self.ent_dmg = ttk.Entry(self.f_weapon, width=10)
        self.ent_dmg.pack(side=tk.LEFT)
        self.ent_dmg.bind("<KeyRelease>", lambda e: self.update_selected_item())

    def build_tab_enemies(self):
        pane = ttk.PanedWindow(self.tab_enemies, orient=tk.HORIZONTAL)
        pane.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        left_f = ttk.LabelFrame(pane, text=" Список врагов ")
        pane.add(left_f, weight=1)

        self.enemy_listbox = tk.Listbox(left_f, bg="#333", fg="white")
        self.enemy_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.enemy_listbox.bind("<<ListboxSelect>>", self.on_enemy_select)

        ef_buttons = ttk.Frame(left_f)
        ef_buttons.pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(ef_buttons, text="+ Создать Enemy", command=self.add_enemy).pack(side=tk.LEFT, expand=True, fill=tk.X)
        ttk.Button(ef_buttons, text="- Удалить", command=self.delete_enemy).pack(side=tk.RIGHT, expand=True, fill=tk.X)

        right_pane = ttk.PanedWindow(pane, orient=tk.VERTICAL)
        pane.add(right_pane, weight=2)

        props_f = ttk.LabelFrame(right_pane, text=" Параметры Enemy ")
        right_pane.add(props_f, weight=1)

        ttk.Label(props_f, text="ID:").pack(anchor=tk.W, padx=10, pady=1)
        self.ent_en_id = ttk.Entry(props_f)
        self.ent_en_id.pack(fill=tk.X, padx=10, pady=1)
        self.ent_en_id.bind("<KeyRelease>", lambda e: self.update_selected_enemy())

        ttk.Label(props_f, text="Имя:").pack(anchor=tk.W, padx=10, pady=1)
        self.ent_en_name = ttk.Entry(props_f)
        self.ent_en_name.pack(fill=tk.X, padx=10, pady=1)
        self.ent_en_name.bind("<KeyRelease>", lambda e: self.update_selected_enemy())

        ttk.Label(props_f, text="HP:").pack(anchor=tk.W, padx=10, pady=1)
        self.ent_en_hp = ttk.Entry(props_f)
        self.ent_en_hp.pack(fill=tk.X, padx=10, pady=1)
        self.ent_en_hp.bind("<KeyRelease>", lambda e: self.update_selected_enemy())

        ttk.Label(props_f, text="Урон:").pack(anchor=tk.W, padx=10, pady=1)
        self.ent_en_dmg = ttk.Entry(props_f)
        self.ent_en_dmg.pack(fill=tk.X, padx=10, pady=1)
        self.ent_en_dmg.bind("<KeyRelease>", lambda e: self.update_selected_enemy())

        ttk.Label(props_f, text="Предыстория (Промпт):").pack(anchor=tk.W, padx=10, pady=1)
        self.txt_en_story = tk.Text(props_f, height=3, bg="#fafafa", wrap=tk.WORD)
        self.txt_en_story.pack(fill=tk.X, padx=10, pady=1)
        self.txt_en_story.bind("<KeyRelease>", lambda e: self.update_selected_enemy())

        inv_f = ttk.LabelFrame(right_pane, text=" Инвентарь выбранного Enemy ")
        right_pane.add(inv_f, weight=1)

        inv_sub_pane = ttk.PanedWindow(inv_f, orient=tk.HORIZONTAL)
        inv_sub_pane.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        inv_left = ttk.Frame(inv_sub_pane)
        inv_sub_pane.add(inv_left, weight=1)

        self.enemy_inv_listbox = tk.Listbox(inv_left, bg="#444", fg="white")
        self.enemy_inv_listbox.pack(fill=tk.BOTH, expand=True)
        self.enemy_inv_listbox.bind("<<ListboxSelect>>", self.on_enemy_item_select)

        inv_btn_f = ttk.Frame(inv_left)
        inv_btn_f.pack(fill=tk.X, pady=2)
        ttk.Button(inv_btn_f, text="+ Добавить предмет", command=self.add_enemy_item).pack(side=tk.LEFT, expand=True, fill=tk.X)
        ttk.Button(inv_btn_f, text="- Удалить предмет", command=self.delete_enemy_item).pack(side=tk.RIGHT, expand=True, fill=tk.X)

        inv_right = ttk.Frame(inv_sub_pane)
        inv_sub_pane.add(inv_right, weight=1)

        ttk.Label(inv_right, text="Тип предмета:").pack(anchor=tk.W, padx=5)
        self.cb_en_item_class = ttk.Combobox(inv_right, values=["Item (Обычный)", "Potion (Зелье)", "Weapon (Оружие)"], state="readonly")
        self.cb_en_item_class.pack(fill=tk.X, padx=5, pady=2)
        self.cb_en_item_class.bind("<<ComboboxSelected>>", self.on_enemy_item_class_change)

        ttk.Label(inv_right, text="ID:").pack(anchor=tk.W, padx=5)
        self.ent_en_item_id = ttk.Entry(inv_right)
        self.ent_en_item_id.pack(fill=tk.X, padx=5, pady=2)
        self.ent_en_item_id.bind("<KeyRelease>", lambda e: self.update_enemy_item())

        ttk.Label(inv_right, text="Имя:").pack(anchor=tk.W, padx=5)
        self.ent_en_item_name = ttk.Entry(inv_right)
        self.ent_en_item_name.pack(fill=tk.X, padx=5, pady=2)
        self.ent_en_item_name.bind("<KeyRelease>", lambda e: self.update_enemy_item())

        ttk.Label(inv_right, text="Описание:").pack(anchor=tk.W, padx=5)
        self.ent_en_item_desc = ttk.Entry(inv_right)
        self.ent_en_item_desc.pack(fill=tk.X, padx=5, pady=2)
        self.ent_en_item_desc.bind("<KeyRelease>", lambda e: self.update_enemy_item())

        self.f_en_potion = ttk.Frame(inv_right)
        ttk.Label(self.f_en_potion, text="Лечение:").pack(side=tk.LEFT, padx=5)
        self.ent_en_heal = ttk.Entry(self.f_en_potion, width=8)
        self.ent_en_heal.pack(side=tk.LEFT)
        self.ent_en_heal.bind("<KeyRelease>", lambda e: self.update_enemy_item())

        self.f_en_weapon = ttk.Frame(inv_right)
        ttk.Label(self.f_en_weapon, text="Урон:").pack(side=tk.LEFT, padx=5)
        self.ent_en_dmg = ttk.Entry(self.f_en_weapon, width=8)
        self.ent_en_dmg.pack(side=tk.LEFT)
        self.ent_en_dmg.bind("<KeyRelease>", lambda e: self.update_enemy_item())

    def build_tab_raw_json(self):
        ttk.Label(self.tab_raw_json, text="Прямое редактирование JSON кода объекта World:").pack(anchor=tk.W, padx=10, pady=5)
        self.txt_raw_json = tk.Text(self.tab_raw_json, bg="#1e1e1e", fg="#d4d4d4", insertbackground="white", font=("Consolas", 10))
        self.txt_raw_json.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        btn_frame = ttk.Frame(self.tab_raw_json)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Button(btn_frame, text="Обновить JSON из текущего мира", command=self.sync_world_to_json_field).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Записать JSON в объект World", command=self.parse_json_field_to_world).pack(side=tk.LEFT, padx=5)

    def on_location_select(self, event):
        selection = self.loc_listbox.curselection()
        if not selection: return
        
        self.current_location_idx = selection[0]
        loc = self.active_world.locations[self.current_location_idx]

        self.ent_loc_id.delete(0, tk.END)
        self.ent_loc_id.insert(0, getattr(loc, "id", ""))
        
        self.ent_loc_name.delete(0, tk.END)
        self.ent_loc_name.insert(0, getattr(loc, "name", ""))

        self.txt_loc_desc.delete("1.0", tk.END)
        self.txt_loc_desc.insert("1.0", getattr(loc, "description", ""))

        self.txt_loc_flags.delete("1.0", tk.END)
        if hasattr(loc, "flags") and loc.flags:
            self.txt_loc_flags.insert("1.0", json.dumps(loc.flags, ensure_ascii=False))
        else:
            self.txt_loc_flags.insert("1.0", "{}")

        for d, entry in self.exit_entries.items():
            entry.delete(0, tk.END)
            entry.insert(0, loc.exits.get(d, ""))

        self.refresh_items_list()
        self.refresh_enemies_list()
        self.hide_item_dynamic_fields()
        self.hide_enemy_item_dynamic_fields()

    def update_location_meta(self):
        if self.current_location_idx is None: return
        loc = self.active_world.locations[self.current_location_idx]
        
        loc.id = self.ent_loc_id.get().strip()
        loc.name = self.ent_loc_name.get().strip()
        loc.description = self.txt_loc_desc.get("1.0", tk.END).strip()
        
        try:
            loc.special_flags = json.loads(self.txt_loc_flags.get("1.0", tk.END).strip() or "{}")
        except Exception:
            loc.special_flags = {}
        
        loc.exits = {}
        for d, entry in self.exit_entries.items():
            val = entry.get().strip()
            if val:
                loc.exits[d] = val
        
        self.loc_listbox.delete(self.current_location_idx)
        self.loc_listbox.insert(self.current_location_idx, loc.id)
        self.loc_listbox.select_set(self.current_location_idx)

    def refresh_items_list(self):
        self.items_listbox.delete(0, tk.END)
        if self.current_location_idx is None: return
        loc = self.active_world.locations[self.current_location_idx]
        if not hasattr(loc, "items"):
            loc.items = []
        for item in loc.items:
            self.items_listbox.insert(tk.END, f"[{type(item).__name__}] {item.name} ({item.id})")

    def hide_item_dynamic_fields(self):
        self.f_potion.pack_forget()
        self.f_weapon.pack_forget()

    def on_item_select(self, event):
        selection = self.items_listbox.curselection()
        if not selection: return
        
        item = self.active_world.locations[self.current_location_idx].items[selection[0]]
        
        self.ent_item_id.delete(0, tk.END)
        self.ent_item_id.insert(0, item.id)
        
        self.ent_item_name.delete(0, tk.END)
        self.ent_item_name.insert(0, item.name)
        
        self.ent_item_desc.delete(0, tk.END)
        self.ent_item_desc.insert(0, getattr(item, "desc", ""))

        self.hide_item_dynamic_fields()
        if isinstance(item, Potion):
            self.cb_item_class.set("Potion (Зелье)")
            self.f_potion.pack(fill=tk.X, pady=5)
            self.ent_heal.delete(0, tk.END)
            self.ent_heal.insert(0, str(getattr(item, "heal_power", 0)))
        elif isinstance(item, Weapon):
            self.cb_item_class.set("Weapon (Оружие)")
            self.f_weapon.pack(fill=tk.X, pady=5)
            self.ent_dmg.delete(0, tk.END)
            self.ent_dmg.insert(0, str(getattr(item, "damage", 0)))
        else:
            self.cb_item_class.set("Item (Обычный)")

    def on_item_class_change(self, event):
        selection = self.items_listbox.curselection()
        if not selection or self.current_location_idx is None: return
        
        idx = selection[0]
        loc = self.active_world.locations[self.current_location_idx]
        old_item = loc.items[idx]
        
        cls_type = self.cb_item_class.get()
        i_id = self.ent_item_id.get().strip() or old_item.id
        i_name = self.ent_item_name.get().strip() or old_item.name
        i_desc = self.ent_item_desc.get().strip() or getattr(old_item, "desc", "")

        if "Potion" in cls_type:
            loc.items[idx] = Potion(i_id, i_name, i_desc, 25)
        elif "Weapon" in cls_type:
            loc.items[idx] = Weapon(i_id, i_name, i_desc, 10)
        else:
            loc.items[idx] = Item(i_id, i_name, i_desc)
            
        self.refresh_items_list()
        self.items_listbox.select_set(idx)
        self.on_item_select(None)

    def update_selected_item(self):
        selection = self.items_listbox.curselection()
        if not selection: return
        
        idx = selection[0]
        item = self.active_world.locations[self.current_location_idx].items[idx]
        item.id = self.ent_item_id.get().strip()
        item.name = self.ent_item_name.get().strip()
        item.desc = self.ent_item_desc.get().strip()
        
        if isinstance(item, Potion):
            try: item.heal_power = int(self.ent_heal.get() or 0)
            except ValueError: pass
        elif isinstance(item, Weapon):
            try: item.damage = int(self.ent_dmg.get() or 0)
            except ValueError: pass

        self.items_listbox.delete(idx)
        self.items_listbox.insert(idx, f"[{type(item).__name__}] {item.name} ({item.id})")
        self.items_listbox.select_set(idx)

    def add_item(self):
        if self.current_location_idx is None: return
        new_obj = Item("item_id", "Новый предмет", "Описание")
        self.active_world.locations[self.current_location_idx].items.append(new_obj)
        self.refresh_items_list()
        self.items_listbox.select_set(tk.END)
        self.on_item_select(None)

    def delete_item(self):
        selection = self.items_listbox.curselection()
        if not selection: return
        del self.active_world.locations[self.current_location_idx].items[selection[0]]
        self.refresh_items_list()
        self.hide_item_dynamic_fields()

    def refresh_enemies_list(self):
        self.enemy_listbox.delete(0, tk.END)
        if self.current_location_idx is None: return
        loc = self.active_world.locations[self.current_location_idx]
        if not hasattr(loc, "enemies"):
            loc.enemies = []
        for idx, en in enumerate(loc.enemies):
            hp = en.gethp() if hasattr(en, "gethp") else getattr(en, "_Enemy__hp", 0)
            self.enemy_listbox.insert(tk.END, f"[{idx}] {en.name} (HP: {hp})")

    def on_enemy_select(self, event):
        selection = self.enemy_listbox.curselection()
        if not selection: return
        
        en = self.active_world.locations[self.current_location_idx].enemies[selection[0]]
        
        self.ent_en_id.delete(0, tk.END)
        self.ent_en_id.insert(0, getattr(en, "id", ""))
        self.ent_en_name.delete(0, tk.END)
        self.ent_en_name.insert(0, getattr(en, "name", ""))
        
        hp = en.gethp() if hasattr(en, "gethp") else getattr(en, "_Enemy__hp", 0)
        self.ent_en_hp.delete(0, tk.END)
        self.ent_en_hp.insert(0, str(hp))
        
        self.ent_en_dmg.delete(0, tk.END)
        self.ent_en_dmg.insert(0, str(getattr(en, "dmg", 0)))
        
        self.txt_en_story.delete("1.0", tk.END)
        self.txt_en_story.insert("1.0", getattr(en, "backstory", ""))

        self.refresh_enemy_inventory_list()
        self.hide_enemy_item_dynamic_fields()

    def update_selected_enemy(self):
        selection = self.enemy_listbox.curselection()
        if not selection: return
        
        idx = selection[0]
        en = self.active_world.locations[self.current_location_idx].enemies[idx]
        
        en.id = self.ent_en_id.get().strip()
        en.name = self.ent_en_name.get().strip()
        try: en.dmg = int(self.ent_en_dmg.get() or 0)
        except ValueError: pass
        en.backstory = self.txt_en_story.get("1.0", tk.END).strip()
        
        try:
            hp_val = int(self.ent_en_hp.get() or 0)
            if hasattr(en, "_Enemy__hp"): en._Enemy__hp = hp_val
            elif hasattr(en, "hp"): en.hp = hp_val
        except Exception:
            pass

        hp = en.gethp() if hasattr(en, "gethp") else getattr(en, "_Enemy__hp", 0)
        self.enemy_listbox.delete(idx)
        self.enemy_listbox.insert(idx, f"[{idx}] {en.name} (HP: {hp})")
        self.enemy_listbox.select_set(idx)

    def add_enemy(self):
        if self.current_location_idx is None: return
        new_enemy = Enemy("enemy_id", "Новый враг", 50, 5, "Описание")
        if not hasattr(new_enemy, "inventory"):
            new_enemy.inventory = []
        self.active_world.locations[self.current_location_idx].enemies.append(new_enemy)
        self.refresh_enemies_list()
        self.enemy_listbox.select_set(tk.END)
        self.on_enemy_select(None)

    def delete_enemy(self):
        selection = self.enemy_listbox.curselection()
        if not selection: return
        del self.active_world.locations[self.current_location_idx].enemies[selection[0]]
        self.refresh_enemies_list()
        self.enemy_inv_listbox.delete(0, tk.END)

    def refresh_enemy_inventory_list(self):
        self.enemy_inv_listbox.delete(0, tk.END)
        e_sel = self.enemy_listbox.curselection()
        if not e_sel: return
        
        en = self.active_world.locations[self.current_location_idx].enemies[e_sel[0]]
        if not hasattr(en, "inventory") or en.inventory is None:
            en.inventory = []
            
        for item in en.inventory:
            self.enemy_inv_listbox.insert(tk.END, f"[{type(item).__name__}] {item.name}")

    def hide_enemy_item_dynamic_fields(self):
        self.f_en_potion.pack_forget()
        self.f_en_weapon.pack_forget()

    def on_enemy_item_select(self, event):
        e_sel = self.enemy_listbox.curselection()
        i_sel = self.enemy_inv_listbox.curselection()
        if not e_sel or not i_sel: return
        
        item = self.active_world.locations[self.current_location_idx].enemies[e_sel[0]].inventory[i_sel[0]]
        
        self.ent_en_item_id.delete(0, tk.END)
        self.ent_en_item_id.insert(0, item.id)
        self.ent_en_item_name.delete(0, tk.END)
        self.ent_en_item_name.insert(0, item.name)
        self.ent_en_item_desc.delete(0, tk.END)
        self.ent_en_item_desc.insert(0, getattr(item, "desc", ""))

        self.hide_enemy_item_dynamic_fields()
        if isinstance(item, Potion):
            self.cb_en_item_class.set("Potion (Зелье)")
            self.f_en_potion.pack(fill=tk.X, pady=2)
            self.ent_en_heal.delete(0, tk.END)
            self.ent_en_heal.insert(0, str(getattr(item, "heal_power", 0)))
        elif isinstance(item, Weapon):
            self.cb_en_item_class.set("Weapon (Оружие)")
            self.f_en_weapon.pack(fill=tk.X, pady=2)
            self.ent_en_dmg.delete(0, tk.END)
            self.ent_en_dmg.insert(0, str(getattr(item, "damage", 0)))
        else:
            self.cb_en_item_class.set("Item (Обычный)")

    def on_enemy_item_class_change(self, event):
        e_sel = self.enemy_listbox.curselection()
        i_sel = self.enemy_inv_listbox.curselection()
        if not e_sel or not i_sel: return
        
        en = self.active_world.locations[self.current_location_idx].enemies[e_sel[0]]
        idx = i_sel[0]
        old_item = en.inventory[idx]
        
        cls_type = self.cb_en_item_class.get()
        i_id = self.ent_en_item_id.get().strip() or old_item.id
        i_name = self.ent_en_item_name.get().strip() or old_item.name
        i_desc = self.ent_en_item_desc.get().strip() or getattr(old_item, "desc", "")

        if "Potion" in cls_type:
            en.inventory[idx] = Potion(i_id, i_name, i_desc, 25)
        elif "Weapon" in cls_type:
            en.inventory[idx] = Weapon(i_id, i_name, i_desc, 10)
        else:
            en.inventory[idx] = Item(i_id, i_name, i_desc)
            
        self.refresh_enemy_inventory_list()
        self.enemy_inv_listbox.select_set(idx)
        self.on_enemy_item_select(None)

    def update_enemy_item(self):
        e_sel = self.enemy_listbox.curselection()
        i_sel = self.enemy_inv_listbox.curselection()
        if not e_sel or not i_sel: return
        
        idx = i_sel[0]
        item = self.active_world.locations[self.current_location_idx].enemies[e_sel[0]].inventory[idx]
        item.id = self.ent_en_item_id.get().strip()
        item.name = self.ent_en_item_name.get().strip()
        item.desc = self.ent_en_item_desc.get().strip()
        
        if isinstance(item, Potion):
            try: item.heal_power = int(self.ent_en_heal.get() or 0)
            except ValueError: pass
        elif isinstance(item, Weapon):
            try: item.damage = int(self.ent_en_dmg.get() or 0)
            except ValueError: pass

        self.enemy_inv_listbox.delete(idx)
        self.enemy_inv_listbox.insert(idx, f"[{type(item).__name__}] {item.name}")
        self.enemy_inv_listbox.select_set(idx)

    def add_enemy_item(self):
        e_sel = self.enemy_listbox.curselection()
        if not e_sel: return
        en = self.active_world.locations[self.current_location_idx].enemies[e_sel[0]]
        new_obj = Item("loot_id", "Новый лут", "Описание")
        en.inventory.append(new_obj)
        self.refresh_enemy_inventory_list()
        self.enemy_inv_listbox.select_set(tk.END)
        self.on_enemy_item_select(None)

    def delete_enemy_item(self):
        e_sel = self.enemy_listbox.curselection()
        i_sel = self.enemy_inv_listbox.curselection()
        if not e_sel or not i_sel: return
        del self.active_world.locations[self.current_location_idx].enemies[e_sel[0]].inventory[i_sel[0]]
        self.refresh_enemy_inventory_list()
        self.hide_enemy_item_dynamic_fields()

    def sync_world_to_json_field(self):
        import base64
        try:
            if hasattr(self.active_world, "to_dict"):
                world_dict = self.active_world.to_dict()
                if isinstance(world_dict, bytes):
                    world_dict = world_dict.decode('utf-8')
                self.txt_raw_json.delete("1.0", tk.END)
                self.txt_raw_json.insert("1.0", json.loads(base64.b64decode(world_dict).decode('utf-8')))
            else:
                messagebox.showerror("Ошибка", "Метод to_dict не найден у объекта World.")
        except Exception as e:
            messagebox.showerror("Ошибка синхронизации", str(e))

    def parse_json_field_to_world(self):
        import base64
        raw_text = self.txt_raw_json.get("1.0", tk.END).strip()
        if not raw_text: return
        try:
            if hasattr(World, "from_dict"):
                dic = ast.literal_eval(raw_text)
                self.active_world = World.from_dict(
                    base64.b64encode(json.dumps(dic).encode('utf-8')).decode('utf-8'))
                self.current_location_idx = None
                self.refresh_location_list()
                messagebox.showinfo("Успех", "Объект World успешно обновлен из JSON-текста.")
            else:
                messagebox.showerror("Ошибка", "Метод from_dict не найден в классе World.")
        except Exception as e:
            messagebox.showerror("Ошибка парсинга", f"Не удалось преобразовать текст в объект: {e}")

    def add_location(self):
        win = tk.Toplevel(self.root)
        win.title("Новая локация")
        win.geometry("320x120")
        ttk.Label(win, text="Введите ID локации (строка):").pack(pady=5)
        ent = ttk.Entry(win)
        ent.pack(pady=5)
        ent.focus()

        def confirm():
            lid = ent.get().strip()
            if lid:
                new_loc_obj = Location(id=lid, name="Новая Зона", description="Описание...", exits={})
                new_loc_obj.flags = {}
                new_loc_obj.items = []
                new_loc_obj.enemies = []
                self.active_world.locations.append(new_loc_obj)
                self.refresh_location_list()
                win.destroy()
        ttk.Button(win, text="Создать", command=confirm).pack(pady=5)

    def delete_location(self):
        if self.current_location_idx is not None:
            del self.active_world.locations[self.current_location_idx]
            self.current_location_idx = None
            self.refresh_location_list()

    def refresh_location_list(self):
        self.loc_listbox.delete(0, tk.END)
        for loc in self.active_world.locations:
            self.loc_listbox.insert(tk.END, loc.id)

    def new_world(self):
        self.active_world = World(locations=[], name="Zero")
        self.current_location_idx = None
        self.refresh_location_list()

    def load_world(self):
        path = filedialog.askopenfilename(filetypes=[("JSON мира", "*")])
        if not path: return
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
                if hasattr(World, "from_dict"):
                    self.active_world = World.from_dict(content)
                else:
                    data = json.loads(content)
                    locs = [Location.from_dict(l) for l in data.get("locations", [])]
                    self.active_world = World(locations=locs, name=data.get("name", "Zero"))
            self.current_location_idx = None
            self.refresh_location_list()
            messagebox.showinfo("Успех", "Объект World восстановлен из файла.")
        except Exception as e:
            messagebox.showerror("Ошибка загрузки", str(e))

    def save_world(self):
        path = filedialog.asksaveasfilename(defaultextension=".wld", filetypes=[("World files", "*.wld")])
        if not path: return
        try:
            if hasattr(self.active_world, "to_dict"):
                world_data = self.active_world.to_dict()
                if isinstance(world_data, bytes):
                    world_data = world_data.decode('utf-8')
                
                with open(path, "w", encoding="utf-8") as f:
                    if isinstance(world_data, str):
                        f.write(world_data)
                    else:
                        json.dump(world_data, f, ensure_ascii=False, indent=4)
                messagebox.showinfo("Успех", "Мир успешно экспортирован.")
            else:
                messagebox.showerror("Ошибка", "Метод to_dict не обнаружен у объекта World.")
        except Exception as e:
            messagebox.showerror("Ошибка сохранения", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = VisualWorldSDK(root)
    root.mainloop()