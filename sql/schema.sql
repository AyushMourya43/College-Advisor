-- Enable pgvector extension
create extension if not exists vector;

-- Colleges table
create table colleges (
    id serial primary key,
    aishe_code text unique,
    name text,
    state text,
    district text,
    website text,
    year_of_establishment integer,
    location text,
    college_type text,
    management text,
    university_aishe_code text,
    university_name text,
    university_type text,
    profile_text text,
    embedding vector(384)
);

ALTER TABLE colleges ADD COLUMN reference_search_url TEXT;