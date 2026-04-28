#include "drivers/scale_driver.h"
#include "FreeRTOS.h"
#include "task.h"

struct scale_driver_t {
    scale_config_t config;
};

// Static allocation for one scale
static struct scale_driver_t scale_instance;

scale_handle_t scale_driver_init(scale_config_t *config) {
    if (!config || !config->read_byte || !config->clear_buffer) {
        return NULL;
    }
    scale_instance.config = *config;
    return &scale_instance;
}

// Frame format: "SPPPPPPC" where C is CR (\r). S is status. P is weight.
// Example weight_str: "PPPP.PP\0" (8 bytes total)
status_t scale_driver_read(scale_handle_t self, char *weight_str, uint32_t timeout_ms) {
    if (!self) return STATUS_ERROR;

    self->config.clear_buffer();

    uint32_t start_time = xTaskGetTickCount();
    uint8_t byte;
    uint8_t frame_index = 0;
    char rx_frame[8]; // S P P P P P P C

    while ((xTaskGetTickCount() - start_time) < pdMS_TO_TICKS(timeout_ms)) {
        if (self->config.read_byte(&byte)) {
            // Find start of frame (wait for CR to finish previous, or just wait for 'S')
            // Actually, wait, status byte can be anything? Assuming status is space or specific char.
            // A better way is to collect 8 bytes ending in '\r'.
            if (byte == '\r') {
                if (frame_index == 7) {
                    // Complete frame received: rx_frame[0] is S, rx_frame[1..6] is weight, byte is \r
                    for (int i = 0; i < 6; i++) {
                        weight_str[i] = rx_frame[i+1];
                    }
                    weight_str[6] = '\0'; // We will pad it to match PPPP.PP format. Wait, 6 digits?
                    // The soft spec says: "viene en un string donde los mas significativos son la parte entera luego viene un punto y despues la parte decimal. La longitud del string es de 7 caractes mas el terminador nulo."
                    // If the scale sends 6 digits e.g., "123.45", that's 6 characters. If it sends "1234.56", that's 7 characters.
                    // The prompt: "La balanza envia continuamente un string de 8 caracteres ... SPPPPPPC". So P is 6 chars. 
                    // Let's copy 6 chars from index 1.
                    for (int i = 0; i < 6; i++) {
                        weight_str[i] = rx_frame[i+1];
                    }
                    weight_str[6] = ' '; // Pad with space to make it 7 chars
                    weight_str[7] = '\0'; 
                    return STATUS_OK;
                }
                frame_index = 0; // Reset if CR is received out of order
            } else {
                if (frame_index < 7) {
                    rx_frame[frame_index++] = byte;
                } else {
                    // Frame too long without CR, reset
                    frame_index = 0;
                    rx_frame[frame_index++] = byte;
                }
            }
        } else {
            vTaskDelay(pdMS_TO_TICKS(2));
        }
    }

    return STATUS_TIMEOUT;
}
