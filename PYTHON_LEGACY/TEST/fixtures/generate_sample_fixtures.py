"""
Generator script to build realistic fixtures for all 15 supported formats.
Produces realistic, syntax-valid, and semantically rich sample files in TEST/fixtures/.
"""

from __future__ import annotations

import io
from pathlib import Path
import docx
import pypdf

FIXTURES_DIR = Path(__file__).parent
FORMATS_DIR = FIXTURES_DIR / "formats"
FORMATS_DIR.mkdir(exist_ok=True, parents=True)

REPORT_MD_PATH = FIXTURES_DIR / "sample_report.md"


def generate_docx(text: str, output_path: Path) -> None:
    """Generate a rich DOCX from the markdown text with headings, paragraphs, and tables."""
    doc = docx.Document()
    doc.add_heading("Distributed Edge Anomaly Detection: Architecture & Performance Evaluation", 0)

    for line in text.splitlines():
        line_s = line.strip()
        if not line_s:
            continue
        if line_s.startswith("## "):
            doc.add_heading(line_s[3:], level=1)
        elif line_s.startswith("### "):
            doc.add_heading(line_s[4:], level=2)
        elif line_s.startswith("- "):
            doc.add_paragraph(line_s[2:], style="List Bullet")
        elif line_s.startswith("|") and "---" not in line_s:
            # Table row or header
            pass
        else:
            doc.add_paragraph(line_s)

    # Add a realistic table
    table = doc.add_table(rows=1, cols=4)
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = "Cluster"
    hdr_cells[1].text = "Nodes"
    hdr_cells[2].text = "Records"
    hdr_cells[3].text = "F1-Score"

    row_data = [
        ("Alpha (Compute Module 4)", "40", "5,840,000", "0.965"),
        ("Beta (BeagleBone Black)", "50", "4,920,000", "0.912"),
        ("Gamma (Siemens IOT2050)", "30", "3,440,000", "0.948"),
    ]
    for cluster, nodes, recs, f1 in row_data:
        row_cells = table.add_row().cells
        row_cells[0].text = cluster
        row_cells[1].text = nodes
        row_cells[2].text = recs
        row_cells[3].text = f1

    doc.save(str(output_path))


def generate_pdf(text: str, output_path: Path) -> None:
    """Generate a valid multi-page PDF using standard PDF syntax and text streams."""
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    
    # Split lines across 3 pages
    chunk_size = len(lines) // 3 + 1
    page_chunks = [lines[i:i + chunk_size] for i in range(0, len(lines), chunk_size)]

    # Escape PDF text characters
    def escape_pdf(s: str) -> str:
        return s.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")

    pdf_writer = pypdf.PdfWriter()

    for p_num, chunk in enumerate(page_chunks):
        stream_cmds = ["BT", "/F1 10 Tf", "50 750 Td"]
        for idx, line in enumerate(chunk[:40]):  # up to 40 lines per page
            # Truncate line for PDF display margin
            clean_l = escape_pdf(line[:85])
            if idx > 0:
                stream_cmds.append(f"0 -16 Td ({clean_l}) Tj")
            else:
                stream_cmds.append(f"({clean_l}) Tj")
        stream_cmds.append("ET")

        stream_body = "\n".join(stream_cmds)
        stream_len = len(stream_body.encode("latin-1"))

        raw_page_pdf = f"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /Resources << /Font << /F1 4 0 R >> >> /MediaBox [0 0 612 792] /Contents 5 0 R >>
endobj
4 0 obj
<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>
endobj
5 0 obj
<< /Length {stream_len} >>
stream
{stream_body}
endstream
endobj
xref
0 6
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000244 00000 n 
0000000318 00000 n 
trailer
<< /Size 6 /Root 1 0 R >>
startxref
450
%%EOF"""
        single_reader = pypdf.PdfReader(io.BytesIO(raw_page_pdf.encode("latin-1")))
        pdf_writer.add_page(single_reader.pages[0])

    with open(output_path, "wb") as f:
        pdf_writer.write(f)


def generate_all_fixtures() -> None:
    """Build all report formats and code fixtures."""
    raw_md = REPORT_MD_PATH.read_text(encoding="utf-8")

    # 1. Base sample reports
    (FIXTURES_DIR / "sample_report.txt").write_text(raw_md, encoding="utf-8")
    generate_docx(raw_md, FIXTURES_DIR / "sample_report.docx")
    generate_pdf(raw_md, FIXTURES_DIR / "sample_report.pdf")

    # Copies into formats/ for uniform format testing
    (FORMATS_DIR / "sample.md").write_text(raw_md, encoding="utf-8")
    (FORMATS_DIR / "sample.txt").write_text(raw_md, encoding="utf-8")
    generate_docx(raw_md, FORMATS_DIR / "sample.docx")
    generate_pdf(raw_md, FORMATS_DIR / "sample.pdf")

    # 2. PY - Python
    (FORMATS_DIR / "sample.py").write_text(
        '''"""
