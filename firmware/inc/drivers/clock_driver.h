#ifndef CLOCK_DRIVER_H
#define CLOCK_DRIVER_H

#include <stdint.h>
#include <stdbool.h>
#include "drivers/driver_types.h"

// Opaque pointer
typedef struct clock_driver_t* clock_handle_t;

typedef bool (*uart_read_byte_cb)(uint8_t *data);
typedef void (*uart_clear_cb)(void);

typedef struct {
    uart_read_byte_cb read_byte;
    uart_clear_cb clear_buffer;
} clock_config_t;

clock_handle_t clock_driver_init(clock_config_t *config);

// Read time from clock. Returns STATUS_OK on success.
// Expects "TTTT.TTT\0" (8 chars + \0 = 9 bytes max).
status_t clock_driver_read(clock_handle_t self, char *time_str, uint32_t timeout_ms);

#endif /* CLOCK_DRIVER_H */
