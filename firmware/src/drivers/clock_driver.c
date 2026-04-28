#include "drivers/clock_driver.h"
#include "FreeRTOS.h"
#include "task.h"

struct clock_driver_t {
    clock_config_t config;
};

// Static allocation for one clock
static struct clock_driver_t clock_instance;

clock_handle_t clock_driver_init(clock_config_t *config) {
    if (!config || !config->read_byte || !config->clear_buffer) {
        return NULL;
    }
    clock_instance.config = *config;
    return &clock_instance;
}

// We assume the clock sends data terminated by CR '\r' or similar.
// Format expected by PC: "TTTT.TTT" + '\0' (8 bytes + 1).
status_t clock_driver_read(clock_handle_t self, char *time_str, uint32_t timeout_ms) {
    if (!self) return STATUS_ERROR;

    self->config.clear_buffer();

    uint32_t start_time = xTaskGetTickCount();
    uint8_t byte;
    uint8_t frame_index = 0;

    while ((xTaskGetTickCount() - start_time) < pdMS_TO_TICKS(timeout_ms)) {
        if (self->config.read_byte(&byte)) {
            if (byte == '\r' || byte == '\n') {
                if (frame_index > 0) {
                    time_str[frame_index] = '\0';
                    return STATUS_OK;
                }
            } else {
                if (frame_index < 8) { // Up to 8 chars "TTTT.TTT"
                    time_str[frame_index++] = byte;
                }
            }
        } else {
            vTaskDelay(pdMS_TO_TICKS(2));
        }
    }

    return STATUS_TIMEOUT;
}
