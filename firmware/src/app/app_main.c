#include "app/app_main.h"
#include "app/app_protocol.h"
#include "mcu/hal_gpio.h"
#include "mcu/hal_usb.h"
#include "mcu/hal_uart.h"
#include "drivers/scale_driver.h"
#include "drivers/clock_driver.h"
#include "FreeRTOS.h"
#include "task.h"
#include "queue.h"
#include "semphr.h"
#include <string.h>
#include <stdio.h>

// Static OS Allocation
#define TAREA_USB_STACK_SIZE 256
static StackType_t tarea_usb_stack[TAREA_USB_STACK_SIZE];
static StaticTask_t tarea_usb_tcb;

#define TAREA_CONTROL_STACK_SIZE 256
static StackType_t tarea_control_stack[TAREA_CONTROL_STACK_SIZE];
static StaticTask_t tarea_control_tcb;

#define TAREA_MUX_STACK_SIZE 256
static StackType_t tarea_mux_stack[TAREA_MUX_STACK_SIZE];
static StaticTask_t tarea_mux_tcb;

#define CMD_QUEUE_LEN 5
static uint8_t cmd_queue_storage[CMD_QUEUE_LEN * sizeof(app_cmd_t)];
static StaticQueue_t cmd_queue_struct;
static QueueHandle_t cmd_queue;

typedef enum {
    REQ_SCALE,
    REQ_CLOCK
} mux_req_type_t;

typedef struct {
    mux_req_type_t type;
    char response[16];
    status_t status;
    TaskHandle_t notify_task;
} mux_req_t;

static uint8_t mux_queue_storage[2 * sizeof(mux_req_t)];
static StaticQueue_t mux_queue_struct;
static QueueHandle_t mux_queue;

static scale_handle_t scale;
static clock_handle_t clock_hw;

static void Tarea_USB(void *pvParameters);
static void Tarea_Control(void *pvParameters);
static void Tarea_Mux_Serial(void *pvParameters);

void app_main_init(void) {
    hal_gpio_init();
    hal_uart_init();

    scale_config_t scale_cfg = {
        .read_byte = hal_uart_read_byte,
        .clear_buffer = hal_uart_clear_rx_buffer
    };
    scale = scale_driver_init(&scale_cfg);

    clock_config_t clock_cfg = {
        .read_byte = hal_uart_read_byte,
        .clear_buffer = hal_uart_clear_rx_buffer
    };
    clock_hw = clock_driver_init(&clock_cfg);

    cmd_queue = xQueueCreateStatic(CMD_QUEUE_LEN, sizeof(app_cmd_t), cmd_queue_storage, &cmd_queue_struct);
    mux_queue = xQueueCreateStatic(2, sizeof(mux_req_t), mux_queue_storage, &mux_queue_struct);

    xTaskCreateStatic(Tarea_USB, "Tarea_USB", TAREA_USB_STACK_SIZE, NULL, 2, tarea_usb_stack, &tarea_usb_tcb);
    xTaskCreateStatic(Tarea_Control, "Tarea_Control", TAREA_CONTROL_STACK_SIZE, NULL, 3, tarea_control_stack, &tarea_control_tcb);
    xTaskCreateStatic(Tarea_Mux_Serial, "Tarea_Mux", TAREA_MUX_STACK_SIZE, NULL, 4, tarea_mux_stack, &tarea_mux_tcb);
}

static void Tarea_USB(void *pvParameters) {
    (void)pvParameters;
    char rx_buf[32];
    uint8_t rx_idx = 0;
    
    while(1) {
        uint8_t byte;
        if (hal_usb_read_bytes(&byte, 1) > 0) {
            if (byte == '\0' || byte == '\n' || byte == '\r') {
                if (rx_idx > 0) {
                    rx_buf[rx_idx] = '\0';
                    app_cmd_t cmd = app_parse_command(rx_buf);
                    if (cmd != CMD_NONE) {
                        xQueueSend(cmd_queue, &cmd, 0);
                    }
                    rx_idx = 0;
                }
            } else {
                if (rx_idx < sizeof(rx_buf) - 1) {
                    rx_buf[rx_idx++] = byte;
                }
            }
        } else {
            vTaskDelay(pdMS_TO_TICKS(10));
        }
    }
}

