#include "../../hal/hal_gpio.h"
#include "driver/gpio.h"
#include <stddef.h>

hal_gpio_status_t HAL_GPIO_Init(uint8_t pin, hal_gpio_mode_t mode) {
    gpio_config_t io_conf = {0};
    io_conf.intr_type = GPIO_INTR_DISABLE;
    io_conf.pin_bit_mask = (1ULL << pin);
    
    if (mode == HAL_GPIO_MODE_OUTPUT) {
        io_conf.mode = GPIO_MODE_OUTPUT;
        io_conf.pull_down_en = 0;
        io_conf.pull_up_en = 0;
    } else {
        io_conf.mode = GPIO_MODE_INPUT;
        io_conf.pull_down_en = 0;
        io_conf.pull_up_en = 1;
    }
    
    if (gpio_config(&io_conf) != ESP_OK) {
        return HAL_GPIO_ERROR;
    }
    return HAL_GPIO_SUCCESS;
}

hal_gpio_status_t HAL_GPIO_Write(uint8_t pin, uint8_t value) {
    if (gpio_set_level((gpio_num_t)pin, value) != ESP_OK) {
        return HAL_GPIO_ERROR;
    }
    return HAL_GPIO_SUCCESS;
}

hal_gpio_status_t HAL_GPIO_Read(uint8_t pin, uint8_t *value) {
    if (value == NULL) {
        return HAL_GPIO_ERROR;
    }
    *value = (uint8_t)gpio_get_level((gpio_num_t)pin);
    return HAL_GPIO_SUCCESS;
}
