import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, computed_field


EXP_CHAT_ID = "experiencedishchat_5028908493890416"


class Message(BaseModel):
    data: dict
    dir_name: Optional[str] = None

    @computed_field
    def time_str(self) -> str:
        return datetime.datetime.fromtimestamp(
            self.data["timestamp_ms"] / 1000
        ).strftime("%Y-%m-%d %H:%M:%S")

    @computed_field
    def sender_name(self) -> str:
        return self.data["sender_name"]

    @computed_field
    def content(self) -> Optional[str]:
        return self.data.get("content", None)

    @computed_field
    def photos(self) -> Optional[List[str]]:
        photos = self.data.get("photos", None)
        if photos is None:
            return None

        return [photo["uri"] for photo in photos]

    @computed_field
    def reactions(self) -> Optional[List[str]]:
        return self.data.get("reactions", None)

    def to_dict(self) -> dict:
        return self.model_dump(exclude={"data"}, exclude_none=True)


class MemberStats(BaseModel):
    name: str
    num_messages: int = 0
    first_message: Optional[Message] = None
    last_message: Optional[Message] = None
    location: Optional[str] = None
    locations: Optional[Dict[str, "MemberStats"]] = None

    def new_message(self, message: Message):
        dir_name = message.dir_name
        if self.location is not None and message.dir_name != self.location:
            print(f"Warning: {self.location} != {dir_name} (Skipping message)")
            return

        self.num_messages += 1

        if self.first_message is None:
            self.first_message = message
        if self.last_message is None:
            self.last_message = message

        if message.data["timestamp_ms"] < self.first_message.data["timestamp_ms"]:
            self.first_message = message

        if message.data["timestamp_ms"] > self.last_message.data["timestamp_ms"]:
            self.last_message = message

        if self.location is not None:
            return

        # If this isn't bound to a location, then it should track all locations
        if self.locations is None:
            self.locations = dict()

        if dir_name not in self.locations:
            # This is a new location, so create a new MemberStats object for it, and bind it to the location
            self.locations[dir_name] = MemberStats(name=self.name, location=dir_name)

        self.locations[dir_name].new_message(message)

    def to_dict(self) -> dict:
        dump = self.model_dump(
            exclude={"first_message", "last_message", "locations"},
            exclude_none=True,
        )

        if self.first_message is not None:
            dump["first_message"] = self.first_message.to_dict()

        if self.last_message is not None:
            dump["last_message"] = self.last_message.to_dict()

        if self.locations is not None:
            dump["locations"] = {
                location: stats.to_dict() for location, stats in self.locations.items()
            }

        return dump
