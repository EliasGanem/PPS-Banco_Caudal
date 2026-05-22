#include "app/app_control.h"
#include "app/app_usb_task.h"
#include "app/app_rs232_task.h"
#include "app/board_config.h"
#include "hal/hal_uart.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

void app_main(void) {
    // Inicializar hardware base (UARTs)
    HAL_UART_Init(HAL_UART_PORT_USB, USB_BAUDRATE, NULL);
    HAL_UART_Init(HAL_UART_PORT_RS232, RS232_BAUDRATE, NULL);

    // Inicializar módulos de aplicación
    App_Control_Init();
    App_RS232_Init();
    App_USB_Init();

    // Crear la tarea principal de control
    xTaskCreate(App_Control_Task, "CONTROL_TASK", 4096, NULL, 5, NULL);
}
