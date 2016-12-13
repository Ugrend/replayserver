--This is to update the original replay server schema to this 1, you should'nt need to worry about this if running a new server

ALTER TABLE beatmaps ADD COLUMN   approved INT,
  ADD COLUMN total_length INT,
  ADD COLUMN hit_length INT,
  ADD COLUMN version TEXT,
  ADD COLUMN diff_size FLOAT,
  ADD COLUMN diff_overall FLOAT,
  ADD COLUMN diff_approach FLOAT,
  ADD COLUMN diff_drain FLOAT,
  ADD COLUMN mode INT,
  ADD COLUMN approved_date TIMESTAMP,
  ADD COLUMN last_update TIMESTAMP,
  ADD COLUMN artist TEXT,
  ADD COLUMN title TEXT,
  ADD COLUMN creator TEXT,
  ADD COLUMN bpm FLOAT,
  ADD COLUMN source TEXT,
  ADD COLUMN tags TEXT,
  ADD COLUMN genre_id INT,
  ADD COLUMN language_id INT,
  ADD COLUMN max_combo INT,
  ADD COLUMN playcount BIGINT,
  ADD COLUMN passcount BIGINT,
  ADD COLUMN favourite_count BIGINT,
  ADD COLUMN difficultyrating FLOAT;



ALTER TABLE replays ADD COLUMN beatmap_id INT REFERENCES beatmaps(id);

CREATE TABLE _dedup(beatmap_id INT, asset_id INT, filename TEXT);

INSERT INTO _dedup SELECT  beatmap_id, asset_id, filename
from beatmap_to_assets
group by beatmap_id, asset_id, filename
HAVING count(*) > 1);

DELETE FROM beatmap_to_assets WHERE id in (select beatmap_to_assets.id from beatmap_to_assets
  JOIN _dedup ON _dedup.beatmap_id = beatmap_to_assets.beatmap_id AND  _dedup.asset_id = beatmap_to_assets.asset_id AND  _dedup.filename = beatmap_to_assets.filename);

INSERT into beatmap_to_assets (beatmap_id, asset_id, filename) SELECT * FROM _dedup;

ALTER TABLE beatmap_to_assets ADD COLUMN trusted BOOLEAN DEFAULT FALSE, ADD CONSTRAINT beatmap_to_assets_beatmap_id_asset_id_filename_key UNIQUE(beatmap_id, asset_id, filename);
DROP TABLE _dedup;
