
import pandas as pd
from pathlib import Path
import math

JSON_FILE = "csv_to_json/ign_subset.json"
OUT_DIR = "config/-qrels-maker-out/"
QRELS_FILES = [
    ("controls",    OUT_DIR + "qrels1.txt"),
    ("multiplayer", OUT_DIR + "qrels2.txt"),
    ("relaxing",    OUT_DIR + "qrels3.txt"),
    ("narrative",   OUT_DIR + "qrels4.txt"),
    ("technical",   OUT_DIR + "qrels5.txt"),
]
QRELS = len(QRELS_FILES)

CHARACTERS = 2400
LINE_LENGTH = 120
LINES = 10 + math.ceil(CHARACTERS / LINE_LENGTH)

UP = f"\x1B[{LINES}A"
UP_ONE = f"\x1B[1A"
CLR = "\x1B[0K"

STARTING_INDEX = 0 # Change to fit your needs

if __name__ == "__main__":
    base_dir = Path(__file__).parent.parent
    json_file = base_dir / JSON_FILE

    df = pd.read_json(json_file).transpose()
    DOCS = df.shape[1]
    STARTING_INDEX = min(STARTING_INDEX, DOCS)
    evals = [[] for _ in range(STARTING_INDEX)]
    print("\n\n\n\n")
    last_idx = STARTING_INDEX - 1
    stopped = False
    for idx in range(STARTING_INDEX, DOCS):
        last_idx = idx
        row = df[idx]
        title, subtitle, subheader, content, score, docId, *_ = row
        print(f"{UP}{idx / DOCS * 100:.1f}% [{idx}/{DOCS}] {CLR}\n"
              f"{title}{CLR}\n"
              f"{subtitle}{CLR}\n"
              f"{subheader}{CLR}\n"
              f"{docId}{CLR}\n"
              f"{score}{CLR}\n{CLR}\n{CLR}", end=f"\n{CLR}")
        for i in range(0, CHARACTERS, LINE_LENGTH):
            print(content[i : i + LINE_LENGTH])
        print(f"{CLR}\n")
        new_eval = [False for _ in range(QRELS)]
        i = 0
        while (i < QRELS):
            c = input(f"{UP_ONE}[{QRELS_FILES[i][0]}] Relevant? (y/n):{CLR}").strip()
            if c == "":
                i -= 1
                continue
            if c == "stop":
                stopped = True
                break
            new_eval[i] = "y" in c or "Y" in c or "p" in c
            i += 1
        if stopped: break
        evals.append(new_eval)
    
    for i in range(QRELS):
        with open(base_dir / QRELS_FILES[i][1], "a") as f:
            for idx in range(STARTING_INDEX, last_idx if stopped else DOCS):
                if not evals[idx][i]: continue
                row = df[idx]
                doc_id = row["id"].strip()
                f.write(f"0 0 {doc_id} 1\n")


