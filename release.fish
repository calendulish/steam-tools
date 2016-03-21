#!/usr/bin/fish

if not count $argv >/dev/null
    echo "Please, set the version"
    exit 1
end

function build
    if test $argv[2] = 'Windows'
        echo "Building for Windows"
        if test $argv[3] = '32'
            echo "Using 32 bits python"
            set py 'pythonwin32'; or exit 1
        else
            echo "Using 64 bits python"
            set py 'pythonwin64'; or exit 1
        end
        sleep 5
        eval $py setup.py py2exe; or exit 1
    else
        echo "Building for Linux"
        if test $argv[3] = '32'
            echo "Using 32bits python"
            set py 'python32'; or exit 1
        else
            echo "Using 64bits python"
            set py 'python64'; or exit 1
        end
        sleep 5
        eval $py setup.py build; or exit 1
        eval $py setup.py install --root=dist; or exit 1 
    end

    set rDir steam_tools_$argv[1]_$argv[2]_$argv[3]bits; or exit 1
    cd dist; or exit 1
    mkdir $rDir; or exit 1
    find * -maxdepth 0 -not -iname $rDir -exec mv \{\} $rDir \; ; or exit 1
    zip -r -9 $rDir.zip $rDir; or exit 1
    rm -f ../$rDir.zip; or exit 1
    mv $rDir.zip ..; or exit 1
    cd ..; or exit 1
    rm -rf dist/*; or exit 1
end

mkdir -p dist; or exit 1
rm -rf dist/* *.zip; or exit 1
build $argv[1] Windows 32
build $argv[1] Windows 64
#build $argv[1] Linux 32
#build $argv[1] Linux 64
#build $argv[1] $argv[2] $argv[3]