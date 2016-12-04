CREATE TABLE assets (
  id       SERIAL PRIMARY KEY,
  filehash VARCHAR(32) UNIQUE
);
CREATE TABLE beatmaps (
  id     SERIAL PRIMARY KEY,
  bmhash VARCHAR(32) UNIQUE,
  beatmap_id INT,
  beatmap_set_id INT,
  approved BOOLEAN,
  total_length INT,
  hit_length INT,
  version TEXT,
  diff_size FLOAT,
  diff_overall FLOAT,
  diff_approach FLOAT,
  diff_drain FLOAT,
  mode INT,
  approved_date TIMESTAMP,
  last_update TIMESTAMP,
  artist TEXT,
  title TEXT,
  creator TEXT,
  bpm INT,
  source TEXT,
  tags TEXT,
  genre_id INT,
  language_id INT,
  max_combo INT,
  playcount BIGINT,
  passcount BIGINT,
  favourite_count BIGINT,
  difficultyrating FLOAT
);


CREATE TABLE beatmap_to_assets (
  id         SERIAL PRIMARY KEY,
  beatmap_id INT REFERENCES beatmaps (id),
  asset_id   INT REFERENCES assets (id),
  filename   TEXT,
  trusted    BOOLEAN DEFAULT FALSE,
  UNIQUE (beatmap_id, asset_id)
);


CREATE TABLE players (
  id          SERIAL PRIMARY KEY,
  player_name TEXT UNIQUE
);

CREATE TABLE replays (
  id         SERIAL PRIMARY KEY,
  replayhash VARCHAR(32) UNIQUE,
  replay64hash VARCHAR(32) UNIQUE,
  game_type INT,
  player_id  INT REFERENCES players (id),
  player_name TEXT,
  hit_300 INT,
  hit_100 INT,
  hit_50 INT,
  hit_gekis INT,
  hit_katus INT,
  total_score BIGINT,
  total_combo INT,
  total_misses INT,
  mods INT,
  time_played BIGINT,
  bmhash VARCHAR(32),
  beatmap_id INT REFERENCES beatmaps(id)
);


CREATE INDEX bmhash_on_replay_indx ON replays(bmhash);

