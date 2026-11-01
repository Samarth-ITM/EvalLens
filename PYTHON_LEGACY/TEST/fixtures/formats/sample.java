package com.evallens.monitoring;

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
