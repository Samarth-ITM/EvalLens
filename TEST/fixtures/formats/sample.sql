-- Schema for Edge Telemetry Logs and Anomaly Records
CREATE TABLE IF NOT EXISTS edge_nodes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    node_uuid TEXT NOT NULL UNIQUE,
    cluster_name TEXT NOT NULL,
    architecture TEXT NOT NULL,
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS telemetry_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    node_id INTEGER NOT NULL REFERENCES edge_nodes(id) ON DELETE CASCADE,
    recorded_at TIMESTAMP NOT NULL,
    vibration_amplitude REAL NOT NULL,
    line_voltage REAL NOT NULL,
    temperature_celsius REAL NOT NULL,
    is_anomaly INTEGER NOT NULL DEFAULT 0,
    confidence_score REAL DEFAULT 0.0
);

CREATE INDEX IF NOT EXISTS idx_telemetry_node_time 
ON telemetry_snapshots(node_id, recorded_at DESC);

-- Query recent anomalous records
SELECT 
    en.cluster_name,
    en.node_uuid,
    ts.recorded_at,
    ts.vibration_amplitude,
    ts.confidence_score
FROM telemetry_snapshots ts
JOIN edge_nodes en ON ts.node_id = en.id
WHERE ts.is_anomaly = 1
ORDER BY ts.recorded_at DESC
LIMIT 100;
