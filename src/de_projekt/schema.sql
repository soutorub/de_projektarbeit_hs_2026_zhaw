-- Analytischer Unfallbestand, eine Zeile pro Unfall; Herkunft: Open Data Zürich / ASTRA.
-- STRICT verlangt SQLite >= 3.37; NULL bleibt bei unbekannten Angaben erlaubt.
CREATE TABLE accidents (
    AccidentUID TEXT PRIMARY KEY NOT NULL
        CHECK (length(AccidentUID) = 32 AND AccidentUID NOT GLOB '*[^0-9A-Fa-f]*'),
    AccidentYear INTEGER CHECK (AccidentYear BETWEEN 2011 AND 9999),
    AccidentMonth INTEGER CHECK (AccidentMonth BETWEEN 1 AND 12),
    AccidentWeekDay TEXT CHECK (AccidentWeekDay IN
        ('aw401','aw402','aw403','aw404','aw405','aw406','aw407')),
    AccidentHour INTEGER CHECK (AccidentHour BETWEEN 0 AND 23),
    AccidentType TEXT CHECK (AccidentType IN
        ('at0','at00','at1','at2','at3','at4','at5','at6','at7','at8','at9')),
    AccidentType_de TEXT,
    AccidentSeverityCategory TEXT CHECK (AccidentSeverityCategory IN ('as1','as2','as3','as4')),
    AccidentSeverityCategory_de TEXT,
    RoadType TEXT CHECK (RoadType IN
        ('rt430','rt431','rt432','rt433','rt434','rt435','rt436','rt437','rt438','rt439')),
    RoadType_de TEXT,
    AccidentWeekDay_de TEXT,
    AccidentInvolvingPedestrian INTEGER CHECK (AccidentInvolvingPedestrian IN (0,1)),
    AccidentInvolvingBicycle INTEGER CHECK (AccidentInvolvingBicycle IN (0,1)),
    AccidentInvolvingMotorcycle INTEGER CHECK (AccidentInvolvingMotorcycle IN (0,1)),
    AccidentLocation_CHLV95_E REAL,
    AccidentLocation_CHLV95_N REAL,
    CantonCode TEXT,
    MunicipalityCode TEXT,
    is_weekend INTEGER CHECK (is_weekend IN (0,1)),
    time_period TEXT CHECK (time_period IN ('night','morning','afternoon','evening')),
    vulnerable_road_user INTEGER CHECK (vulnerable_road_user IN (0,1)),
    -- IS statt =: Ein unzulässiges NULL darf nicht durch eine CHECK-Prüfung schlüpfen.
    CHECK (is_weekend IS CASE
        WHEN AccidentWeekDay IS NULL THEN NULL
        WHEN AccidentWeekDay IN ('aw406','aw407') THEN 1 ELSE 0 END),
    CHECK (time_period IS CASE
        WHEN AccidentHour IS NULL THEN NULL
        WHEN AccidentHour <= 5 THEN 'night' WHEN AccidentHour <= 11 THEN 'morning'
        WHEN AccidentHour <= 17 THEN 'afternoon' ELSE 'evening' END),
    CHECK (vulnerable_road_user IS CASE
        WHEN AccidentInvolvingPedestrian = 1 OR AccidentInvolvingBicycle = 1 THEN 1
        WHEN AccidentInvolvingPedestrian = 0 AND AccidentInvolvingBicycle = 0 THEN 0
        ELSE NULL END)
) STRICT;

-- Ein kleines Herkunftsregister, keine zusätzliche fachliche Dimension.
CREATE TABLE pipeline_metadata (
    key TEXT PRIMARY KEY NOT NULL,
    value TEXT NOT NULL
) STRICT;
