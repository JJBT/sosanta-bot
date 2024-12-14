import json
import random
from collections import defaultdict

USER_NAMES = [
    'lqrhy3',
    'Vladmir077',
    # 'backspace3'
]

EXCEPTIONS = [
    # {'lqrhy3', 'backspace3'},
]

DATA_PATH = 'data.json'


def read_json(path: str) -> dict:
    with open(path, 'r') as f:
        return json.load(f)


def save_json(data: dict, path: str):
    with open(path, 'w') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def shuffle_users():
    data = defaultdict(dict)
    user_names = USER_NAMES.copy()
    for user_name in USER_NAMES:
        possible_recipients = [name for name in user_names if name != user_name and {name, user_name} not in EXCEPTIONS]
        recipient = random.choice(possible_recipients)
        user_names.remove(recipient)
        print(user_name, possible_recipients, recipient)
        data[user_name]['recipient'] = recipient

    save_json(data, DATA_PATH)
