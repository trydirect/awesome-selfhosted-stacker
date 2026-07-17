CREATE EXTENSION IF NOT EXISTS pg_net;

CREATE OR REPLACE FUNCTION public.forward_to_posthog()
RETURNS TRIGGER AS $$
BEGIN
  PERFORM net.http_post(
    url := 'http://posthog:8000/capture',
    body := json_build_object(
      'event', coalesce(NEW.event, 'demo_event'),
      'properties', json_build_object(
        'id', NEW.id,
        'created_at', NEW.created_at,
        'source', 'supabase_pipe_demo'
      )
    )::text,
    headers := '{"Content-Type": "application/json"}'::text
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS pipe_demo_forward ON public.pipe_demo;
CREATE TRIGGER pipe_demo_forward
AFTER INSERT ON public.pipe_demo
FOR EACH ROW EXECUTE FUNCTION public.forward_to_posthog();