static void Tarea_Control(void *pvParameters) {
    (void)pvParameters;
    app_cmd_t cmd;

    while(1) {
        if (xQueueReceive(cmd_queue, &cmd, portMAX_DELAY) == pdTRUE) {
            switch(cmd) {
                case CMD_INICIAR_ENSAYO:
                    hal_gpio_write(HAL_PIN_PB9_VALVE_WEIGH, true);
                    hal_gpio_write(HAL_PIN_PB8_TANK_SEL, false);
                    hal_gpio_write(HAL_PIN_PB7_VALVE_REC, false);
                    break;
                case CMD_FINALIZAR_ENSAYO: {
                    mux_req_t req = { .type = REQ_CLOCK, .notify_task = xTaskGetCurrentTaskHandle() };
                    xQueueSend(mux_queue, &req, portMAX_DELAY);
                    ulTaskNotifyTake(pdTRUE, portMAX_DELAY);
                    
                    hal_gpio_write(HAL_PIN_PB7_VALVE_REC, true);
                    hal_gpio_write(HAL_PIN_PB8_TANK_SEL, true);
                    hal_gpio_write(HAL_PIN_PB9_VALVE_WEIGH, false);
                    
                    if (req.status == STATUS_OK) {
                        uint16_t len = strlen(req.response);
                        req.response[len] = '\0'; // ensure null termination
                        hal_usb_transmit((uint8_t*)req.response, len + 1); // send with null terminator
                    }
                    break;
                }
                case CMD_MEDICION_BALANZA: {
                    mux_req_t req = { .type = REQ_SCALE, .notify_task = xTaskGetCurrentTaskHandle() };
                    xQueueSend(mux_queue, &req, portMAX_DELAY);
                    ulTaskNotifyTake(pdTRUE, portMAX_DELAY);
                    
                    if (req.status == STATUS_OK) {
                        uint16_t len = strlen(req.response);
                        req.response[len] = '\0';
                        hal_usb_transmit((uint8_t*)req.response, len + 1);
                    }
                    break;
                }
                case CMD_MEDICION_RELOJ: {
                    mux_req_t req = { .type = REQ_CLOCK, .notify_task = xTaskGetCurrentTaskHandle() };
                    xQueueSend(mux_queue, &req, portMAX_DELAY);
                    ulTaskNotifyTake(pdTRUE, portMAX_DELAY);
                    
                    if (req.status == STATUS_OK) {
                        uint16_t len = strlen(req.response);
                        req.response[len] = '\0';
                        hal_usb_transmit((uint8_t*)req.response, len + 1);
                    }
                    break;
                }
                case CMD_MEDICION_COMPLETA: {
                    mux_req_t req_scale = { .type = REQ_SCALE, .notify_task = xTaskGetCurrentTaskHandle() };
                    xQueueSend(mux_queue, &req_scale, portMAX_DELAY);
                    ulTaskNotifyTake(pdTRUE, portMAX_DELAY);
                    
                    if (req_scale.status == STATUS_OK) {
                        uint16_t len = strlen(req_scale.response);
                        req_scale.response[len] = '\0';
                        hal_usb_transmit((uint8_t*)req_scale.response, len + 1);
                    }
                    
                    // Small delay to separate transmissions if needed, but the PC expects 2 strings.
                    // Wait until USB finishes sending? The transmit function is blocking while BUSY.
                    
                    mux_req_t req_clock = { .type = REQ_CLOCK, .notify_task = xTaskGetCurrentTaskHandle() };
                    xQueueSend(mux_queue, &req_clock, portMAX_DELAY);
                    ulTaskNotifyTake(pdTRUE, portMAX_DELAY);
                    
                    if (req_clock.status == STATUS_OK) {
                        uint16_t len = strlen(req_clock.response);
                        req_clock.response[len] = '\0';
                        hal_usb_transmit((uint8_t*)req_clock.response, len + 1);
                    }
                    break;
                }
                default:
                    break;
            }
        }
    }
}

static void Tarea_Mux_Serial(void *pvParameters) {
    (void)pvParameters;
    mux_req_t req;

    while(1) {
        if (xQueueReceive(mux_queue, &req, portMAX_DELAY) == pdTRUE) {
            hal_gpio_write(HAL_PIN_PB5_MUX_EN, false); // enable mux

            if (req.type == REQ_SCALE) {
                hal_gpio_write(HAL_PIN_PB6_MUX_SEL, false);
                vTaskDelay(pdMS_TO_TICKS(10)); // allow mux to settle
                hal_uart_clear_rx_buffer();
                req.status = scale_driver_read(scale, req.response, 1000);
            } else if (req.type == REQ_CLOCK) {
                hal_gpio_write(HAL_PIN_PB6_MUX_SEL, true);
                vTaskDelay(pdMS_TO_TICKS(10));
                hal_uart_clear_rx_buffer();
                req.status = clock_driver_read(clock_hw, req.response, 1000);
            }

            xTaskNotifyGive(req.notify_task);
        }
    }
}

// Required for FreeRTOS static allocation
void vApplicationGetIdleTaskMemory( StaticTask_t **ppxIdleTaskTCBBuffer,
                                    StackType_t **ppxIdleTaskStackBuffer,
                                    uint32_t *pulIdleTaskStackSize ) {
    static StaticTask_t xIdleTaskTCB;
    static StackType_t uxIdleTaskStack[configMINIMAL_STACK_SIZE];
    *ppxIdleTaskTCBBuffer = &xIdleTaskTCB;
    *ppxIdleTaskStackBuffer = uxIdleTaskStack;
    *pulIdleTaskStackSize = configMINIMAL_STACK_SIZE;
}

void vApplicationGetTimerTaskMemory( StaticTask_t **ppxTimerTaskTCBBuffer,
                                     StackType_t **ppxTimerTaskStackBuffer,
                                     uint32_t *pulTimerTaskStackSize ) {
    static StaticTask_t xTimerTaskTCB;
    static StackType_t uxTimerTaskStack[configMINIMAL_STACK_SIZE];
    *ppxTimerTaskTCBBuffer = &xTimerTaskTCB;
    *ppxTimerTaskStackBuffer = uxTimerTaskStack;
    *pulTimerTaskStackSize = configMINIMAL_STACK_SIZE;
}
