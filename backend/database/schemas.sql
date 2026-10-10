CREATE TABLE "user_types" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "nm_type" TEXT NOT NULL
);


CREATE TABLE "courses" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "nm_course" TEXT NOT NULL
);


CREATE TABLE "classes" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "ds_class_code" TEXT UNIQUE NOT NULL
);


CREATE TABLE "materials" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "nm_material" TEXT NOT NULL,
    "nr_points_per_kilogram" INTEGER NOT NULL
);


CREATE TABLE "users" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "nm_user" TEXT NOT NULL, 
    "nr_ra" TEXT NOT NULL UNIQUE, 
    "fk_cd_course" INTEGER NOT NULL REFERENCES "courses"("id"),
    "fk_cd_class" INTEGER NOT NULL REFERENCES "classes"("id"), 
    "ds_email" TEXT UNIQUE NOT NULL,
    "ds_password" TEXT NOT NULL,
    "fk_cd_user_type" INTEGER NOT NULL DEFAULT 1 REFERENCES "user_types"("id"),
    "nr_points" REAL NOT NULL DEFAULT 0,
    "dh_created_at" TEXT DEFAULT (CURRENT_TIMESTAMP),
    "fk_cd_event" INTEGER REFERENCES "events"("id") ON DELETE SET NULL
);


CREATE TABLE "recycling" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT, 
    "fk_cd_material" INTEGER NOT NULL REFERENCES "materials"("id"),
    "nr_weight_kilograms" REAL NOT NULL,
    "fk_cd_user" INTEGER NOT NULL REFERENCES "users"("id") ON DELETE SET NULL,
    "dh_gave" TEXT NOT NULL DEFAULT (CURRENT_TIMESTAMP)
);


CREATE TABLE "events" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "nm_event" TEXT NOT NULL DEFAULT 'Evento sem nome',
    "ds_event_description" TEXT NOT NULL DEFAULT 'Evento sem descrição.',
    "dt_event_start" TEXT NOT NULL,
    "dt_event_end" TEXT NOT NULL
);


CREATE TABLE "event_groups" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "group_name" TEXT NOT NULL DEFAULT 'Grupo sem nome',
    "fk_cd_event" INTEGER NOT NULL REFERENCES "events"("id") ON DELETE CASCADE
);

