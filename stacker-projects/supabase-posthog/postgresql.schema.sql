ALTER ROLE authenticator PASSWORD 'c738814ec2aa527aa46663d5822e20bf';
ALTER ROLE supabase_auth_admin PASSWORD 'c738814ec2aa527aa46663d5822e20bf';
ALTER ROLE supabase_functions_admin PASSWORD 'c738814ec2aa527aa46663d5822e20bf';
ALTER ROLE supabase_storage_admin PASSWORD 'c738814ec2aa527aa46663d5822e20bf';
CREATE SCHEMA IF NOT EXISTS graphql_public;
DO $$ DECLARE r RECORD; BEGIN FOR r IN SELECT proname, pg_get_function_identity_arguments(oid) AS args FROM pg_proc WHERE pronamespace = 'auth'::regnamespace LOOP EXECUTE format('ALTER FUNCTION auth.%I(%s) OWNER TO supabase_auth_admin', r.proname, r.args); END LOOP; END $$;
ALTER SCHEMA auth OWNER TO supabase_auth_admin;
