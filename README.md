# Convert a single latex file to markdown

- Comments (lines starting with %) are removed
- Enumerations are converted to markdown
- Tables are converted to markdown format
- Figures are removed
- Sections will be replaced by markdown headings
- Subsection will be marked in bold
- `\textbf{text}` will be converted
- `\hyperlink` will be converted
- Characters that need to be escaped in latex will be unescaped for markdown (&, #)
- `$\sim$` is converted to ~

`python overleaf_to_markdown.py --src file.text --dst output.md`


# Clean comments from a single latex file

- removes everything starting from `%` in a line
- skips if `\%` is used 
- `%` at end of line are ignored (e.g. in `\end{subfigure}%`)