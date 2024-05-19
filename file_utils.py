import os
import shutil
import hashlib
from typing import Dict, Tuple


def combine(root_dir: str, target_dir: str, dry_run: bool = False):
    # root_dir = "C:\\Users\\Levi\\Downloads\\json-fb"
    # target_dir = "C:\\Users\\Levi\\Downloads\\json-fb\\combined"
    target_dirname = os.path.basename(target_dir)

    verified_dirs = set([root_dir])
    dirs_to_combine = set()
    skipped_files = dict()

    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    # Traverse the root directory
    for root, dirs, files in os.walk(root_dir):
        if root.startswith(target_dir):
            continue

        if root == root_dir:
            dirs_to_combine.update(dirs)
            dirs_to_combine.remove(target_dirname)
            continue

        if os.path.basename(root) in dirs_to_combine:
            continue

        dir_to_combine = next(
            dir for dir in root.split(os.path.sep) if dir in dirs_to_combine
        )
        dst_dir = root.replace(dir_to_combine, target_dirname)

        if dst_dir not in verified_dirs:
            if not os.path.exists(dst_dir):
                os.makedirs(dst_dir)

            verified_dirs.add(dst_dir)

        for file in files:
            src = os.path.join(root, file)
            dst = os.path.join(dst_dir, file)

            if os.path.exists(dst):
                print(f"File {dst} already exists, checking hashes...")

                with open(src, "rb") as src_file:
                    src_hash = hashlib.md5(src_file.read()).hexdigest()

                with open(dst, "rb") as dst_file:
                    dst_hash = hashlib.md5(dst_file.read()).hexdigest()

                if src_hash == dst_hash:
                    print(f"Hashes match, deleting {src}")
                    if not dry_run:
                        os.remove(src)
                    continue

                print(f"Hashes don't match, skipping {src}")
                skipped_files[src] = dst
                continue

            print(f"Moving {src} to {dst}")
            if not dry_run:
                shutil.move(src, dst)

    print("Done!")

    if skipped_files:
        compare_skipped_files(skipped_files)


def compare_skipped_files(
    skipped_files: Dict[str, str],
    home_path_abs: str = "C:/Users/Levi/",
    home_path_rel: str = "../../../",
):
    with open("output/skipped_files.md", "w") as f:
        sorted_skipped_files = sorted(skipped_files.items())
        for src, dst in sorted_skipped_files:
            with open(src, "rb") as file:
                src_hash = hashlib.md5(file.read()).hexdigest()

            with open(dst, "rb") as file:
                dst_hash = hashlib.md5(file.read()).hexdigest()

            src = src.replace("\\", "/").replace(home_path_abs, home_path_rel)
            dst = dst.replace("\\", "/").replace(home_path_abs, home_path_rel)
            hash_equal = src_hash == dst_hash
            f.write(f"hash_equal: {hash_equal} ({src_hash} == {dst_hash})\n")
            f.write(f"![{os.path.basename(src)}]({src})\n")
            f.write(f"![{os.path.basename(dst)}]({dst})\n\n")


def find_json_files(root_dir: str):
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".json"):
                print(os.path.join(root, file))
