#include "utils/circular_buffer.h"

void cb_init(circular_buffer_t *cb, uint8_t *buffer, uint32_t max_size) {
    cb->buffer = buffer;
    cb->max_size = max_size;
    cb->head = 0;
    cb->tail = 0;
    cb->size = 0;
}

bool cb_push(circular_buffer_t *cb, uint8_t data) {
    if (cb->size == cb->max_size) {
        return false;
    }
    cb->buffer[cb->head] = data;
    cb->head = (cb->head + 1) % cb->max_size;
    cb->size++;
    return true;
}

bool cb_pop(circular_buffer_t *cb, uint8_t *data) {
    if (cb->size == 0) {
        return false;
    }
    *data = cb->buffer[cb->tail];
    cb->tail = (cb->tail + 1) % cb->max_size;
    cb->size--;
    return true;
}

void cb_clear(circular_buffer_t *cb) {
    cb->head = 0;
    cb->tail = 0;
    cb->size = 0;
}

uint32_t cb_get_size(circular_buffer_t *cb) {
    return cb->size;
}

bool cb_is_empty(circular_buffer_t *cb) {
    return (cb->size == 0);
}
