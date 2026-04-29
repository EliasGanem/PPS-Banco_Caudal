#ifndef APP_RS232_TASK_H
#define APP_RS232_TASK_H

#include <stdint.h>
#include <stdbool.h>

/**
 * @brief Inicializa el hardware y recursos compartidos del bus RS232 (Mutex)
 */
void App_RS232_Init(void);

/**
 * @brief Lee la balanza. Aplica Mutex, cambia selectores, lee trama y formatea.
 * 
 * @param out_buffer Buffer de al menos 8 bytes donde se escribirá "PPPP.PP\0"
 * @return true si fue exitoso, false en caso de error o timeout
 */
bool App_RS232_ReadBalanza(char* out_buffer);

/**
 * @brief Lee el reloj. Aplica Mutex, cambia selectores, manda comando y lee respuesta.
 * 
 * @param out_buffer Buffer de al menos 2 bytes
 * @return true si fue exitoso, false en error o timeout
 */
bool App_RS232_ReadReloj(uint8_t* out_buffer);

#endif // APP_RS232_TASK_H
