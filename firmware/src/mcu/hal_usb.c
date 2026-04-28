#include "mcu/hal_usb.h"
#include "usbd_cdc_if.h"
#include "FreeRTOS.h"
#include "task.h"

uint16_t hal_usb_bytes_available(void) {
    return CDC_GetRxBufferBytesAvailable_FS();
}

uint8_t hal_usb_read_bytes(uint8_t *buffer, uint16_t length) {
    if (CDC_ReadRxBuffer_FS(buffer, length) == USB_CDC_RX_BUFFER_OK) {
        return length;
    }
    return 0;
}

bool hal_usb_transmit(uint8_t *buffer, uint16_t length) {
    // Retry transmission if busy
    uint8_t retry_count = 0;
    while (CDC_Transmit_FS(buffer, length) == USBD_BUSY) {
        vTaskDelay(pdMS_TO_TICKS(1));
        retry_count++;
        if (retry_count > 10) {
            return false;
        }
    }
    return true;
}
