# Parsing medical sites

## launch main parsing

`python3 main.py`

### launch parsing certain urls

`python3 -m addons.parse_certain_urls`

### launch parsing pubmed sub (for testing purpose)

`python3 -m addons.test_parse_pubmed_sub`

When using "Seleniumbase" lib it will automatically download chrome driver (uc_driver in my case) to the installed lib on first launch of it.
You have to check the installed driver and installed chrome browser versions to be same.
