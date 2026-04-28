#ifndef CIRCULAR_BUFFER_H
#define CIRCULAR_BUFFER_H

#include <stdint.h>
#include <stdbool.h>

typedef struct {
    uint8_t *buffer;
    uint32_t head;
    uint32_t tail;
    uint32_t size;
    uint32_t max_size;
} circular_buffer_t;

void cb_init(circular_buffer_t *cb, uint8_t *buffer, uint32_t max_size);
bool cb_push(circular_buffer_t *cb, uint8_t data);
bool cb_pop(circular_buffer_t *cb, uint8_t *data);
void cb_clear(circular_buffer_t *cb);
uint32_t cb_get_size(circular_buffer_t *cb);
bool cb_is_empty(circular_buffer_t *cb);

#endif /* CIRCULAR_BUFFER_H */
