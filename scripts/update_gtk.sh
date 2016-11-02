#!/bin/bash

msys_dir=/cygdrive/c/msys64
supported_arch=(32 64)

required_dlls=(
    'libgtk-3-0.dll'
    'libgdk-3-0.dll'
    'libgdk_pixbuf-2.0-0.dll'
    'libpango-1.0-0.dll'
    'libpangocairo-1.0-0.dll'
    'libpangowin32-1.0-0.dll'
    'libatk-1.0-0.dll'
    'libcairo-gobject-2.dll'
    'libffi-6.dll'
    'libgio-2.0-0.dll'
    'libgirepository-1.0-1.dll'
    'libglib-2.0-0.dll'
    'libgmodule-2.0-0.dll'
    'libgobject-2.0-0.dll'
    'libgthread-2.0-0.dll'
    'libintl-8.dll'
    'libpng16-16.dll'
    'librsvg-2-2.dll'
    'libwinpthread-1.dll'
)

pushd $(dirname $0)/..

echo -e "\nCleaning...\n"

rm -rfv gi_repository/

mkdir -p gi_repository \
         lib32.new/girepository-1.0 \
         lib64.new/girepository-1.0

mv lib32/libsteam* lib32.new/
mv lib64/libsteam* lib64.new/
mv lib32/LIBSTEAM* lib32.new/
mv lib64/LIBSTEAM* lib64.new/

rm -rfv lib32 lib64
mv lib32.new lib32
mv lib64.new lib64

echo -e "\nUpdating...\n"

for arch in ${supported_arch[@]}; do
    mingw_dir=$msys_dir/mingw${arch}
    library_dir=lib${arch}

    cp -rfv $mingw_dir/lib/girepository-1.0/* $library_dir/girepository-1.0/

    for dll in ${required_dlls[@]}; do
        cp -rfv $mingw_dir/bin/$dll $library_dir/
    done
done

cp -rfv $msys_dir/mingw64/lib/python3.5/site-packages/gi/* gi_repository/

echo -e "\nCleanup unneded...\n"

rm -fv gi_repository/*.pyc
rm -fv gi_repository/*.a
rm -fv gi_repository/*cpython*

for arch in ${supported_arch[@]}; do
    library_dir=lib${arch}
    rm -fv $library_dir/girepository-1.0/HarfBuzz*
    rm -fv $library_dir/girepository-1.0/Json*
    rm -fv $library_dir/girepository-1.0/PangoFT2*
done

echo -e "\nDone.\n"

popd
