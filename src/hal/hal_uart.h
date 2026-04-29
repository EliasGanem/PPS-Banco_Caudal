#ifndef HAL_UART_H
#define HAL_UART_H

#include <stdint.h>
#include <stddef.h>

/**
 * @brief Estados de retorno para las funciones de HAL UART
 */
typedef enum {
    HAL_UART_SUCCESS = 0,
    HAL_UART_ERROR,
    HAL_UART_TIMEOUT
} hal_uart_status_t;

/**
 * @brief Identificadores lógicos de los puertos UART
 */
typedef enum {
    HAL_UART_PORT_USB = 0,    // Conectado a UART0
    HAL_UART_PORT_RS232 = 1   // Conectado a UART2
} hal_uart_port_t;

/**
 * @brief Inicializa el puerto UART y configura una cola de eventos si event_queue_out no es NULL.
 * 
 * @param port Identificador del puerto
 * @param baudrate Velocidad en baudios
 * @param event_queue_out Puntero doble donde se guardará el handle de la cola de eventos. Puede ser NULL si no se desean eventos.
 * @return hal_uart_status_t Estado de la operación
 */
hal_uart_status_t HAL_UART_Init(hal_uart_port_t port, uint32_t baudrate, void** event_queue_out);

/**
 * @brief Escribe un bloque de datos en el UART
 * 
 * @param port Identificador del puerto
 * @param data Puntero a los datos
 * @param length Cantidad de bytes a escribir
 * @return hal_uart_status_t Estado de la operación
 */
hal_uart_status_t HAL_UART_Write(hal_uart_port_t port, const uint8_t* data, size_t length);

/**
 * @brief Lee datos del UART de forma bloqueante (con timeout)
 * 
 * @param port Identificador del puerto
 * @param buffer Puntero al buffer de recepción
 * @param length Cantidad máxima de bytes a leer
 * @param read_bytes Puntero donde se guardará la cantidad de bytes leídos
 * @param timeout_ms Tiempo máximo de espera en milisegundos
 * @return hal_uart_status_t Estado de la operación
 */
hal_uart_status_t HAL_UART_Read(hal_uart_port_t port, uint8_t* buffer, size_t length, size_t* read_bytes, uint32_t timeout_ms);

/**
 * @brief Limpia el buffer de recepción del UART
 * 
 * @param port Identificador del puerto
 * @return hal_uart_status_t Estado de la operación
 */
hal_uart_status_t HAL_UART_Flush(hal_uart_port_t port);

#endif // HAL_UART_H
