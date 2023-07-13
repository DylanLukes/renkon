-- name: create-tables#
-- Create all of the tables in the metadata database.
create table if not exists tables
(
    path text primary key,            -- The _logical_ path to the table (relative to storage).
    name text not null,               -- The unique name of the table (generally same as or close to path).
    filetype text not null,           -- The format of the table in storage (parquet or arrow).

    schema blob not null,             -- The schema of the table.
    rows integer not null,            -- The number of rows in the table.
    size integer not null,            -- The serialized size of the table in storage (in bytes).

    constraint table_name_filetype_unique unique (name, filetype),
    constraint table_filetype_valid check ( filetype in ('parquet', 'arrow') )
);

-- name: register-table^
-- Register a new table in the database.
insert or replace into tables (path, name, filetype, schema, rows, size)
values (:path, :name, :filetype, :schema, :rows, :size);

-- name: unregister-table^
-- Unregister a table from the database.
delete from tables where name = :name;

-- name: get-table^
-- Get a table by its name and format.
select * from tables where name = :name and filetype = :filetype;

-- name: get-table-by-path^
-- Get a table by its path.
select * from tables where path = :path;

-- name: list-tables
-- List all of the tables in the database.
select * from tables;

-- name: search-tables-by-name^
-- List all of the tables in the database whose name matches the given pattern.
select * from tables where name like :pattern;

-- name: search-tables-by-path^
-- List all of the tables in the database whose path matches the given pattern.
select * from tables where path like :pattern;