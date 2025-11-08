-- PostgreSQL Initialisierungs-Script
-- Erstellt Extensions und grundlegende Konfiguration

-- Enable UUID Extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable pgcrypto für zusätzliche Verschlüsselung
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Set timezone
SET timezone = 'Europe/Berlin';

-- Create database (wird von Docker bereits erstellt)
-- CREATE DATABASE patientenakte_db WITH ENCODING 'UTF8' LC_COLLATE='de_DE.UTF-8' LC_CTYPE='de_DE.UTF-8';
