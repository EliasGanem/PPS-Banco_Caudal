#ifndef MCU_USB_CDC_H
#define MCU_USB_CDC_H

#include "hal_comm.h"

/**
 * @brief Obtiene la instancia de la interfaz HAL de comunicaciones USB CDC.
 * @return hal_comm_t* Puntero a la interfaz configurada para USB CDC.
 */
hal_comm_t *MCU_USB_CDC_GetInstance(void);

#endif // MCU_USB_CDC_H
