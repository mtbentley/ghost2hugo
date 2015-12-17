#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sqlite3
import json
from datetime import datetime


# optional usage to remove accents on tag names
# -------------
import unicodedata
def remove_accents(input_str):
    nkfd_form = unicodedata.normalize('NFKD', unicode(input_str))
    return u"".join([c for c in nkfd_form if not unicodedata.combining(c)])
# -------------

conn = sqlite3.connect('ghost-dev.db')
conn.row_factory = sqlite3.Row

c = conn.cursor()
c2 = conn.cursor()

l = []

for i in c.execute('''
SELECT id, title, meta_description as description, slug, markdown as text,
status as draft, page, meta_title, image,
DATE(published_at/1000, "unixepoch") as date,
DATE(created_at/1000, "unixepoch") as date2
FROM posts'''):
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

    # post description
    if g['description'] == None:
        g['description'] = ""

    # post content    
    text = g.pop('text')
    text = text.replace("# ", "#")
    text = text.replace("#", "# ")
    text = text.replace("# # # ", "### ")
    text = text.replace("# # ", "## ")
    text = text.replace("\# ", "\#")

    # post type
    if g['page'] == True:
        page = 'page'
    else:
        page = 'post'
    g['type'] = page
    g.pop('page')    

    with open('./content/%s.md' % (g['slug']), 'w') as post_file:
        post_file.write('+++\n')
        post_file.write('type = "%s"\n' % g['type'])
        post_file.write('date = "%s"\n' % g['date'])
        post_file.write('title = "%s"\n' % g['title'].encode('utf8'))
        post_file.write('description = "%s"\n' % g['description'].encode('utf8'))
        post_file.write('slug = "%s"\n' % g['slug'])
        
        post_file.write('tags = [')

        # encode each tag to accept accents or removed them
        # and add a comma to separate each one
        for i in xrange(0, len(g['tags'])):
            if i < len(g['tags']) - 1 :
                separator = ", "
            else:
                separator = ""
            
            # encode string to keep accents etc. E.g. "Introdução e Avaliações"
            tag = g['tags'][i].encode('utf8')

            # uncomment if you like to remove accents. E.g. "Introducao e Avaliacoes"
            tag = remove_accents(g['tags'][i])

            post_file.write('"%s"' % tag+separator)

        post_file.write(']\n')

        post_file.write('+++\n\n')
        post_file.write(text.encode('utf8'))
