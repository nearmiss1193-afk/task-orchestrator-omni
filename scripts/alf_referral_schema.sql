-- ALF Referral Agency Database Schema
-- Run this in Supabase SQL Editor
-- ALF Facilities Database
CREATE TABLE IF NOT EXISTS alf_facilities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    address TEXT,
    city TEXT,
    county TEXT,
    zip TEXT,
    phone TEXT,
    email TEXT,
    website TEXT,
    -- Licensing
    license_number TEXT,
    license_type TEXT,
    -- Standard, LNS, ECC, LMH
    ahca_rating TEXT,
    last_inspection DATE,
    -- Capacity & Rates
    bed_count INT,
    current_availability INT,
    monthly_rate_min INT,
    monthly_rate_max INT,
    -- Commission
    commission_rate DECIMAL DEFAULT 1.0,
    -- 1.0 = 100% first month
    commission_structure TEXT,
    -- 'first_month', 'flat_fee', 'percentage'
    payment_terms TEXT,
    -- 'on_move_in', '30_days', '60_days'
    -- Services
    accepts_medicaid BOOLEAN DEFAULT FALSE,
    specialties TEXT [],
    -- memory_care, dementia, diabetes, etc.
    care_levels TEXT [],
    -- independent, assisted, skilled
    amenities TEXT [],
    -- Relationship
    contact_name TEXT,
    contact_title TEXT,
    contact_phone TEXT,
    contact_email TEXT,
    relationship_status TEXT DEFAULT 'prospect',
    -- prospect, contacted, partner, contracted
    contract_signed BOOLEAN DEFAULT FALSE,
    contract_date DATE,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
-- Client Referrals (Enhanced with full intake fields)
CREATE TABLE IF NOT EXISTS alf_referrals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    -- Family Contact (Section 1)
    family_contact_name TEXT NOT NULL,
    family_relationship TEXT,
    family_phone TEXT,
    family_email TEXT,
    best_contact_time TEXT,
    lead_source TEXT,
    -- girlfriend_referral, website, facebook, hospital, etc.
    -- Senior Info (Section 2)
    senior_name TEXT,
    senior_dob DATE,
    senior_age INT,
    senior_gender TEXT,
    current_situation TEXT,
    -- living_alone, with_spouse, hospital, rehab, other_alf
    current_city TEXT,
    -- Care Needs (Section 3)
    placement_reason TEXT,
    care_level TEXT,
    -- independent, assisted, memory_care, skilled_nursing
    adl_needs TEXT [],
    -- bathing, dressing, eating, toileting, walking, transferring, medications
    mobility_status TEXT,
    -- independent, walker, wheelchair, bedridden
    memory_status TEXT,
    -- none, mild, moderate, dementia, wanders
    medical_conditions TEXT [],
    special_care_needs TEXT [],
    -- Budget & Payment (Section 4) - CRITICAL
    budget_min INT,
    budget_max INT,
    budget_range TEXT,
    payment_source TEXT,
    -- private_pay, ltc_insurance, va, medicaid, selling_home
    has_ltc_insurance BOOLEAN DEFAULT FALSE,
    is_veteran BOOLEAN DEFAULT FALSE,
    medicaid_recipient BOOLEAN DEFAULT FALSE,
    -- ⚠️ NO COMMISSION IF TRUE
    -- Location (Section 5)
    preferred_city TEXT,
    preferred_county TEXT,
    max_distance_miles INT DEFAULT 25,
    placement_timeline TEXT,
    -- immediate, soon, planning, exploring
    -- Preferences (Section 6)
    room_preference TEXT,
    amenity_preferences TEXT [],
    additional_notes TEXT,
    -- Pipeline Status
    status TEXT DEFAULT 'intake',
    -- intake, matching, touring, placed, lost
    status_changed_at TIMESTAMPTZ,
    -- Matching
    matched_facilities UUID [],
    tours_scheduled INT DEFAULT 0,
    tours_completed INT DEFAULT 0,
    selected_facility_id UUID REFERENCES alf_facilities(id),
    -- Placement
    placed_date DATE,
    move_in_date DATE,
    monthly_rate INT,
    -- Commission
    commission_amount DECIMAL,
    commission_status TEXT,
    -- pending, invoiced, paid
    commission_paid_date DATE,
    invoice_number TEXT,
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
-- Facility Outreach Tracking
CREATE TABLE IF NOT EXISTS facility_outreach (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    facility_id UUID REFERENCES alf_facilities(id),
    outreach_type TEXT,
    -- email, call, visit, linkedin
    outreach_date TIMESTAMPTZ DEFAULT NOW(),
    contact_name TEXT,
    outcome TEXT,
    -- no_answer, callback, interested, not_interested, contracted
    notes TEXT,
    next_followup DATE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
-- Commission Tracking
CREATE TABLE IF NOT EXISTS alf_commissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    referral_id UUID REFERENCES alf_referrals(id),
    facility_id UUID REFERENCES alf_facilities(id),
    senior_name TEXT,
    move_in_date DATE,
    monthly_rate INT,
    commission_rate DECIMAL,
    commission_amount DECIMAL,
    invoice_date DATE,
    invoice_number TEXT,
    status TEXT DEFAULT 'pending',
    -- pending, invoiced, paid, disputed
    paid_date DATE,
    payment_method TEXT,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
-- Indexes
CREATE INDEX IF NOT EXISTS idx_facilities_city ON alf_facilities(city);
CREATE INDEX IF NOT EXISTS idx_facilities_status ON alf_facilities(relationship_status);
CREATE INDEX IF NOT EXISTS idx_referrals_status ON alf_referrals(status);
CREATE INDEX IF NOT EXISTS idx_referrals_medicaid ON alf_referrals(medicaid_recipient);
CREATE INDEX IF NOT EXISTS idx_commissions_status ON alf_commissions(status);
-- Updated_at trigger
CREATE OR REPLACE FUNCTION update_alf_updated_at() RETURNS TRIGGER AS $$ BEGIN NEW.updated_at = NOW();
RETURN NEW;
END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER update_facilities_updated_at BEFORE
UPDATE ON alf_facilities FOR EACH ROW EXECUTE FUNCTION update_alf_updated_at();
CREATE TRIGGER update_referrals_updated_at BEFORE
UPDATE ON alf_referrals FOR EACH ROW EXECUTE FUNCTION update_alf_updated_at();
-- Grant permissions
GRANT ALL ON alf_facilities TO authenticated;
GRANT ALL ON alf_referrals TO authenticated;
GRANT ALL ON facility_outreach TO authenticated;
GRANT ALL ON alf_commissions TO authenticated;