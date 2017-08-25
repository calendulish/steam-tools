@echo off

pushd -d "$0\.."

if "%1" == "" goto nopython

echo "Compiling..."

call "C:\\%1\\python.exe" -u setup.py py2exe

cd dist

echo "Optimizing..."

if exist "C:\\7-zip\\7z.exe" set PATH="%PATH%;C:\\7-zip\\7z.exe"

7z -aoa x library.zip -olibrary
del library.zip

cd library
7z a -tzip -mx9 ..\library.zip -r
cd..
rd library /s /q

call "C:\UPX\upx.exe" --best *.*

exit 0

:nopython
echo Please, specify the python version.
goto error

:error
popd
exit 1
