-- Set role passwords from POSTGRES_PASSWORD environment variable
DO $$
DECLARE
  pw TEXT;
BEGIN
  pw := current_setting('POSTGRES_PASSWORD', true);
  IF pw IS NOT NULL AND pw != '' THEN
    EXECUTE format('ALTER USER authenticator WITH PASSWORD %L', pw);
    EXECUTE format('ALTER USER pgbouncer WITH PASSWORD %L', pw);
    EXECUTE format('ALTER USER supabase_auth_admin WITH PASSWORD %L', pw);
    EXECUTE format('ALTER USER supabase_functions_admin WITH PASSWORD %L', pw);
    EXECUTE format('ALTER USER supabase_storage_admin WITH PASSWORD %L', pw);
  END IF;
END $$;
