import json
import os
from typing import Dict, Generator, List, Optional

from models import Message


def all_messages(root_dir: str) -> Generator[Message, None, None]:
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.startswith("message_") and file.endswith(".json"):
                with open(os.path.join(root, file), "r") as f:
                    content = json.load(f)
                    if "messages" not in content:
                        continue

                    messages = content["messages"]
                    for message in messages:
                        yield Message(data=message, dir_name=os.path.basename(root))


def find_messages(root_dir: str, sender: Optional[str] = None):
    messages: Dict[str, List[dict]] = dict()

    for message in all_messages(root_dir):
        if sender is None or message.sender_name == sender:
            dir_name = message.dir_name

            if dir_name not in messages:
                messages[dir_name] = []

            messages[dir_name].append(message)

    return messages
