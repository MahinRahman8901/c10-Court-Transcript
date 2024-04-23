CREATE TABLE "judges"(
    "judge_id" SMALLINT NOT NULL,
    "name" VARCHAR(50) NOT NULL,
    "appointed" DATE,
    "circuit_id" SMALLINT,
    "judge_type_id" BIGINT NOT NULL,
    "gender" CHAR(1)
);
ALTER TABLE
    "judges" ADD PRIMARY KEY("judge_id");
CREATE TABLE "judge_types"(
    "judge_type_id" SMALLINT NOT NULL,
    "type_name" VARCHAR(100) NOT NULL
);
ALTER TABLE
    "judge_types" ADD PRIMARY KEY("judge_type_id");
CREATE TABLE "circuits"(
    "circuit_id" SMALLINT NOT NULL,
    "name" VARCHAR(50) NOT NULL
);
ALTER TABLE
    "circuits" ADD PRIMARY KEY("circuit_id");
CREATE TABLE "cases"(
    "case_no_id" VARCHAR(14) NOT NULL,
    "judge_id" SMALLINT NOT NULL,
    "verdict" TEXT NOT NULL,
    "summary" TEXT NOT NULL
);
ALTER TABLE
    "cases" ADD PRIMARY KEY("case_no_id");
CREATE TABLE "hearing_dates"(
    "hearing_id" INTEGER NOT NULL,
    "date" DATE NOT NULL,
    "case_no_id" VARCHAR(14) NOT NULL
);
ALTER TABLE
    "hearing_dates" ADD PRIMARY KEY("hearing_id");
ALTER TABLE
    "hearing_dates" ADD CONSTRAINT "hearing_dates_case_no_id_foreign" FOREIGN KEY("case_no_id") REFERENCES "cases"("case_no_id");
ALTER TABLE
    "cases" ADD CONSTRAINT "cases_judge_id_foreign" FOREIGN KEY("judge_id") REFERENCES "judges"("judge_id");
ALTER TABLE
    "judges" ADD CONSTRAINT "judges_circuit_id_foreign" FOREIGN KEY("circuit_id") REFERENCES "circuits"("circuit_id");
ALTER TABLE
    "judges" ADD CONSTRAINT "judges_judge_type_id_foreign" FOREIGN KEY("judge_type_id") REFERENCES "judge_types"("judge_type_id");