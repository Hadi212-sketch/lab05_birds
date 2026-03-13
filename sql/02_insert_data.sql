INSERT INTO species (name, scientific_name, family, conservation_status, wingspan_cm)
VALUES
  ('House Sparrow', 'Passer domesticus', 'Passeridae', 'Least Concern', 21.00),
  ('European Robin', 'Erithacus rubecula', 'Muscicapidae', 'Least Concern', 22.50),
  ('Barn Owl', 'Tyto alba', 'Tytonidae', 'Least Concern', 95.00),
  ('White Stork', 'Ciconia ciconia', 'Ciconiidae', 'Least Concern', 195.00);

INSERT INTO birds (nickname, ring_code, age, species_id)
VALUES
  ('Pip', 'SPARROW-001', 2, 1),
  ('Rusty', 'ROBIN-001', 1, 2),
  ('Ghost', 'OWL-001', 4, 3),
  ('Cloud', 'STORK-001', 6, 4);

INSERT INTO birdspotting (bird_id, spotted_at, location, observer_name, notes)
VALUES
  (1, '2026-03-01 08:15:00', 'Brussels Park', 'Nina Peeters', 'Seen near the fountain'),
  (1, '2026-03-02 09:40:00', 'Ghent Riverside', 'Lars Mertens', 'Feeding on breadcrumbs'),
  (2, '2026-03-02 07:55:00', 'Antwerp Zoo Garden', 'Emma Janssens', 'Singing from a low branch'),
  (3, '2026-03-03 21:10:00', 'Ardennes Forest Edge', 'Tom Wouters', 'Hunting at dusk'),
  (4, '2026-03-04 12:25:00', 'Leuven Wetlands', 'Sofie Claes', 'Resting close to the marsh');
