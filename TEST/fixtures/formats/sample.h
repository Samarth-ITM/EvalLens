#ifndef SAMPLE_H
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
