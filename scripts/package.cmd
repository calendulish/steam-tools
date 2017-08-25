@echo off

pushd -d "$0\.."

if "%1" == "" goto noversion

echo "Building package..."

if exist "C:\\7-zip\\7z.exe" set PATH="%PATH%;C:\\7-zip\\7z.exe"

rename dist "Steam Tools-%1"
7z a -tzip -mx9 "Steam Tools-%1.zip" "Steam Tools-%1" -r
mkdir dist
move "Steam Tools-%1.zip" dist

exit 0

:noversion
echo Please, specify a ST version
goto error

:error
popd
exit 1