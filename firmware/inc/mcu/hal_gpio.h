#ifndef HAL_GPIO_H
#define HAL_GPIO_H

#include <stdint.h>
#include <stdbool.h>

typedef enum {
    HAL_PIN_PB5_MUX_EN,
    HAL_PIN_PB6_MUX_SEL,
    HAL_PIN_PB7_VALVE_REC,
    HAL_PIN_PB8_TANK_SEL,
    HAL_PIN_PB9_VALVE_WEIGH
} hal_gpio_pin_t;

void hal_gpio_init(void);
void hal_gpio_write(hal_gpio_pin_t pin, bool state);
bool hal_gpio_read(hal_gpio_pin_t pin);

#endif /* HAL_GPIO_H */
