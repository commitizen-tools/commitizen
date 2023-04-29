#!/bin/sh
COMMIT_MSG_FILE=$1
exec < /dev/tty && cz commit --dry-run --write-message-to-file $COMMIT_MSG_FILE || true
