CREATE SCHEMA IF NOT EXISTS content;

CREATE TABLE IF NOT EXISTS content.film_work (
    id uuid PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    creation_date DATE,
    rating FLOAT CHECK (rating BETWEEN 0 AND 10),
    type TEXT NOT NULL CHECK (type IN ('movie', 'tv_show')),
    created timestamp with time zone DEFAULT now(),
    modified timestamp with time zone DEFAULT now()
);

-- Индексы на creation_date и rating, так как они более селективные
CREATE INDEX IF NOT EXISTS film_work_creation_date_idx ON content.film_work (creation_date);
CREATE INDEX IF NOT EXISTS film_work_rating_idx ON content.film_work (rating);

CREATE TABLE IF NOT EXISTS content.genre (
    id uuid PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    created timestamp with time zone DEFAULT now(),
    modified timestamp with time zone DEFAULT now(),
    CONSTRAINT genre_name_unique UNIQUE (name)
);

CREATE TABLE IF NOT EXISTS content.person (
    id uuid PRIMARY KEY,
    full_name TEXT NOT NULL,
    created timestamp with time zone DEFAULT now(),
    modified timestamp with time zone DEFAULT now()
);

CREATE INDEX IF NOT EXISTS person_full_name_idx ON content.person (full_name);

CREATE TABLE IF NOT EXISTS content.genre_film_work (
    id uuid PRIMARY KEY,
    genre_id uuid NOT NULL REFERENCES content.genre(id) ON DELETE CASCADE,
    film_work_id uuid NOT NULL REFERENCES content.film_work(id) ON DELETE CASCADE,
    created timestamp with time zone DEFAULT now(),
    CONSTRAINT genre_film_work_unique UNIQUE (genre_id, film_work_id)
);

CREATE INDEX IF NOT EXISTS genre_film_work_film_work_id_idx ON content.genre_film_work (film_work_id);

CREATE TABLE IF NOT EXISTS content.person_film_work (
    id uuid PRIMARY KEY,
    person_id uuid NOT NULL REFERENCES content.person(id) ON DELETE CASCADE,
    film_work_id uuid NOT NULL REFERENCES content.film_work(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('actor', 'director', 'writer', 'producer')),
    created timestamp with time zone DEFAULT now(),
    CONSTRAINT person_film_work_unique UNIQUE (person_id, film_work_id, role)
);

CREATE INDEX IF NOT EXISTS person_film_work_person_id_idx ON content.person_film_work (person_id);
CREATE INDEX IF NOT EXISTS person_film_work_film_work_id_idx ON content.person_film_work (film_work_id);