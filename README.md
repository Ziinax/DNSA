CREATE TABLE funds 
( 
    fund_id UUID PRIMARY KEY, 
    name TEXT NOT NULL, 
    currency VARCHAR(10), 
    fund_type TEXT CHECK (fund_type IN ('fund', 'benchmark')), 
    inception_date DATE 
);

CREATE TABLE underlyings 
( 
    underlying_id UUID PRIMARY KEY, 
    name TEXT NOT NULL, 
    identifier TEXT, 
    currency VARCHAR(10),
    asset_type TEXT, 
    region TEXT, 
    country TEXT, 
    sector TEXT, 
    esg_score DECIMAL(5,2), 
    country_risk_rating TEXT, 
    sustainable_classification TEXT 
);

CREATE TABLE risk_reports 
( 
    report_id UUID PRIMARY KEY, 
    fund_id UUID REFERENCES funds(fund_id), 
    benchmark_id UUID REFERENCES funds(fund_id), 
    report_date DATE NOT NULL, 
    portfolio_name TEXT,
    pricing_date DATE,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP 
);

CREATE TABLE report_compositions 
( 
    report_id UUID REFERENCES risk_reports(report_id), 
    underlying_id UUID REFERENCES underlyings(underlying_id), 
    parent_underlying_id UUID REFERENCES underlyings(underlying_id), 
    level INT, PRIMARY KEY (report_id, underlying_id) 

    PRIMARY KEY(report_id, underlying_id, level)    
);

CREATE TABLE indicators 
( 
    indicator_id UUID PRIMARY KEY, 
    name TEXT NOT NULL, 
    description TEXT, 
    unit TEXT 
);

CREATE TABLE report_indicator_values 
( 
    report_id UUID REFERENCES risk_reports(report_id), 
    underlying_id UUID REFERENCES underlyings(underlying_id), 
    indicator_id UUID REFERENCES indicators(indicator_id), 
    value TEXT, 
    
    PRIMARY KEY (report_id, underlying_id, indicator_id) 
);

CREATE TABLE archive
(
    archive_id UUID PRIMARY KEY,
    report_id UUID REFERENCES risk_reports (report_id)
    row_data TEXT,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)