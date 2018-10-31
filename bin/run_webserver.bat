set pwd=%cd%
echo "mounting directory %pwd%"


docker run --rm -itv %pwd%:/code -w /code -p 8042:8042  python:latest bash bin/webserver.sh