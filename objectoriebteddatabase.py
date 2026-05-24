import json
import os

class Database():
    def __init__(self, filename):
        self.filename = filename
        self.load_db()

    def load_db(self):

        self.db = {}
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r", encoding="utf-8") as f:
                    self.db = json.load(f)
                print("self.db loaded from file")
            except:
                print("self.db returned to existence")
                self.db = {
                    "Users" : {
                        "1" : {"name" : "admin", "pass":"someshit"}
                    }
                }
        else:
            self.db = {
                "Users" : {
                    "1" : {"name" : "admin", "pass":"someshit"}
                }
            }
    def force_insert(self, collection, id, data):
        self.db[collection][id] = data
        print("succ")
    def force_append(self, collection, data):
        self.db[collection][str(int(list(self.db[collection].keys())[-1])+1)] = data
        return str(int(list(self.db[collection].keys())[-1])+1)


    def save_db(self):

        try:
            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump(self.db, f, ensure_ascii=False, indent=4)
                print("saved")
        except Exception as e:
            print(f"Error saving self.db: {e}")

    def handle(self, cmd):
    
        cmd = cmd.split(' ')
        if not cmd: return
        match cmd:
            case ["CREATE", "COLLECTION", name]:
                if(name not in self.db.keys()):
                    self.db[name] = {
                        "0":{}
                    }
                    self.save_db()
            case ["SHOW", "COLLECTIONS"]:
                print(list(self.db.keys()))
                return list(self.db.keys())
            case ["INSERT", collection, id, data]:
                self.db[collection][id] = json.loads(data)
                print("succ")
            case ["APPEND", collection, data]:
                self.db[collection][str(int(list(self.db[collection].keys())[-1])+1)] = json.loads(data)
                return str(int(list(self.db[collection].keys())[-1])+1)
                #print(json.loads(data))
            case ["DATAAPPEND", collection, id, data]:
                self.db[collection][id].update(json.loads(data))
            case ["EXIT"]:
                return 
            case ["FIND", collection, path, value]:
                for obj in self.db[collection]:
                    if path not in self.db[collection][obj].keys():
                        continue
                    if self.db[collection][obj][path] == value:
                        #print(self.db[collection][obj])
                        return self.db[collection][obj], obj
                return "Fuck you", ""
            case ["GET", collection, obj, path]:
                try:
                    if self.db[collection][obj][path]:
                        #print(self.db[collection][obj])
                        return self.db[collection][obj][path]
                    else: return "Fuck you"
                except:
                    return "Fuck you"
            case ["GETIDTREE", collection, obj]:
                try:
                    if self.db[collection][obj]:
                        #print(self.db[collection][obj])
                        return self.db[collection][obj]
                    else: return "Fuck you"
                except:
                    return "Fuck you"
            case ["DELETE", collection, obj]:
                del self.db[collection][obj]
            case ["SAVE"]:
                self.save_db()
            case ["LOAD"]:
                self.load_db()
            case _:
                print(f"unknown command: {cmd}")
    if __name__ == "main":
        while True:
            com = input("nosql > ")
            handle(com)