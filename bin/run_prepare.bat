set pwd=%cd%
echo "mounting directory %pwd%"

docker run --rm -itv %pwd%:/code -w /code python:latest bash bin/prepare_psv.sh