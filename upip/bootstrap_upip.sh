# This script performs bootstrap installation of upip package manager from PyPI
# All the other packages can be installed using it.

if [ -z "$TMPDIR" ]; then
    cd /tmp
else
    cd $TMPDIR
fi

# Remove any stale old version
rm -rf pycopy-upip-*
wget -nd -rH -l1 -D files.pythonhosted.org https://pypi.org/project/pycopy-upip/ --reject=html

tar xfz pycopy-upip-*.tar.gz
mkdir -p ~/.micropython/lib/
cp pycopy-upip-*/upip*.py ~/.micropython/lib/

echo "upip is installed. To use:"
echo "pycopy -m upip --help"
