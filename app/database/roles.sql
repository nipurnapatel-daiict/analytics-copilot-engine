-- Create a dedicated, read-only analyst account
CREATE USER analytics_analyst WITH PASSWORD 'readonly_secret_pass';
GRANT CONNECT ON DATABASE analytics_db TO analytics_analyst;
GRANT USAGE ON SCHEMA public TO analytics_analyst;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO analytics_analyst;

-- Ensure future tables are also read-only
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO analytics_analyst;
