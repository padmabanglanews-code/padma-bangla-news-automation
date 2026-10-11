#!/usr/bin/env python3
"""index.html + style.css + demo-data.js + app.js -> একটি ফাইল blogger-paste.html (Blogger পেজের HTML ভিউতে পেস্ট করার জন্য)।
কোনো নেটওয়ার্ক ব্যবহার করে না।"""
import pathlib
d = pathlib.Path(__file__).parent
r = lambda n: (d / n).read_text(encoding='utf-8')
out = ('<style>\n' + r('style.css') + '\n</style>\n<div id="padma-dash"></div>\n'
       '<script>\n' + r('demo-data.js') + '\n</script>\n<script>\n' + r('app.js') + '\n</script>\n')
(d / 'blogger-paste.html').write_text(out, encoding='utf-8')
(d / 'preview-standalone.html').write_text(
    '<!DOCTYPE html><html lang="bn"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
    '<title>Padma Bangla News — AI Manager (DEMO)</title></head><body style="margin:0">\n' + out + '</body></html>\n', encoding='utf-8')
print('written', len(out), 'bytes')
