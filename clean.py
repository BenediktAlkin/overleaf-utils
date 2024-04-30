from argparse import ArgumentParser
from pathlib import Path


def parse_args():
    parser = ArgumentParser()
    parser.add_argument("--src", type=str, default="src.tex", help="path to a latex file")
    parser.add_argument("--dst", type=str, default="dst.tex", help="path to output markdown file")
    return vars(parser.parse_args())


def main(src, dst):
    # read lines from overleaf file
    src = Path(src).expanduser()
    assert src.exists(), f"could not find file '{src.as_posix()}'"
    with open(src, encoding="utf8") as f:
        lines = f.readlines()

    # remove whitespaces
    lines = [line.strip() for line in lines]

    i = 0
    while i < len(lines):
        try:
            idx = lines[i].index("%")
        except ValueError:
            i += 1
            continue
        if idx == 0:
            del lines[i]
            continue
        if idx == len(lines[i]) - 1:
            i += 1
            continue
        if lines[i][idx - 1] != "\\":
            lines[i] = lines[i][:idx]
        i += 1


    dst = Path(dst).expanduser()
    with open(dst, "w", encoding="utf8") as f:
        f.writelines([f"{line}\n" for line in lines])



if __name__ == "__main__":
    main(**parse_args())