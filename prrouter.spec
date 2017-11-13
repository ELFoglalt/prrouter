# -*- mode: python -*-
import sys

block_cipher = None

#datafiles = [
#    ('colors.yaml', 'colors.base.yaml'),
#    ('overlays.yaml', 'overlays.base.yaml'),
#    ('overlays', 'overlays'),
#    ('maps', 'maps'),
#    ('fonts', 'fonts'),
#]
datafiles = []

a = Analysis(['prrouter.py'],
             pathex=['C:\\Dev\\projects\\pr-maps'],
             binaries=[],
             datas=datafiles,
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries + [('msvcp100.dll', 'C:\\Windows\\System32\\msvcp100.dll', 'BINARY'),
                        ('msvcr100.dll', 'C:\\Windows\\System32\\msvcr100.dll', 'BINARY')],
          a.zipfiles,
          a.datas,
          name='prrouter',
          debug=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=True)
