DROP TABLE IF EXISTS transcript, judge, judge_type, circuit;

CREATE TABLE judge_type(
    "judge_type_id" SMALLINT UNIQUE PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    "type_name" VARCHAR(100) NOT NULL
);

CREATE TABLE circuit(
    "circuit_id" SMALLINT UNIQUE PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    "name" VARCHAR(50) NOT NULL
);

CREATE TABLE judge(
    "judge_id" INT UNIQUE PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    "name" TEXT NOT NULL,
    "appointed" DATE,
    "circuit_id" SMALLINT,
    "judge_type_id" BIGINT NOT NULL,
    "gender" CHAR(1),
    FOREIGN KEY ("circuit_id") REFERENCES circuit("circuit_id"),
    FOREIGN KEY ("judge_type_id") REFERENCES judge_type("judge_type_id")
);

CREATE TABLE transcript(
    "transcript_id" INT UNIQUE PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    "case_no" VARCHAR(17),
    "judge_id" INT NOT NULL,
    "verdict" TEXT NOT NULL,
    "summary" TEXT NOT NULL,
    "title" TEXT NOT NULL,
    "transcript_date" DATE NOT NULL,
    FOREIGN KEY ("judge_id") REFERENCES judge("judge_id")
);