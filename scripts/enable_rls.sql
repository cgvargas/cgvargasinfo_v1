-- Script para habilitar Row Level Security (RLS) em todas as tabelas do esquema public
DO $$
DECLARE
    r RECORD;
BEGIN
    FOR r IN 
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
          AND table_type = 'BASE TABLE'
    LOOP
        EXECUTE 'ALTER TABLE public.' || quote_ident(r.table_name) || ' ENABLE ROW LEVEL SECURITY;';
    END LOOP;
END $$;
