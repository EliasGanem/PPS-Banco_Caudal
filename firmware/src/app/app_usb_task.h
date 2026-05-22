#ifndef APP_USB_TASK_H
#define APP_USB_TASK_H

#include <stdint.h>
#include <stddef.h>

/**
 * @brief Inicializa el puerto USB y crea la tarea de recepción
 */
void App_USB_Init(void);

/**
 * @brief Envía una cadena de texto a través del USB a la PC
 * 
 * @param str Cadena terminada en nulo
 */
void App_USB_SendString(const char* str);

/**
 * @brief Envía un arreglo de bytes a través del USB a la PC
 * 
 * @param data Puntero a los bytes
 * @param len Cantidad de bytes
 */
void App_USB_SendBytes(const uint8_t* data, size_t len);

#endif // APP_USB_TASK_H
