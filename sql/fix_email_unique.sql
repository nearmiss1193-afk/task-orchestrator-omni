-- Add unique constraint to email for upsert support
ALTER TABLE contacts_master
ADD CONSTRAINT unique_email UNIQUE (email);