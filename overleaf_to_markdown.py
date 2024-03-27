from argparse import ArgumentParser
from pathlib import Path


def parse_args():
    parser = ArgumentParser()
    parser.add_argument("--src", type=str, required=True, help="path to a latex file")
    parser.add_argument("--dst", type=str, required=True, help="path to output markdown file")
    return vars(parser.parse_args())


def main(src, dst):
    # read lines from overleaf file
    src = Path(src).expanduser()
    assert src.exists(), f"could not find file '{src.as_posix()}'"
    with open(src, encoding="utf8") as f:
        lines = f.readlines()

    # remove whitespaces
    lines = [line.strip() for line in lines]

    # remove latex packages
    lines = [
        line
        for line in lines
        if (
                not line.startswith(r"\documentclass")
                and not line.startswith(r"\usepackage")
                and not line.startswith(r"\setlength")
                and not line.startswith(r"\newcommand")
                and not line.startswith(r"\begin{document}")
                and not line.startswith(r"\end{document}")
                and not line.startswith(r"\hline")
                and not line.startswith(r"\newpage")
        )
    ]

    # first pass (remove or add lines)
    i = 0
    while i < len(lines):
        line = lines[i]

        # remove comments
        if line.strip().startswith("%"):
            lines.pop(i)
            continue

        # replace \begin{enumerate} with markdown enumerate
        if line.startswith(r"\begin{enumerate}"):
            lines.pop(i)
            line = lines[i]
            while not line.startswith(r"\end{enumerate}"):
                item = r"\item "
                assert lines[i].startswith(item)
                lines[i] = "- " + lines[i][len(item):]
                i += 1
                line = lines[i]
            lines.pop(i)
            continue

        # reformat tables
        if line.startswith(r"\begin{table}"):
            # remove things like \begin{center} or \begin{tabular}
            while line.startswith(r"\begin{"):
                lines.pop(i)
                line = lines[i]
            # create markdown table from latex table
            row_idx = 0
            while not line.startswith(r"\end{"):
                assert r"\&" not in line, r"parsing tables with \& are not implemented"
                # remove trailing \\
                line = line.replace(r"\\", "")
                # replace & by | for column seperator
                line = line.replace("&", "|")
                num_cols = 1 + line.count("|")
                # add | before and after column
                line = "| " + line + " |"
                lines[i] = line
                i += 1
                line = lines[i]

                row_idx += 1
                # second row for markdown tables defines formatting of columns
                if row_idx == 1:
                    format_line = "|" + "".join(["---|" for _ in range(num_cols)])
                    lines.insert(i, format_line)
                    i += 1

            # remove things like \end{center} or \end{tabular} or \end{table}
            while line.startswith(r"\end{"):
                lines.pop(i)
                line = lines[i]
            continue

        # remove figures
        if line.startswith(r"\begin{figure}"):
            while not line.startswith(r"\end{figure}"):
                lines.pop(i)
                line = lines[i]
            lines.pop(i)
            continue

        i += 1

    # second pass (reformat lines individually)
    i = 0
    while i < len(lines):
        # remove whitespaces and comments
        line = lines[i].strip()

        # replace \section{text} with # text
        section = r"\section{"
        while section in line:
            section_start = line.index(section)
            text_start = section_start + len(section)
            text_end = text_start + line[text_start:].index("}")
            text = line[text_start:text_end]
            line = line[:section_start] + f"# {text}" + line[text_end + 1:]


        # replace \subsection{text} with **text**
        subsection = r"\subsection{"
        while subsection in line:
            subsection_start = line.index(subsection)
            text_start = subsection_start + len(subsection)
            text_end = text_start + line[text_start:].index("}")
            text = line[text_start:text_end]
            line = line[:subsection_start] + f"**{text}**" + line[text_end + 1:]


        # replace \textbf{text} with **text**
        textbf = r"\textbf{"
        while textbf in line:
            textbf_start = line.index(textbf)
            text_start = textbf_start + len(textbf)
            text_end = text_start + line[text_start:].index("}")
            text = line[text_start:text_end]
            line = line[:textbf_start] + f"**{text}**" + line[text_end + 1:]

        # replace \hyperlink{link}{text} with [text](link)
        hyperlink = r"\hyperlink{"
        while hyperlink in line:
            hyperlink_start = line.index(hyperlink)
            link_start = hyperlink_start + len(hyperlink)
            link_end = link_start + line[link_start:].index("}")
            link = line[link_start:link_end]
            text_start = link_end + 2
            assert line[text_start - 1] == "{"
            text_end = text_start + line[text_start:].index("}")
            text = line[text_start:text_end]
            line = line[:hyperlink_start] + f"[{text}]({link})" + line[text_end + 1:]

        # replace escaped characters
        # \& -> &
        line = line.replace(r"\&", "&")
        # $\sim$ -> ~
        line = line.replace(r"$\sim$", "~")
        # \# -> #
        line = line.replace(r"\#", "#")

        lines[i] = line
        i += 1




    dst = Path(dst).expanduser()
    with open(dst, "w") as f:
        f.writelines([f"{line}\n" for line in lines])



if __name__ == "__main__":
    main(**parse_args())