FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Create wait-for-it script
RUN echo '#!/bin/bash\n\
\n\
TIMEOUT=15\n\
QUIET=0\n\
\n\
echoerr() {\n\
    if [ "$QUIET" -ne 1 ]; then printf "%s\\n" "$*" 1>&2; fi\n\
}\n\
\n\
usage() {\n\
    exitcode="$1"\n\
    cat << USAGE >&2\n\
Usage:\n\
    $cmdname host:port [-t timeout] [-- command args]\n\
    -q | --quiet                        Do not output any status messages\n\
    -t TIMEOUT | --timeout=timeout      Timeout in seconds, zero for no timeout\n\
    -- COMMAND ARGS                     Execute command with args after the test finishes\n\
USAGE\n\
    exit "$exitcode"\n\
}\n\
\n\
wait_for() {\n\
    for i in `seq $TIMEOUT` ; do\n\
        nc -z "$HOST" "$PORT" > /dev/null 2>&1\n\
        \n\
        result=$?\n\
        if [ $result -eq 0 ] ; then\n\
            if [ $# -gt 0 ] ; then\n\
                exec "$@"\n\
            fi\n\
            exit 0\n\
        fi\n\
        sleep 1\n\
    done\n\
    echo "Operation timed out" >&2\n\
    exit 1\n\
}\n\
\n\
while [ $# -gt 0 ]\n\
do\n\
    case "$1" in\n\
        *:* )\n\
        HOST=$(printf "%s\\n" "$1"| cut -d : -f 1)\n\
        PORT=$(printf "%s\\n" "$1"| cut -d : -f 2)\n\
        shift 1\n\
        ;;\n\
        -q | --quiet)\n\
        QUIET=1\n\
        shift 1\n\
        ;;\n\
        -t)\n\
        TIMEOUT="$2"\n\
        if [ "$TIMEOUT" = "" ]; then break; fi\n\
        shift 2\n\
        ;;\n\
        --timeout=*)\n\
        TIMEOUT="${1#*=}"\n\
        shift 1\n\
        ;;\n\
        --)\n\
        shift\n\
        break\n\
        ;;\n\
        --help)\n\
        usage 0\n\
        ;;\n\
        *)\n\
        echoerr "Unknown argument: $1"\n\
        usage 1\n\
        ;;\n\
    esac\n\
done\n\
\n\
if [ "$HOST" = "" -o "$PORT" = "" ]; then\n\
    echoerr "Error: you need to provide a host and port to test."\n\
    usage 2\n\
fi\n\
\n\
wait_for "$@"' > /wait-for-it.sh && chmod +x /wait-for-it.sh

COPY . .

# Create entrypoint script
RUN echo '#!/bin/bash\n\
/wait-for-it.sh trip-db:5432 -t 60 -- python app.py' > /entrypoint.sh \
    && chmod +x /entrypoint.sh

CMD ["/entrypoint.sh"]
