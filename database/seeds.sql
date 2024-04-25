INSERT INTO judge_type
    ("type_name")
VALUES
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
    ('John Doe', '2021-06-15', 1, 1, 'M'),
    ('Jane Smith', '2019-04-23', 2, 2, 'F'),
    ('Alice Johnson', '2020-11-01', 1, 3, 'F'),
    ('Chris Lee', '2022-01-12', 3, 1, 'M'),
    ('Pat Thomas', '2018-05-19', 2, 8, 'M');