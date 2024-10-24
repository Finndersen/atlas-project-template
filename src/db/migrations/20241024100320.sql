-- Create "users" table
CREATE TABLE "users" (
  "id" serial NOT NULL,
  "name" character varying NOT NULL,
  "email" character varying NOT NULL,
  PRIMARY KEY ("id")
);
-- Create "addresses" table
CREATE TABLE "addresses" (
  "id" serial NOT NULL,
  "street_number" integer NOT NULL,
  "street_name" character varying NOT NULL,
  "city" character varying NOT NULL,
  "state" character varying NOT NULL,
  "postal_code" character varying NOT NULL,
  "country" character varying NOT NULL,
  "user_id" integer NOT NULL,
  PRIMARY KEY ("id"),
  CONSTRAINT "addresses_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "users" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION
);
