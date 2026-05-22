#ifndef APP_CONTROL_H
#define APP_CONTROL_H

#include "freertos/FreeRTOS.h"
#include "freertos/queue.h"

/**
 * @brief Comandos soportados provenientes de la PC (USB)
 */
typedef enum {
    CMD_INICIAR_ENSAYO,
    CMD_INICIAR_RETORNO,
    CMD_FINALIZAR_ENSAYO,
    CMD_FINALIZAR_RETORNO,
    CMD_MEDICION_BALANZA,
    CMD_MEDICION_RELOJ,
    CMD_MEDICION_COMPLETA,
    CMD_DESCONOCIDO
} app_cmd_t;

/**
 * @brief Inicializa los pines de control y pone el sistema en MODO_RECIRCULACION
 */
void App_Control_Init(void);

/**
 * @brief Envía un comando a la cola de control principal
 */
void App_Control_SendCmd(app_cmd_t cmd);

/**
 * @brief Tarea principal de control (Máquina de estados)
 */
void App_Control_Task(void *pvParameters);

#endif // APP_CONTROL_H
