import pandas as pd
import json
from pathlib import Path

def make_subset(filein, fileout, rows=200):
    df = pd.read_json(filein)
    df = df.sample(rows)
    res = list(df.to_dict(orient="index").values())
    with open(fileout, "w") as f:
        json.dump(res, f, indent=4, ensure_ascii=False)
    
if __name__ == "__main__":
    base_dir = Path(__file__).parent
    in_file = base_dir / "ign_processed.json"
    out_file = base_dir / "ign_subset.json"
    make_subset(in_file, out_file)
