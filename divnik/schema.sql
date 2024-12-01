CREATE TABLE IF NOT EXISTS "lesson" (
    "id" INTEGER PRIMARY KEY NOT NULL,
    "name" TEXT,
    "teacher" TEXT
);
CREATE TABLE IF NOT EXISTS "homework" (
    "id" INTEGER PRIMARY KEY NOT NULL,
    "desc" TEXT,
    "date" DATE,
    "lesson_id" INTEGER REFERENCES "lesson"("id") ON DELETE CASCADE
);