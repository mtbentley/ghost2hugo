#!/usr/bin/python3

import sqlite3
import json
from datetime import datetime


conn = sqlite3.connect('ghost.db')
conn.row_factory = sqlite3.Row

c = conn.cursor()
c2 = conn.cursor()


for i in c.execute('''
SELECT id, title, meta_description as description, slug, markdown as text,
status as draft, page, meta_title, image,
DATE(published_at/1000, "unixepoch") as date,
DATE(created_at/1000, "unixepoch") as date2
FROM posts
'''):
    g = {i.keys()[e]: tuple(i)[e] for e in range(len(i.keys()))}
    t = (i['id'],)
    g['tags'] = [e['name'] for e in c2.execute('''
    SELECT t.name FROM posts_tags pt JOIN tags t ON pt.tag_id = t.id
    WHERE pt.post_id=?''', t)]

    if g['date'] == None:
        g['date'] = g['date2']
    if g['draft'] == 'published':
        g['draft'] = False
    else:
        g['draft'] = True
    g.pop('date2')

    text = g.pop('text')
    text = text.replace("# ", "#")
    text = text.replace("#", "# ")
    text = text.replace("# # # ", "### ")
    text = text.replace("# # ", "## ")
    text = text.replace("\# ", "\#")

    if g['page'] == True:
        page = 'page'
    else:
        page = 'post'
    g['type'] = page
    g.pop('page')

    f = open("./content/%s.md" % (g['title']), "w")
    f.write(json.dumps(g, sort_keys=True, indent=4, separators=(',', ': ')))
    f.write('\n\n\n')
    f.write(text)
    f.close()
