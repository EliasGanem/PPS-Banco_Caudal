#ifndef HAL_GPIO_H
#define HAL_GPIO_H

#include <stdint.h>

/**
 * @brief Estados de retorno para las funciones de HAL GPIO
 */
typedef enum {
    HAL_GPIO_SUCCESS = 0,
    HAL_GPIO_ERROR
} hal_gpio_status_t;

/**
 * @brief Modos de configuración de un pin
 */
typedef enum {
    HAL_GPIO_MODE_INPUT = 0,
    HAL_GPIO_MODE_OUTPUT
} hal_gpio_mode_t;

/**
 * @brief Inicializa un pin del microcontrolador
 * 
 * @param pin Número del pin (GPIO)
 * @param mode Modo de entrada o salida
 * @return hal_gpio_status_t Estado de la operación
 */
hal_gpio_status_t HAL_GPIO_Init(uint8_t pin, hal_gpio_mode_t mode);

/**
 * @brief Escribe un estado digital en un pin de salida
 * 
 * @param pin Número del pin
 * @param value Estado a escribir (0 o 1)
 * @return hal_gpio_status_t Estado de la operación
 */
hal_gpio_status_t HAL_GPIO_Write(uint8_t pin, uint8_t value);

/**
 * @brief Lee el estado de un pin de entrada
 * 
 * @param pin Número del pin
 * @param value Puntero donde se almacenará el valor leído (0 o 1)
 * @return hal_gpio_status_t Estado de la operación
 */
hal_gpio_status_t HAL_GPIO_Read(uint8_t pin, uint8_t *value);

#endif // HAL_GPIO_H
