source .env
export PGPASSWORD=$DB_PASSWORD
psql --host c10-court-transcript-db.c57vkec7dkkx.eu-west-2.rds.amazonaws.com -p 5432 -U postgres court_transcript