Edge Anomaly Detector Service.
Monitors node telemetry streams and flags statistical outliers.
"""

from dataclasses import dataclass
from typing import List, Optional
import math


@dataclass
class TelemetryRecord:
    timestamp: float
    voltage: float
    current: float
    vibration_amplitude: float


class AnomalyDetector:
    """Calculates rolling z-scores across multi-axis industrial sensor streams."""

    def __init__(self, threshold_sigma: float = 3.0) -> None:
        self.threshold_sigma = threshold_sigma
        self.history: List[float] = []

    def record_observation(self, record: TelemetryRecord) -> bool:
        magnitude = math.sqrt(record.voltage**2 + record.current**2 + record.vibration_amplitude**2)
        self.history.append(magnitude)
        if len(self.history) < 10:
            return False

        mean = sum(self.history) / len(self.history)
        variance = sum((x - mean) ** 2 for x in self.history) / len(self.history)
        std_dev = math.sqrt(variance) if variance > 0 else 1.0

        z_score = abs(magnitude - mean) / std_dev
        return z_score > self.threshold_sigma
''',
        encoding="utf-8",
    )

    # 3. CPP - C++
    (FORMATS_DIR / "sample.cpp").write_text(
        '''#include "sample.hpp"
#include <cmath>
#include <numeric>
#include <stdexcept>

namespace edge_eval {

AnomalyDetector::AnomalyDetector(double threshold) : threshold_sigma(threshold) {}

void AnomalyDetector::ingestMetric(const SensorPayload& payload) {
    double magnitude = std::sqrt(payload.vibrationX * payload.vibrationX + 
                                 payload.vibrationY * payload.vibrationY + 
                                 payload.vibrationZ * payload.vibrationZ);
    windowBuffer.push_back(magnitude);
    if (windowBuffer.size() > 1000) {
        windowBuffer.pop_front();
    }
}

bool AnomalyDetector::isAnomaly(double currentVal) const {
    if (windowBuffer.size() < 10) return false;
    double sum = std::accumulate(windowBuffer.begin(), windowBuffer.end(), 0.0);
    double mean = sum / windowBuffer.size();
    
    double sq_sum = std::inner_product(windowBuffer.begin(), windowBuffer.end(), 
                                       windowBuffer.begin(), 0.0);
    double stdev = std::sqrt(sq_sum / windowBuffer.size() - mean * mean);
    if (stdev == 0.0) return false;

    return std::abs(currentVal - mean) / stdev > threshold_sigma;
}

} // namespace edge_eval
''',
        encoding="utf-8",
    )

    # 4. H - C Header
    (FORMATS_DIR / "sample.h").write_text(
        '''#ifndef SAMPLE_H
#define SAMPLE_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    uint64_t timestamp_ms;
    float temperature_celsius;
    float vibration_g;
    uint32_t cluster_id;
} c_sensor_data_t;

int initialize_sensor_interface(uint32_t baud_rate);
bool read_sensor_data(c_sensor_data_t* out_data);
void shutdown_sensor_interface(void);

#ifdef __cplusplus
}
#endif

#endif // SAMPLE_H
''',
        encoding="utf-8",
    )

    # 5. HPP - C++ Header
    (FORMATS_DIR / "sample.hpp").write_text(
        '''#pragma once

#include <deque>
#include <cstdint>

namespace edge_eval {

struct SensorPayload {
    uint64_t timestamp;
    double vibrationX;
    double vibrationY;
    double vibrationZ;
};

class AnomalyDetector {
public:
    explicit AnomalyDetector(double threshold = 3.0);
    void ingestMetric(const SensorPayload& payload);
    bool isAnomaly(double currentVal) const;

private:
    double threshold_sigma;
    std::deque<double> windowBuffer;
};

} // namespace edge_eval
''',
        encoding="utf-8",
    )

    # 6. JAVA - Java
    (FORMATS_DIR / "sample.java").write_text(
        '''package com.evallens.monitoring;

import java.time.Instant;
import java.util.ArrayList;
import java.util.List;

/**
 * Edge node monitoring agent responsible for telemetry ingestion.
 */
public class EdgeMonitorAgent {
    private final String clusterId;
    private final List<Double> latencyRecords;

    public EdgeMonitorAgent(String clusterId) {
        this.clusterId = clusterId;
        this.latencyRecords = new ArrayList<>();
    }

    public synchronized void logObservation(double latencyMs) {
        if (latencyMs < 0) {
            throw new IllegalArgumentException("Latency cannot be negative: " + latencyMs);
        }
        latencyRecords.add(latencyMs);
    }

    public synchronized double getAverageLatency() {
        return latencyRecords.stream()
                .mapToDouble(Double::doubleValue)
                .average()
                .orElse(0.0);
    }
}
''',
        encoding="utf-8",
    )

    # 7. JS - JavaScript
    (FORMATS_DIR / "sample.js").write_text(
        '''/**
 * Anomaly Event Dispatcher.
 * Batches telemetry alerts and dispatches websocket messages.
 */

class AlertDispatcher {
    constructor(endpointUrl, batchSize = 50) {
        this.endpointUrl = endpointUrl;
        this.batchSize = batchSize;
        this.queue = [];
    }

    enqueueAlert(alert) {
        this.queue.push({ ...alert, recordedAt: new Date().toISOString() });
        if (this.queue.length >= this.batchSize) {
            return this.flush();
        }
        return Promise.resolve(false);
    }

    async flush() {
        if (this.queue.length === 0) return true;
        const payload = [...this.queue];
        this.queue = [];
        console.log(`Dispatched ${payload.length} alerts to ${this.endpointUrl}`);
        return true;
    }
}

module.exports = { AlertDispatcher };
''',
        encoding="utf-8",
    )

    # 8. TS - TypeScript
    (FORMATS_DIR / "sample.ts").write_text(
        '''/**
 * Type-safe Edge Cluster Definitions.
 */

export interface ClusterNode {
    id: string;
    hostname: string;
    ipAddress: string;
    cores: number;
    memoryMb: number;
    isActive: boolean;
    tags: string[];
}

export type HealthStatus = "HEALTHY" | "DEGRADED" | "CRITICAL" | "OFFLINE";

export function evaluateClusterHealth(nodes: ClusterNode[]): HealthStatus {
    const activeNodes = nodes.filter(n => n.isActive);
    const healthRatio = activeNodes.length / nodes.length;

    if (healthRatio >= 0.95) return "HEALTHY";
    if (healthRatio >= 0.70) return "DEGRADED";
    if (healthRatio > 0.0) return "CRITICAL";
    return "OFFLINE";
}
''',
        encoding="utf-8",
    )

    # 9. JSON - Structured JSON
    (FORMATS_DIR / "sample.json").write_text(
        '''{
  "system": "Distributed Edge Anomaly Detection",
  "version": "2.4.0",
  "clusters": [
    {
      "name": "Cluster Alpha",
      "architecture": "ARM Cortex-A72",
      "node_count": 40,
      "f1_score": 0.965,
      "p99_latency_ms": 38.2
    },
    {
      "name": "Cluster Beta",
      "architecture": "ARM Cortex-A8",
      "node_count": 50,
      "f1_score": 0.912,
      "p99_latency_ms": 64.5
    }
  ],
  "monitoring_enabled": true
}
''',
        encoding="utf-8",
    )

    # 10. HTML - HTML5
    (FORMATS_DIR / "sample.html").write_text(
        '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Cluster Telemetry Status Dashboard</title>
    <style>
        body { font-family: sans-serif; margin: 2rem; }
        .status-card { border: 1px solid #ccc; padding: 1rem; border-radius: 4px; }
        .healthy { color: #2e7d32; }
    </style>
</head>
<body>
    <header>
        <h1>Edge Cluster Operational Status</h1>
        <p>Real-time telemetry indicators across 120 edge nodes.</p>
    </header>
    <main>
        <div class="status-card">
            <h2>Cluster Alpha Status: <span class="healthy">Optimal</span></h2>
            <p>Throughput: 11.2 MB/hr | Mean Latency: 42ms | Active Nodes: 40/40</p>
        </div>
    </main>
</body>
</html>
''',
        encoding="utf-8",
    )

    # 11. CSS - CSS Stylesheet
    (FORMATS_DIR / "sample.css").write_text(
        ''':root {
    --primary-color: #1a73e8;
    --success-color: #0f9d58;
    --warning-color: #f4b400;
    --danger-color: #d93025;
    --card-background: #ffffff;
    --border-radius-base: 6px;
}

body {
    margin: 0;
    padding: 1.5rem;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background-color: #f8f9fa;
    color: #202124;
}

.dashboard-container {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 1.25rem;
    max-width: 1200px;
    margin: 0 auto;
}

.metric-card {
    background: var(--card-background);
    border-radius: var(--border-radius-base);
    padding: 1rem;
    box-shadow: 0 1px 3px rgba(60,64,67, 0.15);
}
''',
        encoding="utf-8",
    )

    # 12. SQL - SQL Schema and Queries
    (FORMATS_DIR / "sample.sql").write_text(
        '''-- Schema for Edge Telemetry Logs and Anomaly Records
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
''',
        encoding="utf-8",
    )


if __name__ == "__main__":
    generate_all_fixtures()
    print("Successfully generated all sample fixtures in TEST/fixtures/ and TEST/fixtures/formats/")

