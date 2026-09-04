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
-- ---------------------------------------------------------------
-- Indexes (performance)
-- ---------------------------------------------------------------

-- Vector similarity search. Without this, every semantic search does a
-- sequential scan over all 52,509 rows.
create index if not exists colleges_embedding_hnsw_idx
    on colleges using hnsw (embedding vector_l2_ops);

-- State filter used by the dashboard and by semantic_search().
create index if not exists colleges_state_idx on colleges (state);

-- District dropdown lookup.
create index if not exists colleges_state_district_idx on colleges (state, district);

-- Name lookup (ILIKE %name%) -- trigram index.
create extension if not exists pg_trgm;
create index if not exists colleges_name_trgm_idx
    on colleges using gin (name gin_trgm_ops);
