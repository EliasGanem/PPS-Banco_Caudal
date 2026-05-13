#include "app_control.h"
#include "../hal/hal_gpio.h"
#include "app_rs232_task.h"
#include "app_usb_task.h"
#include "board_config.h"
#include "freertos/task.h"
#include <stdio.h>

static QueueHandle_t cmd_queue;

static void set_modo_recirculacion(void) {
  HAL_GPIO_Write(PIN_VALV_PESADA, !LOGIC_VALV_PESADA_ACTIVE); // Forzar OFF
  HAL_GPIO_Write(PIN_SEL_TANQUE, VAL_SEL_TANQUE_RECIRCULACION);
  HAL_GPIO_Write(PIN_VALV_RECIRC, LOGIC_VALV_RECIRC_ACTIVE); // ON
}

void App_Control_Init(void) {
  cmd_queue = xQueueCreate(10, sizeof(app_cmd_t));

  // Inicializar pines
  HAL_GPIO_Init(PIN_HAB_MUX, HAL_GPIO_MODE_OUTPUT);
  HAL_GPIO_Init(PIN_SELECTOR_UART, HAL_GPIO_MODE_OUTPUT);
  HAL_GPIO_Init(PIN_VALV_RECIRC, HAL_GPIO_MODE_OUTPUT);
  HAL_GPIO_Init(PIN_SEL_TANQUE, HAL_GPIO_MODE_OUTPUT);
  HAL_GPIO_Init(PIN_VALV_PESADA, HAL_GPIO_MODE_OUTPUT);

  // Estado inicial seguro
  set_modo_recirculacion();
}

void App_Control_SendCmd(app_cmd_t cmd) {
  if (cmd_queue != NULL) {
    if (cmd == CMD_INICIAR_ENSAYO || cmd == CMD_INICIAR_RETORNO || 
        cmd == CMD_FINALIZAR_ENSAYO || cmd == CMD_FINALIZAR_RETORNO) {
        // Comandos críticos: Limpiamos la cola de mediciones pendientes
        // para asegurar que el cambio de estado se ejecute de inmediato y no sea descartado.
        xQueueReset(cmd_queue);
        xQueueSendToFront(cmd_queue, &cmd, 0);
    } else {
        // Comandos de medición (se encolan normalmente)
        xQueueSendToBack(cmd_queue, &cmd, 0);
    }
  }
}

void App_Control_Task(void *pvParameters) {
  app_cmd_t cmd;

  while (1) {
    if (xQueueReceive(cmd_queue, &cmd, portMAX_DELAY) == pdTRUE) {
      switch (cmd) {
      case CMD_INICIAR_ENSAYO:
        HAL_GPIO_Write(PIN_VALV_RECIRC, LOGIC_VALV_RECIRC_ACTIVE);
        HAL_GPIO_Write(PIN_SEL_TANQUE, VAL_SEL_TANQUE_PESADA);
        break;

      case CMD_INICIAR_RETORNO:
        HAL_GPIO_Write(PIN_VALV_PESADA, LOGIC_VALV_PESADA_ACTIVE);
        // Breve espera para asegurar apertura antes de cerrar recirculación
        vTaskDelay(pdMS_TO_TICKS(100));
        HAL_GPIO_Write(PIN_VALV_RECIRC, !LOGIC_VALV_RECIRC_ACTIVE);
        HAL_GPIO_Write(PIN_SEL_TANQUE, VAL_SEL_TANQUE_RECIRCULACION);
        break;

      case CMD_FINALIZAR_ENSAYO: {
        // Aplicar estado seguro INMEDIATAMENTE
        set_modo_recirculacion();

        // Luego leer el reloj de forma segura
        char reloj_buf[9];
        bool reloj_ok = App_RS232_ReadReloj(reloj_buf);

        if (reloj_ok) {
          App_USB_SendBytes((const uint8_t *)reloj_buf, 9);
        }
        break;
      }

      case CMD_FINALIZAR_RETORNO:
        set_modo_recirculacion();
        break;

      case CMD_MEDICION_BALANZA: {
        char balanza_buf[16];
        if (App_RS232_ReadBalanza(balanza_buf)) {
          // El buffer ya viene terminado en nulo desde la función de lectura
          App_USB_SendString(balanza_buf);
          // También se debe mandar el \0 según la regla ("P.PP\0")
          // uint8_t nulo = '\0';
          // App_USB_SendBytes(&nulo, 1);
        }
        break;
      }

      case CMD_MEDICION_RELOJ: {
        char reloj_buf[9];
        if (App_RS232_ReadReloj(reloj_buf)) {
          App_USB_SendBytes((const uint8_t *)reloj_buf, 9);
        }
        break;
      }

      case CMD_MEDICION_COMPLETA: {
        char balanza_buf[16];
        char reloj_buf[9];
        bool b_ok = App_RS232_ReadBalanza(balanza_buf);
        bool r_ok = App_RS232_ReadReloj(reloj_buf);

        if (b_ok) {
          App_USB_SendString(balanza_buf);
          // uint8_t terminador = CMD_TERMINATOR_USB;
          // App_USB_SendBytes(&terminador, 1);
        }
        if (r_ok) {
          App_USB_SendBytes((const uint8_t *)reloj_buf, 9);
        }
        break;
      }

      default:
        break;
      }
    }
  }
}
