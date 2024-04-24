DROP TABLE IF EXISTS
    "judge",
    "judge_type",
    "circuit",
    "case",
    "hearing_date"
;


CREATE TABLE "judge"(
    "judge_id" SMALLINT NOT NULL GENERATED ALWAYS AS IDENTITY,
    "name" VARCHAR(50) NOT NULL,
    "appointed" DATE,
    "circuit_id" SMALLINT,
    "judge_type_id" BIGINT NOT NULL,
    "gender" CHAR(1)
);
ALTER TABLE
    "judge" ADD PRIMARY KEY("judge_id");
CREATE TABLE "judge_type"(
    "judge_type_id" SMALLINT NOT NULL GENERATED ALWAYS AS IDENTITY,
    "type_name" VARCHAR(100) NOT NULL
);
ALTER TABLE
    "judge_type" ADD PRIMARY KEY("judge_type_id");
CREATE TABLE "circuit"(
    "circuit_id" SMALLINT NOT NULL GENERATED ALWAYS AS IDENTITY,
    "name" VARCHAR(50) NOT NULL
);
ALTER TABLE
    "circuit" ADD PRIMARY KEY("circuit_id");
CREATE TABLE "case"(
    "case_no_id" CHAR(14) NOT NULL,
    "judge_id" SMALLINT NOT NULL,
    "verdict" TEXT NOT NULL,
    "summary" TEXT NOT NULL
);
ALTER TABLE
    "case" ADD PRIMARY KEY("case_no_id");
CREATE TABLE "hearing_date"(
    "hearing_id" BIGINT NOT NULL GENERATED ALWAYS AS IDENTITY,
    "date" DATE NOT NULL,
    "case_no_id" CHAR(14) NOT NULL
);
ALTER TABLE
    "hearing_date" ADD PRIMARY KEY("hearing_id");
ALTER TABLE
    "hearing_date" ADD CONSTRAINT "hearing_date_case_no_id_foreign" FOREIGN KEY("case_no_id") REFERENCES "case"("case_no_id");
ALTER TABLE
    "case" ADD CONSTRAINT "case_judge_id_foreign" FOREIGN KEY("judge_id") REFERENCES "judge"("judge_id");
ALTER TABLE
    "judge" ADD CONSTRAINT "judge_circuit_id_foreign" FOREIGN KEY("circuit_id") REFERENCES "circuit"("circuit_id");
ALTER TABLE
    "judge" ADD CONSTRAINT "judge_judge_type_id_foreign" FOREIGN KEY("judge_type_id") REFERENCES "judge_type"("judge_type_id");