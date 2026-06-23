import json
onlymalex = {
    "trls": {
        "malex": {
            "X":0,
            "Y":0,
            "T":0,
            "ANIM":0
        }
    }
}
onlybg = {
    "trls": {
        "bg": {
            "X":0,
            "Y":0,
            "T":0,
            "ANIM":0
        }
    }
}
some = {
    "trls": {
        "malex": {
            "X":1000,
            "Y":0,
            "T":0,
            "ANIM":0
        },
        "bg": {
            "X":1000,
            "Y":0,
            "T":0,
            "ANIM":0
        }
    },
    'locked': 'gift',
    "locked_specialmsg":"Ещё рано начинать праздник, твой РОДИТЕЛЬ не дал тебе подарок..."
}
print(json.dumps(onlybg))