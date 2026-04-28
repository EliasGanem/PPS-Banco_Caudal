#ifndef HAL_USB_H
#define HAL_USB_H

#include <stdint.h>
#include <stdbool.h>

uint16_t hal_usb_bytes_available(void);
uint8_t hal_usb_read_bytes(uint8_t *buffer, uint16_t length);
bool hal_usb_transmit(uint8_t *buffer, uint16_t length);

#endif /* HAL_USB_H */
