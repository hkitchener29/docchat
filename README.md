# docchat

docchat is a command-line program that answers questions about the files in a folder. A language model can list, read, and search the files and do arithmetic to find its answers.

## Installation

```bash
python -m pip install -e . -r requirements.txt
```

Set `GROQ_API_KEY` in your environment or in a `.env` file.

## Usage

Run `chat` in any folder and ask a question. Use `/ls`, `/cat`, `/grep`, and `/calculate` to run a tool directly without contacting the model.

## Examples

### Markdown compiler

```
cd test_projects/markdown-compiler
chat
chat> /ls .
README.md
example
markdown_compiler
pyproject.toml
requirements.txt
chat> how are headings converted?
Arrr, ye be askin’ how the mighty **#** signs be turned into the HTML <h1>‑<h6> tags, aye?  Here’s the low‑down, straight from the code in `line_functions.py`:

1. **Check the prefix** – The function peeks at the first 1 to 6 characters of the line.
2. **Match the header level** – `######` → `<h6>` down to `#` → `<h1>`
3. **Wrap the rest of the line** – Whatever follows the hash marks is sandwiched between the opening and closing `<hX>` tags.
4. **No hash marks?** The line is returned unchanged.
```

The compiler turns a leading `#` through `######` into `<h1>` through `<h6>` by checking the first characters of each line, and it leaves lines without a heading marker unchanged.

### Homepage

```
cd test_projects/lab-homepage
chat
chat> /ls .
README.md
index.html
style.css
chat> what sections does the homepage have?
Arrr, matey! The grand ol' **homepage** (that be the `index.html` ye got) be as empty as a desert at sea.  It only holds a humble comment that says “Build your page here.”  So, to answer yer question: there be **no sections** on the homepage yet—just an empty canvas ready for ye to paint.  Time to set sail and start building!
```

At the commit this submodule points to, `index.html` contains only a placeholder comment ("Build your page here") and no real sections, so the homepage is still an empty starting template alongside `style.css`.

### eBay scraper

```
cd test_projects/ebay-scraper
chat
chat> /ls .
README.md
drill press.csv
drill press.json
ebay-dl.py
garden tools.csv
garden tools.json
practice-pages
practice-pages.zip
submission.toml
trowel.csv
trowel.json
chat> what does this scraper extract from each listing?
Arrr! Let’s set the record straight on what yer eBay‑scrapin’ code be plunderin’ from each listing:

name (the listing title), price (in cents), status (New, Used, etc.), shipping (in cents, 0 for free), free_returns (True/False/None), and items_sold (parsed from phrases like "12 sold").

All of these fields are gathered in `parse_card()` and returned as a list by `extract_items()`. If a field can't be found, it stays `None`.
```

The scraper pulls the name, price (in cents), status, shipping cost, free-returns flag, and number of items sold from each listing card, and it leaves a field as `None` when the listing doesn't show it.
