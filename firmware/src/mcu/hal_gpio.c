#include "mcu/hal_gpio.h"
#include "main.h"

void hal_gpio_init(void) {
    GPIO_InitTypeDef GPIO_InitStruct = {0};

    __HAL_RCC_GPIOB_CLK_ENABLE();

    // PB5, PB6, PB7, PB8, PB9 as outputs
    GPIO_InitStruct.Pin = GPIO_PIN_5 | GPIO_PIN_6 | GPIO_PIN_7 | GPIO_PIN_8 | GPIO_PIN_9;
    GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
    GPIO_InitStruct.Pull = GPIO_NOPULL;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
    HAL_GPIO_Init(GPIOB, &GPIO_InitStruct);

    // Initial safe state (recirculation)
    // PB7=1, PB8=1, PB5=0 (enabled), PB6=0 (scale), PB9=0
    HAL_GPIO_WritePin(GPIOB, GPIO_PIN_5, GPIO_PIN_RESET);
    HAL_GPIO_WritePin(GPIOB, GPIO_PIN_6, GPIO_PIN_RESET);
    HAL_GPIO_WritePin(GPIOB, GPIO_PIN_7, GPIO_PIN_SET);
    HAL_GPIO_WritePin(GPIOB, GPIO_PIN_8, GPIO_PIN_SET);
    HAL_GPIO_WritePin(GPIOB, GPIO_PIN_9, GPIO_PIN_RESET);
}

void hal_gpio_write(hal_gpio_pin_t pin, bool state) {
    GPIO_PinState pin_state = state ? GPIO_PIN_SET : GPIO_PIN_RESET;
    switch(pin) {
        case HAL_PIN_PB5_MUX_EN:
            HAL_GPIO_WritePin(GPIOB, GPIO_PIN_5, pin_state);
            break;
        case HAL_PIN_PB6_MUX_SEL:
            HAL_GPIO_WritePin(GPIOB, GPIO_PIN_6, pin_state);
            break;
        case HAL_PIN_PB7_VALVE_REC:
            HAL_GPIO_WritePin(GPIOB, GPIO_PIN_7, pin_state);
            break;
        case HAL_PIN_PB8_TANK_SEL:
            HAL_GPIO_WritePin(GPIOB, GPIO_PIN_8, pin_state);
            break;
        case HAL_PIN_PB9_VALVE_WEIGH:
            HAL_GPIO_WritePin(GPIOB, GPIO_PIN_9, pin_state);
            break;
    }
}

bool hal_gpio_read(hal_gpio_pin_t pin) {
    GPIO_PinState state = GPIO_PIN_RESET;
    switch(pin) {
        case HAL_PIN_PB5_MUX_EN:
            state = HAL_GPIO_ReadPin(GPIOB, GPIO_PIN_5);
            break;
        case HAL_PIN_PB6_MUX_SEL:
            state = HAL_GPIO_ReadPin(GPIOB, GPIO_PIN_6);
            break;
        case HAL_PIN_PB7_VALVE_REC:
            state = HAL_GPIO_ReadPin(GPIOB, GPIO_PIN_7);
            break;
        case HAL_PIN_PB8_TANK_SEL:
            state = HAL_GPIO_ReadPin(GPIOB, GPIO_PIN_8);
            break;
        case HAL_PIN_PB9_VALVE_WEIGH:
            state = HAL_GPIO_ReadPin(GPIOB, GPIO_PIN_9);
            break;
    }
    return (state == GPIO_PIN_SET);
}
