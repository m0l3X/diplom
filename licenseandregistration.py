cuser = ""
# Auth and shit
def hashstr(st):
    return hashlib.sha256(st.encode('utf-8')).hexdigest()
import objectoriebteddatabase as OOPdb
db = OOPdb.Database("player_database.json")
while True:
    db.handle("LOAD")
    print("1. Регистрация | 2. Вход | 3. Выход | 4. Сброс пароля | 5. Удалить аккаунт")
    if(cuser != ""):
        print(f"Current user: {cuser}")
    choice = input("Выбор: ")

    match choice:
        case "1":
            login = input("Придумайте логин: ")
            pwd = input("Придумайте пароль: ")
            if(len(pwd) < 6):
                print("Слишком короткий пароль, сделайте его длиннее")
                continue
            secret = input("Кого вы больше всех ненавидите? (для восстановления пароля): ")

            # 1. Проверяем, нет ли уже такого логина в БД (чтобы не было дубликатов)
            user,id = db.handle(f"FIND Users name {login}")
            if user != "Fuck you":
                print("Логин уже занят!")
                continue

            # 2. ХЭШИРУЕМ ПАРОЛЬ! НЕБЕЗОПАСНО!!!!!!!!!!!!!! ДАННЫЕ МОГУТ ПЕРЕХВАТИТЬ ЗЛЫЕ АРМАНЫ 
            hashed_pwd = hashstr(pwd)

            # 3. Сохраняем в БД
            db.handle('APPEND Users {' + f'"name":"{login}","pass":"{hashed_pwd}","secret":"{hashstr(secret)}"' + '}')
            db.handle("SAVE")
            print("✅ Успешная регистрация!")

        case "2":
            login = input("Логин: ")
            pwd = input("Пароль: ")
            user,id = db.handle(f"FIND Users name {login}")
            if user == "Fuck you":
                print("Неверно имя пользователя или пароль")
                continue
            pw = db.handle(f'GET Users {id} pass')
            if(hashstr(pwd) == pw):
                cuser = db.handle(f'GET Users {id} name')
                init_game()
                break
            else:
                print("Неверно имя пользователя или пароль")

        case "3":
            raise Exception("Ха, думал сможешь обойти систему и выйти в игру без логина? лови эту ошибку")
        case "4":
            login = input("Логин: ")
            sec = input("Кого вы больше всех ненавидите?: ")
            user,id = db.handle(f"FIND Users name {login}")
            
            if user == "Fuck you":
                print("Неверно имя пользователя")
                continue
            sc = db.handle(f'GET Users {id} secret')
            if(sc == "Fuck you"):
                print("К данному пользователю не привязано секретное слово для сброса пароля...")
                continue
            if(hashstr(sec) == sc):
                print("Правильно. Так им и надо. \n Введите новый пароль: ")
                name = db.handle(f"GET Users {id} name")
                pwd = input()
                cmd = f'INSERT Users {id} '+ '{' + f'"name":"{name}","pass":"{hashstr(pwd)}","secret":"{hashstr(sec)}"' + '}'
                cmd2 = f'INSERT Users {id} {{"name":"{name}","pass":"{hashstr(pwd)}","secret":"{hashstr(sec)}"}}'
                db.handle(cmd2)
                print("Пользователь перезаписан")
                db.handle("SAVE")
            else:
                print("Ложь!")
        case "5":
            login = input("Логин: ")
            pwd = input("Пароль: ")
            user,id = db.handle(f"FIND Users name {login}")
            if user == "Fuck you":
                print("Неверно имя пользователя или пароль")
                continue
            pw = db.handle(f'GET Users {id} pass')
            if(hashstr(pwd) == pw):
                db.handle(f"DELETE Users {id}")
                db.handle("SAVE")
                print("succ")
            else:
                print("Неверно имя пользователя или пароль")
