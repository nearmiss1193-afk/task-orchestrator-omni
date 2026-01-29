-- Add company_name column to contacts_master
ALTER TABLE contacts_master
ADD COLUMN IF NOT EXISTS company_name TEXT;