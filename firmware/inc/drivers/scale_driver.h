#ifndef SCALE_DRIVER_H
#define SCALE_DRIVER_H

#include <stdint.h>
#include <stdbool.h>
#include "drivers/driver_types.h"

// Opaque pointer
typedef struct scale_driver_t* scale_handle_t;

typedef bool (*uart_read_byte_cb)(uint8_t *data);
typedef void (*uart_clear_cb)(void);

typedef struct {
    uart_read_byte_cb read_byte;
    uart_clear_cb clear_buffer;
} scale_config_t;

// Initialize scale driver
scale_handle_t scale_driver_init(scale_config_t *config);

// Read weight from scale. Returns STATUS_OK on success.
// Expects "PPPP.PP" in weight_str (7 bytes + \0 = 8 bytes)
status_t scale_driver_read(scale_handle_t self, char *weight_str, uint32_t timeout_ms);

#endif /* SCALE_DRIVER_H */
