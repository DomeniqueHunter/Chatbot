#!/bin/bash

# Ranch 2.2.0 -> 2.3.0

#rm ranch.db
cp ranch.db.backup ranch.db

FILE=ranch.db

# move table
sqlite3 ${FILE} "ALTER TABLE milking RENAME TO milking_old;"


# create ne table
sqlite3 ${FILE} "CREATE TABLE milking (id integer PRIMARY KEY, worker_id int NOT NULL, cow_id int NOT NULL, amount int NOT NULL, date text NOT NULL);"

# fill table
sqlite3 ${FILE} "INSERT INTO milking SELECT * FROM milking_old;"


# alter table
sqlite3 ${FILE} "ALTER TABLE milking ADD COLUMN work_points int NOT NULL DEFAULT 0;"
sqlite3 ${FILE} "ALTER TABLE worker ADD COLUMN work_points int NOT NULL DEFAULT 1;"
