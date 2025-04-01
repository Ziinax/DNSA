# DNSA

-- === 1. FUNDS (funds and benchmarks) ===
CREATE TABLE funds (
    fund_id UUID PRIMARY KEY,
    name TEXT NOT NULL,
    currency VARCHAR(10),
    fund_type TEXT CHECK (fund_type IN ('fund', 'benchmark')),
    inception_date DATE
);

-- === 2. UNDERLYINGS ===
CREATE TABLE underlyings (
    underlying_id UUID PRIMARY KEY,
    name TEXT NOT NULL,
    identifier TEXT UNIQUE,
    currency VARCHAR(10),
    asset_type TEXT,  -- e.g., Equity, Bond, Derivative
    region TEXT,
    country TEXT,
    sector TEXT,
    esg_score DECIMAL(5,2),
    country_risk_rating TEXT,
    sustainable_classification TEXT
);

-- === 3. RISK REPORTS ===
CREATE TABLE risk_reports (
    report_id UUID PRIMARY KEY,
    fund_id UUID REFERENCES funds(fund_id),
    benchmark_id UUID REFERENCES funds(fund_id),
    report_date DATE NOT NULL,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- === 4. REPORT COMPOSITION TREE ===
CREATE TABLE report_compositions (
    report_id UUID REFERENCES risk_reports(report_id),
    underlying_id UUID REFERENCES underlyings(underlying_id),
    parent_underlying_id UUID REFERENCES underlyings(underlying_id),
    weight DECIMAL(10,4), -- % of NAV
    market_value DECIMAL(20,4),
    position INT,
    level INT,
    PRIMARY KEY (report_id, underlying_id)
);

-- === 5. INDICATORS (Master list) ===
CREATE TABLE indicators (
    indicator_id UUID PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    unit TEXT
);

-- === 6. INDICATOR VIEWS (Subtypes e.g. TOTAL, PORTFOLIO) ===
CREATE TABLE indicator_views (
    view_id UUID PRIMARY KEY,
    name TEXT NOT NULL,         -- e.g. 'TOTAL', 'PORTFOLIO', 'BENCHMARK'
    description TEXT
);

-- === 7. REPORT INDICATOR VALUES (Actual data values) ===
CREATE TABLE report_indicator_values (
    report_id UUID REFERENCES risk_reports(report_id),
    underlying_id UUID REFERENCES underlyings(underlying_id),
    indicator_id UUID REFERENCES indicators(indicator_id),
    view_id UUID REFERENCES indicator_views(view_id),
    value DECIMAL(20,6),
    PRIMARY KEY (report_id, underlying_id, indicator_id, view_id)
);

-- === 8. OPTIONAL: FUND LIMITS (Risk management) ===
CREATE TABLE fund_limits (
    limit_id UUID PRIMARY KEY,
    fund_id UUID REFERENCES funds(fund_id),
    indicator_id UUID REFERENCES indicators(indicator_id),
    limit_min DECIMAL(20,6),
    limit_max DECIMAL(20,6),
    method TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
