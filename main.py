import json
from typing import Dict

from models import EXP_CHAT_ID
from stats import (
    get_member_stats,
    load_common_locations,
    make_member_stats_spreadsheet,
    str_simp,
)


def load_target_members():
    with open("output/target_members.json", "r") as f:
        return sorted(json.load(f))


if __name__ == "__main__":
    root_dir = "C:\\Users\\Levi\\Downloads\\json-fb"
    exp_chat_id = "experiencedishchat_5028908493890416"

    target_members = load_target_members()
    target_member_set = set(str_simp(member) for member in target_members)

    # If this location list doesn't already exist, comment this out and run find_common_locations to generate it
    ish_locations = load_common_locations()

    member_stats = get_member_stats(root_dir, loc_include=ish_locations)

    filtered_member_stats: Dict[str, dict] = dict()

    for member, stats in member_stats.items():
        # Only include members that are in the target_members list or have messages in the exp_chat_id location
        if EXP_CHAT_ID in stats.locations or str_simp(member) in target_member_set:
            filtered_member_stats[member] = stats.to_dict()

    with open("output/ish_member_stats.json", "w") as f:
        json.dump(filtered_member_stats, f, indent=2)

    make_member_stats_spreadsheet(
        member_stats,
        target_members,
        out_file="output/ish_member_stats.txt",
    )
