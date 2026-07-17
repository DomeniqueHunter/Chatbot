#!/bin/bash
set -e

DB_HOST="localhost"
DB_PORT="3306"
DB_USER="chatbot"
DB_PASSWORD="example"
DB_NAME="Ranch"

COLUMN_EXISTS=$(mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASSWORD" -N -B -e "
SELECT COUNT(*) FROM information_schema.columns
WHERE table_schema = '$DB_NAME' AND table_name = 'cow' AND column_name = 'yield';
")

if [ "$COLUMN_EXISTS" -eq 0 ]; then
    echo "column 'yield' does not exist, nothing to do"
    exit 0
fi

mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" -e "
ALTER TABLE \`cow\` DROP COLUMN \`yield\`;
"

echo "column 'yield' dropped from table 'cow'"