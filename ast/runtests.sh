set -e

for f in testdata/*.py; do
    echo $f
    ./test_one.sh $f
done
