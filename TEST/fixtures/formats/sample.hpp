#pragma once

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
