# Setup:
# pip install pyyaml

# This converts all the chapter yaml files into proper *.min.json's

import json
import os
import shutil
import common
import pathlib
from typing import Dict, List

shutil.rmtree("build", ignore_errors=True)
pathlib.Path("build/examples").mkdir(parents=True)
pathlib.Path("build/index").mkdir(parents=True)
pathlib.Path("build/grades").mkdir(parents=True)

info = common.load_yaml("info.yaml")

# Move out the example stuff
if "examples" in info.keys():
    examples = info["examples"]
    del info["examples"]

with open("build/examples/info.json", "w") as examples_fp:
    json.dump(examples, examples_fp, indent=4)

with open("build/index/info.min.json", "w") as site_index_info:
    common.write_min_json(info, site_index_info)

# Create grades
grades: list = []
tags: list = []
grade_boards: Dict[int, List[str]] = {}

walker = os.walk("grades")

for dirpath, boards, _ in walker:
    # We want the subject jsons not the grades
    if dirpath == "grades":
        continue
    
    dir_split = dirpath.split("/")
    
    # Check if we are iterating over a grade. If dir_split is equal to 2: the folder is of the form grades/{GRADE}
    grade = dir_split[1]
    if grade.isdigit() and len(dir_split) == 2:
        grade = int(grade)

        grades.append(grade)
        grade_boards[grade] = []

        print(f"Analysing grade {grade} with boards {boards}")

        for board in boards:
            # Check if we are iterating over a supported board where info["boards"] is all supported boards as per info.yaml
            if board.upper() not in info["boards"]:
                print(f"WARNING: {board.upper()} not in {info['boards']}")
                continue

            board = board.lower()
            grade_boards[grade].append(board)
        
            print(f"Found board {board.upper()}")
                
            board = board.lower()
            _, subjects, _ = next(walker)
            for subject in subjects:
                print(f"Found subject {subject} in board {board.upper()}")

                subject_dir = os.path.join(dirpath, board, subject)

                for chapter in os.scandir(subject_dir):
                    if not chapter.is_dir():
                        continue
                    print(f"Adding chapter {chapter.name}")

                    chapter_dir = os.path.join(subject_dir, chapter.name)
                    chapter_info = common.load_yaml(os.path.join(chapter_dir, "info.yaml"))

                    # Check chapter info and fixup the format
                    if not chapter_info.get("primary-tag"):
                        if chapter_info.get("tags"):
                            chapter_info["primary-tag"] = chapter_info["tags"][0]
                        else:
                            chapter_info["tags"] = []
                            chapter_info["primary-tag"] = "untagged"

                    tags += chapter_info["tags"]

                    build_chapter_dir = subject_dir.replace("grades", "build/grades", 1)
                    pathlib.Path(build_chapter_dir).mkdir(parents=True)

                    with open(os.path.join(build_chapter_dir, "info.min.json"), "w") as chapter_info_json:
                        common.write_min_json(chapter_info, chapter_info_json)

    if common.debug_mode:
        print(dirpath, boards)

with open("build/grades/grade_info.min.json", "w") as grades_file:
    common.write_min_json({
            "grades": grades,
            "tags": tags,
            "grade_boards": grade_boards
        },
        grades_file
    )