#include "sample.hpp"
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
