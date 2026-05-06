#ifndef BOARD_CONFIG_H
#define BOARD_CONFIG_H

#include <stdint.h>

/**
 * @brief Configuración de Baudrates
 */
#define USB_BAUDRATE 115200
#define RS232_BAUDRATE 1200

/**
 * @brief Terminador de comandos USB
 */
#define CMD_TERMINATOR '\r'

/**
 * @brief Asignación de pines del hardware
 */
#define PIN_HAB_MUX 27
#define PIN_SELECTOR_UART 26
#define PIN_VALV_RECIRC 25
#define PIN_SEL_TANQUE 33
#define PIN_VALV_PESADA 32

/**
 * @brief Configuración de la lógica activa para cada terminal
 * Definir como 1 si es lógica positiva (activo en alto)
 * Definir como 0 si es lógica negativa (activo en bajo)
 */
#define LOGIC_HAB_MUX_ACTIVE 0
#define LOGIC_VALV_RECIRC_ACTIVE 1
#define LOGIC_VALV_PESADA_ACTIVE 1

/**
 * @brief Valores para el selector de tanque
 */
#define VAL_SEL_TANQUE_RECIRCULACION 0
#define VAL_SEL_TANQUE_PESADA 1

/**
 * @brief Valores para el selector de UART (MUX RS232)
 */
#define VAL_SEL_UART_BALANZA 0
#define VAL_SEL_UART_RELOJ 1

#endif // BOARD_CONFIG_H
