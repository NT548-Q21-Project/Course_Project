-- ==================================================
-- AIMatch Database Initialization
-- Pattern: Schema per Service
-- Database: aimatch_db
--
-- Services:
--   1. identity_service
--   2. recruitment_service
--   3. ai_service
-- ==================================================

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ==================================================
-- CREATE SCHEMAS
-- ==================================================

CREATE SCHEMA IF NOT EXISTS identity_service;
CREATE SCHEMA IF NOT EXISTS recruitment_service;
CREATE SCHEMA IF NOT EXISTS ai_service;


-- ==================================================
-- IDENTITY SERVICE SCHEMA
-- Owns: authentication + users
-- ==================================================

CREATE TABLE IF NOT EXISTS identity_service.auth_credentials (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role VARCHAR(50) NOT NULL
        CHECK (role IN ('candidate', 'recruiter')),
    status VARCHAR(50) NOT NULL DEFAULT 'active'
        CHECK (status IN ('active', 'inactive', 'banned')),
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS identity_service.users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    auth_id UUID UNIQUE NOT NULL
        REFERENCES identity_service.auth_credentials(id)
        ON DELETE CASCADE,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL
        CHECK (role IN ('candidate', 'recruiter')),
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_auth_credentials_email
ON identity_service.auth_credentials(email);

CREATE INDEX IF NOT EXISTS idx_auth_credentials_role
ON identity_service.auth_credentials(role);

CREATE INDEX IF NOT EXISTS idx_users_auth_id
ON identity_service.users(auth_id);

CREATE INDEX IF NOT EXISTS idx_users_email
ON identity_service.users(email);

CREATE INDEX IF NOT EXISTS idx_users_role
ON identity_service.users(role);


-- ==================================================
-- RECRUITMENT SERVICE SCHEMA
-- Owns: CVs + jobs + applications
-- ==================================================

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE SCHEMA IF NOT EXISTS recruitment_service;

CREATE TABLE IF NOT EXISTS recruitment_service.cvs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    title VARCHAR(255) NOT NULL,
    file_url TEXT,
    content_type VARCHAR(100),
    file_size INTEGER,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS recruitment_service.jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    recruiter_id UUID NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    responsibilities TEXT,
    requirements TEXT,
    nice_to_have TEXT,
    benefits TEXT,
    location VARCHAR(255),
    job_type VARCHAR(50) NOT NULL DEFAULT 'full_time'
        CHECK (job_type IN ('full_time', 'part_time', 'internship')),
    status VARCHAR(50) NOT NULL DEFAULT 'active'
        CHECK (status IN ('active', 'closed')),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    expired_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS recruitment_service.applications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    candidate_id UUID NOT NULL,
    job_id UUID NOT NULL
        REFERENCES recruitment_service.jobs(id)
        ON DELETE CASCADE,
    cv_id UUID NOT NULL
        REFERENCES recruitment_service.cvs(id)
        ON DELETE CASCADE,
    status VARCHAR(50) NOT NULL DEFAULT 'submitted'
        CHECK (status IN ('submitted', 'rejected', 'accepted')),
    applied_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE(candidate_id, job_id)
);

CREATE INDEX IF NOT EXISTS idx_cvs_user_id
ON recruitment_service.cvs(user_id);

CREATE INDEX IF NOT EXISTS idx_cvs_created_at
ON recruitment_service.cvs(created_at);

CREATE INDEX IF NOT EXISTS idx_jobs_recruiter_id
ON recruitment_service.jobs(recruiter_id);

CREATE INDEX IF NOT EXISTS idx_jobs_status
ON recruitment_service.jobs(status);

CREATE INDEX IF NOT EXISTS idx_jobs_location
ON recruitment_service.jobs(location);

CREATE INDEX IF NOT EXISTS idx_jobs_job_type
ON recruitment_service.jobs(job_type);

CREATE INDEX IF NOT EXISTS idx_jobs_created_at
ON recruitment_service.jobs(created_at);

CREATE INDEX IF NOT EXISTS idx_applications_candidate_id
ON recruitment_service.applications(candidate_id);

CREATE INDEX IF NOT EXISTS idx_applications_job_id
ON recruitment_service.applications(job_id);

CREATE INDEX IF NOT EXISTS idx_applications_cv_id
ON recruitment_service.applications(cv_id);

CREATE INDEX IF NOT EXISTS idx_applications_status
ON recruitment_service.applications(status);

CREATE INDEX IF NOT EXISTS idx_applications_applied_at
ON recruitment_service.applications(applied_at);


-- ==================================================
-- AI SERVICE SCHEMA
-- Owns: CV-JD matching results
-- ==================================================

CREATE TABLE IF NOT EXISTS ai_service.match_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    candidate_id UUID NOT NULL,
    cv_id UUID NOT NULL,
    job_id UUID NOT NULL,
    fit_level VARCHAR(30) NOT NULL
        CHECK (fit_level IN ('strong_fit', 'fit', 'weak_fit', 'not_fit')),
    strengths JSONB,
    weaknesses JSONB,
    suggestions TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE(cv_id, job_id)
);

CREATE INDEX IF NOT EXISTS idx_match_results_candidate_id
ON ai_service.match_results(candidate_id);

CREATE INDEX IF NOT EXISTS idx_match_results_cv_id
ON ai_service.match_results(cv_id);

CREATE INDEX IF NOT EXISTS idx_match_results_job_id
ON ai_service.match_results(job_id);

CREATE INDEX IF NOT EXISTS idx_match_results_created_at
ON ai_service.match_results(created_at);
