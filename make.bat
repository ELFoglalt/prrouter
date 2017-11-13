if exist dist rm -r -f dist
if exist build rm -r -f build
START /WAIT pyinstaller prrouter.spec
rm -r -f dist/prrouter/
rm -r -f build
cp colors.yaml dist
cp overlays.yaml dist
cp readme.md dist
cp licence.txt dist
cp -r maps dist
cp -r overlays dist
cp -r fonts dist
fciv -add dist/prrouter.exe -both > dist/checksum
exit