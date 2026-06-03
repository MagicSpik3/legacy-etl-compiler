from pathlib import Path
import argparse
import csv

# Prefer the Windows-mapped drive path first, then UNC / network host variants.
default_candidates = [
    r"Z:\MainstageR8\Monthly Processing\2202\5. Checks & Edits\3. Base Checks",
    r"\\nsdata1\MainstageR8\Monthly Processing\2202\5. Checks & Edits\3. Base Checks",
    r"/nsdata1/MainstageR8/Monthly Processing/2202/5. Checks & Edits/3. Base Checks",
]

parser = argparse.ArgumentParser(description="Count .sps files and line counts under a directory")
parser.add_argument("root", nargs="?", default=None, help="Root folder to search (default tries Z: or /nsdata1 mapping)")
parser.add_argument("output_file", nargs="?", default="sps_report.csv", help="CSV output file path")
parser.add_argument("-p", "--pattern", default="*.sps", help="Filename glob pattern to search")
args = parser.parse_args()


def normalize_path(path_str):
    path = Path(path_str).expanduser()
    if path.exists():
        return path

    if path_str.startswith("/nsdata1/"):
        z_path = Path(r"Z:" + path_str[len("/nsdata1"):])
        if z_path.exists():
            return z_path

        unc_path = Path(r"\\nsdata1" + path_str[len("/nsdata1"):].replace("/", "\\"))
        if unc_path.exists():
            return unc_path

    if path_str.startswith("Z:/"):
        return Path(path_str.replace("/", "\\")).expanduser()

    return path


def resolve_root(root_arg):
    if root_arg:
        root = normalize_path(root_arg)
        if root.exists():
            return root
        raise SystemExit(f"Path does not exist: {root_arg}")

    for candidate in default_candidates:
        root = normalize_path(candidate)
        if root.exists():
            return root

    tried = "\n".join(default_candidates)
    raise SystemExit(f"No default root path exists. Tried:{tried}")

root = resolve_root(args.root)
print(f"Using root: {root}")

results = []

if root.is_file():
    search_paths = [root]
else:
    search_paths = list(root.rglob(args.pattern))

for path in search_paths:
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
        
        results.append({
            "file": str(path),
            "lines": len(lines)
        })

    except Exception as e:
        print(f"Failed: {path} ({e})")

# Preserve discovery order and print files in the order found.
total_lines = sum(r["lines"] for r in results)

print(f"\nTotal files: {len(results)}")
print(f"Total lines: {total_lines}\n")

for r in results:
    print(f"{r['lines']:6}  {r['file']}")

with open(args.output_file, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=["file", "lines"])
    writer.writeheader()
    writer.writerows(results)

print(f"\nSaved report to: {args.output_file}")