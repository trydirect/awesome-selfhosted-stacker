ALTER ROLE authenticator PASSWORD '913496e4675d253ad5ba601a50387f405707649bb34d21692bbdf9762044035c';
ALTER ROLE supabase_auth_admin PASSWORD '913496e4675d253ad5ba601a50387f405707649bb34d21692bbdf9762044035c';
ALTER ROLE supabase_functions_admin PASSWORD '913496e4675d253ad5ba601a50387f405707649bb34d21692bbdf9762044035c';
ALTER ROLE supabase_storage_admin PASSWORD '913496e4675d253ad5ba601a50387f405707649bb34d21692bbdf9762044035c';
ALTER ROLE supabase_read_only_user PASSWORD '913496e4675d253ad5ba601a50387f405707649bb34d21692bbdf9762044035c';
CREATE SCHEMA IF NOT EXISTS graphql_public;
DO $$ DECLARE r RECORD; BEGIN FOR r IN SELECT proname, pg_get_function_identity_arguments(oid) AS args FROM pg_proc WHERE pronamespace = 'auth'::regnamespace LOOP EXECUTE format('ALTER FUNCTION auth.%I(%s) OWNER TO supabase_auth_admin', r.proname, r.args); END LOOP; END $$;
ALTER SCHEMA auth OWNER TO supabase_auth_admin;
