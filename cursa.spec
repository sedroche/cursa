# -*- mode: python -*-
import os

a = Analysis([os.path.join('src', 'dom', 'cursa.py')],
             pathex=['/home/john/pyinstaller-2.0'],
             hiddenimports = ['markdown.extensions.abbr',
			      'markdown.extensions.attr_list',
			      'markdown.extensions.codehilite',
			      'markdown.extensions.def_list',
			      'markdown.extensions.extra',
			      'markdown.extensions.fenced_code',
			      'markdown.extensions.footnotes',
			      'markdown.extensions.headerid',
			      'markdown.extensions.html_tidy',
			      'markdown.extensions.meta',
			      'markdown.extensions.nl2br',
			      'markdown.extensions.rss',
			      'markdown.extensions.sane_lists',
			      'markdown.extensions.smart_strong',
			      'markdown.extensions.tables',
			      'markdown.extensions.toc',
			      'markdown.extensions.wikilinks',
			      'encodings.ascii',
			      'encodings.utf_8'],
             hookspath=None)

datafiles = []
for root, dirnames, filenames in os.walk('DATA'):
    for filename in filenames:
        datafiles.append((filename, os.path.join(root, filename), 'DATA'))

a.datas += datafiles

pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name=os.path.join('dist', 'cursa'),
          debug=False,
          strip=None,
          upx=True,
          console=True )

