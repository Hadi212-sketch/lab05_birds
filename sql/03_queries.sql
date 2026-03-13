-- Query 1: Species with wingspan > 50, sorted DESC, limit 2
SELECT *
FROM species
WHERE wingspan_cm > 50
ORDER BY wingspan_cm DESC
LIMIT 2;

-- Query 2: Birds with their species name (JOIN)
SELECT
  b.nickname,
  b.ring_code,
  s.name AS species_name
FROM birds b
JOIN species s ON b.species_id = s.id;

-- Query 3: Number of sightings per bird (COUNT + GROUP BY)
SELECT
  b.nickname,
  COUNT(*) AS sighting_count
FROM birdspotting bs
JOIN birds b ON bs.bird_id = b.id
GROUP BY b.id, b.nickname
ORDER BY sighting_count DESC;
