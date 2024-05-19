import json
from typing import Dict, List, Optional, Set

from models import EXP_CHAT_ID, MemberStats
from msg_utils import all_messages


def get_member_stats(
    root_dir: str,
    loc_include: Optional[Set[str]] = None,
    loc_exclude: Optional[Set[str]] = None,
) -> Dict[str, MemberStats]:
    member_stats: Dict[str, MemberStats] = dict()

    for message in all_messages(root_dir):
        if loc_include is not None and message.dir_name not in loc_include:
            continue
        if loc_exclude is not None and message.dir_name in loc_exclude:
            continue

        sender = message.sender_name
        if sender not in member_stats:
            member_stats[sender] = MemberStats(name=sender)

        member_stats[sender].new_message(message)

    return member_stats


def str_simp(s: str) -> str:
    return s.encode("ascii", "ignore").decode().casefold()


def load_common_locations():
    with open("output/ish_locations.json", "r") as f:
        return set(json.load(f))


def find_common_locations(
    members: List[str], member_stats: Dict[str, MemberStats]
) -> Set[str]:
    common_locations = set()

    for member in members:
        stats = member_stats[member]
        if stats.locations is None:
            continue

        if not common_locations:
            common_locations.update(stats.locations.keys())
            continue

        common_locations &= set(stats.locations.keys())

    return common_locations


def make_member_stats_spreadsheet(
    member_stats: Dict[str, MemberStats],
    target_members: List[str],
    out_file: str,
):
    member_stats = {str_simp(member): stats for member, stats in member_stats.items()}
    csv_data = [
        (
            "Member",
            "Num Messages",
            "First Message Time",
            "Last Message Time",
            "Last EXP Message Time",
        )
    ]
    for member in target_members:
        if str_simp(member) not in member_stats:
            csv_data.append((member, "", "", "", ""))
            print(f"{member} not found in member_stats")
            continue

        stats = member_stats[str_simp(member)]
        num_messages = stats.num_messages
        first_message_time = stats.first_message.time_str
        last_message_time = stats.last_message.time_str
        last_exp_message_time = ""
        if EXP_CHAT_ID in stats.locations:
            last_exp_message_time = stats.locations[EXP_CHAT_ID].last_message.time_str

        csv_data.append(
            (
                member,
                str(num_messages),
                first_message_time,
                last_message_time,
                last_exp_message_time,
            )
        )

    with open(out_file, "w") as f:
        for row in csv_data:
            # separate by spaces, keep all columns left-aligned
            f.write(" ".join(f"{col:<35}" for col in row) + "\n")
