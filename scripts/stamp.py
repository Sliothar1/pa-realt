"""Stamp name/subtitle/author from site/js/config.js into the static <title>/<meta> of site/index.html.
Run after renaming the project in site/js/config.js (the single config spot)."""
import re, pathlib
cfg = pathlib.Path('site/js/config.js').read_text(encoding='utf-8')
get = lambda k: re.search(rf'{k}:\s*"([^"]*)"', cfg).group(1)
name, sub, author = get('name'), get('subtitle'), get('author')
p = pathlib.Path('site/index.html'); s = p.read_text(encoding='utf-8')
s = re.sub(r'<!--CFG:title-->.*?<!--/CFG-->', f'<!--CFG:title--><title>{name} · {sub} · {author}</title><!--/CFG-->', s, flags=re.S)
s = re.sub(r'(<!--CFG:meta--><meta name="description" content=")[^·]*· [^:]*:', rf'\g<1>{name} · {sub}:', s, flags=re.S)
p.write_text(s, encoding='utf-8'); print('stamped', name, '·', sub)
