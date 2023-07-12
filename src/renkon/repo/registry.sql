-- name: create-tables#
-- Create all of the tables in the metadata database.
create table if not exists tables
(
    table_id   integer primary key,   -- The unique identifier.
    name text not null,               -- The unique name of the table (generally same as or close to path).
    path text not null,               -- The _logical_ path to the table (relative to storage).

    schema blob not null,             -- The schema of the table.
    rows integer not null,            -- The number of rows in the table.
    size integer not null,            -- The serialized size of the table in storage (in bytes).

    constraint input_files_name_key unique (name),
    constraint input_files_path_key unique (path)
);

-- name: register-table^
-- Register a new table in the database.
insert into tables (name, path, schema, rows, size)
values (:name, :path, :schema, :rows, :size)
on conflict (name) do update set path = :path
returning table_id;

-- name: unregister-table^
-- Unregister a table from the database.
delete from tables where name = :name;

-- name: get-table-by-id^
-- Get a table by its unique identifier.
select * from tables where table_id = :table_id;

-- name: get-table-by-name^
-- Get a table by its name.
select * from tables where name = :name;

-- name: get-table-by-path^
-- Get a table by its path.
select * from tables where path = :path;

-- name: list-tables^
-- List all of the tables in the database.
select * from tables;

-- name: list-tables-matching-name^
-- List all of the tables in the database whose name matches the given pattern.
select * from tables where name like :pattern;

-- name: list-tables-matching-path^
-- List all of the tables in the database whose path matches the given pattern.
select * from tables where path like :pattern;