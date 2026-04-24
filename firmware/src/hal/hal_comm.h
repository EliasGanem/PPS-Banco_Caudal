#ifndef HAL_COMM_H
#define HAL_COMM_H

#include <stdint.h>
#include "../utils/status.h"

/**
 * @brief Interfaz de abstracción de hardware (HAL) para comunicaciones.
 * Contiene callbacks para transmitir y recibir datos, aislando a la aplicación 
 * de la implementación subyacente (USB, UART, etc).
 */
typedef struct {
    /**
     * @brief Transmite un arreglo de bytes.
     * @param data Puntero a los datos a enviar.
     * @param length Cantidad de bytes a enviar.
     * @return status_t STATUS_OK en éxito, STATUS_BUSY si está ocupado.
     */
    status_t (*transmit)(const uint8_t* data, uint16_t length);

    /**
     * @brief Recibe datos del buffer.
     * @param data Puntero al buffer donde se guardarán los datos recibidos.
     * @param maxLength Tamaño máximo a leer.
     * @param receivedLength Puntero donde se almacenará la cantidad de bytes leídos realmente.
     * @return status_t STATUS_OK si hay datos leídos, STATUS_BUSY/ERROR en caso contrario.
     */
    status_t (*receive)(uint8_t* data, uint16_t maxLength, uint16_t* receivedLength);
} hal_comm_t;

#endif // HAL_COMM_H
