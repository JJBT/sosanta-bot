import json
import random
from collections import defaultdict

from constants import DATA_PATH, EXCEPTIONS, USER_NAMES


def read_json(path: str) -> dict:
    with open(path, 'r') as f:
        return json.load(f)


def save_json(data: dict, path: str):
    with open(path, 'w') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def shuffle_users():
    data = defaultdict(dict)
    user_names = USER_NAMES.copy()
    senders = list()
    sender = USER_NAMES[0]
    while len(senders) < len(USER_NAMES) - 1:
        possible_recipients = [
            name for name in user_names
            if name != sender and name not in senders and {name, sender} not in EXCEPTIONS
        ]
        recipient = random.choice(possible_recipients)
        senders.append(sender)
        data[sender]['recipient'] = recipient
        sender = recipient

    data[sender]['recipient'] = senders[0]
    save_json(data, DATA_PATH)
