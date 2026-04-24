#include "mcu_usb_cdc.h"
#include "usbd_cdc_if.h"
#include "usbd_def.h"

static status_t USB_CDC_Transmit(const uint8_t* data, uint16_t length);
static status_t USB_CDC_Receive(uint8_t* data, uint16_t maxLength, uint16_t* receivedLength);

static hal_comm_t usb_cdc_inst = {
    .transmit = USB_CDC_Transmit,
    .receive = USB_CDC_Receive
};

hal_comm_t* MCU_USB_CDC_GetInstance(void) {
    return &usb_cdc_inst;
}

static status_t USB_CDC_Transmit(const uint8_t* data, uint16_t length) {
    if (CDC_Transmit_FS((uint8_t*)data, length) == USBD_BUSY) {
        return STATUS_BUSY;
    }
    // Asumimos OK si no está BUSY (normalmente retorna USBD_OK)
    return STATUS_OK;
}

static status_t USB_CDC_Receive(uint8_t* data, uint16_t maxLength, uint16_t* receivedLength) {
    uint16_t bytesAvailable = CDC_GetRxBufferBytesAvailable_FS();
    if (bytesAvailable > 0) {
        uint16_t bytesToRead = (bytesAvailable > maxLength) ? maxLength : bytesAvailable;
        if (CDC_ReadRxBuffer_FS(data, bytesToRead) == USB_CDC_RX_BUFFER_OK) {
            if (receivedLength != NULL) {
                *receivedLength = bytesToRead;
            }
            return STATUS_OK;
        }
        return STATUS_ERROR;
    }
    
    if (receivedLength != NULL) {
        *receivedLength = 0;
    }
    return STATUS_OK; // No hay datos, pero no es error
}
