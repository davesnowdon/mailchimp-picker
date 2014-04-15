# -*- mode: python -*-
from kivy.tools.packaging.pyinstaller_hooks import install_hooks
install_hooks(globals())
a = Analysis(['src/main/python/picker.py'],
             pathex=['src/main/python', 'pyinstaller'],
             hiddenimports=[],
             runtime_hooks=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='mailchimp-picker',
          debug=False,
          strip=None,
          upx=True,
          console=False )
coll = COLLECT(exe,
               Tree('src/main/python'),
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=None,
               upx=True,
               name='mailchimp-picker')
app = BUNDLE(coll,
             name='mailchimp-picker.app',
             icon=None)
