-- Script: create_ahaems_cleaned_view.sql
-- Purpose: Create materialized view with cleaned AHA EMS data
-- Last updated: 2025-06-17
-- Drop existing versions first
DROP MATERIALIZED VIEW IF EXISTS public.ahaems_cleaned;
DROP TABLE IF EXISTS public.ahaems_cleaned;

-- Create the materialized view
CREATE MATERIALIZED VIEW public.ahaems_cleaned AS
SELECT
    -- Unique key
    COALESCE("Response EMS Response Number (eResponse.04)", '') || ' | ' ||
    COALESCE("Incident Unit Notified By Dispatch Date Time (eTimes.03)", '') AS "UniqueIncidentKey",

    -- Basic fields
    "Response EMS Response Number (eResponse.04)",
    "Incident Unit Notified By Dispatch Date Time (eTimes.03)",
    "Patient Age (ePatient.15)",
    "Patient Age Units (ePatient.16)",
    "Primary Impression",
    "Secondary Impression",
    "Transport Disposition",
    "Destination STEMI Team Activation Date Time (eDisposition.24)",
    "Destination STEMI Team Pre-arrival Activation (eDisposition.24)",
    "Destination Stroke Team Activation Date Time (eDisposition.24)",
    "Stroke Alert",
    "Situation Last Known Well Date Time (eSituation.18)",
    "Situation Symptom Onset Date Time (eSituation.01)",
    "Vitals Signs Taken Date Time (eVitals.01)",
    "Cardiac Arrest During EMS Event With Code (eArrest.01)",
    "Disposition Final Patient Acuity Code (eDisposition.19)",
    "Response Type Of Service Requested With Code (eResponse.05)",

    -- Glucose cleanup
    CASE
        WHEN TRIM("Patient Blood Glucose Level Count (eVitals.18)"::text) ILIKE 'low' THEN 40
        WHEN TRIM("Patient Blood Glucose Level Count (eVitals.18)"::text) ILIKE 'high' THEN 500
        WHEN TRIM("Patient Blood Glucose Level Count (eVitals.18)"::text) ~ '^[0-9]+(\.[0-9]+)?$'
            THEN TRIM("Patient Blood Glucose Level Count (eVitals.18)"::text)::numeric
        ELSE NULL
    END AS "Patient Blood Glucose Level Count (eVitals.18)",

    -- Cleaned fields
    RTRIM("Unit Arrived At Patient To First 12 Lead ECG Vitals Reading In "::text) AS "ECG Time",
    "Unit Arrived At Patient To First 12 Lead Procedure In Minutes",

    -- Truncated long field with proper escaping
    "Medication Given or Administered Description And RXCUI Code (eMedications.03)" AS med_admin,

    -- Aspirin flag
    CASE
        WHEN LOWER("Medication Given or Administered Description And RXCUI Code (eMedications.03)"::text) LIKE '%aspirin%'
            OR LOWER("Medication Given or Administered Description And RXCUI Code (eMedications.03)"::text) LIKE '%asa%'
            OR "Medication Given or Administered Description And RXCUI Code (eMedications.03)"::text LIKE '%687078%'
        THEN TRUE
        ELSE FALSE
    END AS "Aspirin Given",

    -- Other fields
    "Patient Cincinnati Stroke Scale Used (eVitals.30)",
    "Patient Initial Stroke Scale Score (eVitals.29)",
    "Vitals ECG Type (eVitals.04)",
    "Patient Initial Cardiac Rhythm ECG Finding List (eVitals.03)",
    "Patient Medication Allergy Description (eHistory.06)",
    "Response Type Of Scene Delay (eResponse.10)",
    "Disposition Type Of Destination (eDisposition.21)",
    "Airway Decision To Manage Patient With An Invasive Airway Date ",  -- Note the space at the end
    "Procedure Performed Description And Code (eProcedures.03)",
    "Patient Care Report Narrative (eNarrative.01)"
FROM public.ahaems_raw;