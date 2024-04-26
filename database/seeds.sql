INSERT INTO judge_type
    ("type_name")
VALUES
    ('N/A'),
    ('Supreme Court Judge'),
    ('High Court King’s Bench Division'),
    ('High Court Family Division'),
    ('High Court Chancery Division'),
    ('Circuit Judge'),
    ('District Judge'),
    ('District Judge (Magistrate'' Court)'),
    ('Diversity and Community Relations Judge'),
    ('Bench Chair'),
    ('Judge Advocates General'),
    ('Retired Senior Judiciary under 75')
;

INSERT INTO circuit
    ("name")
VALUES
    ('N/A'),
    ('London'),
    ('North East'),
    ('South East'),
    ('North West'),
    ('South West'),
    ('North'),
    ('West'),
    ('Midlands'),
    ('Wales'),
    ('Other Tribunal')
;

INSERT INTO judge ("name", "appointed", "circuit_id", "judge_type_id", "gender")
VALUES
    ('Unknown', '2000-02-20', 1, 1, 'X')
;