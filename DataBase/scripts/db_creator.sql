-- Script para la creación de la base de datos y configuración inicial
-- PostgreSQL 13 o posterior.

-- 1. Crear la base de datos
CREATE DATABASE athena
    WITH 
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'es_MX.UTF-8'
    LC_CTYPE = 'es_MX.UTF-8'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1;