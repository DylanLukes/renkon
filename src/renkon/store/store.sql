-- name: create-tables#
-- Create all of the tables in the metadata database.
create table if not exists input_tables
(
    id   integer primary key,
    name text not null,
    path text not null,

    constraint input_files_name_key unique (name),
    constraint input_files_path_key unique (path)
);

create table if not exists output_tables
(
    id   integer primary key,
    name text not null,
    path text not null,

    constraint output_files_name_key unique (name),
    constraint output_files_path_key unique (path)
);

-- create table if not exists input_output
-- (
--     input_file_id  integer primary key,
--     output_file_id integer not null,
--
--     constraint input_file_output_files_input_file_id_fkey foreign key (input_file_id)
--         references input_files (id)
--         on update cascade
--         on delete cascade,
--     constraint input_file_output_files_output_file_id_fkey foreign key (output_file_id)
--         references output_files (id)
--         on update cascade
--         on delete cascade
-- );

-- name: put-input-table^
-- Insert a new input table into the database
insert into input_tables (name, path)
values (:name, :path)
on conflict (name) do update set path = :path
returning id;

-- name: get-input-table-path$
-- Get the path of an input table by name.
select path
from input_tables
where name = :name;

-- name: put-output-table^
-- Insert a new output table into the database
insert into output_tables (name, path)
values (:name, :path)
on conflict (name) do update set path = :path
returning id;


-- name: get-output-table-path$
-- Get the path of an input table by name.
select path
from output_tables
where name = :name;