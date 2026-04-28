#ifndef APP_PROTOCOL_H
#define APP_PROTOCOL_H

typedef enum {
    CMD_NONE = 0,
    CMD_INICIAR_ENSAYO,
    CMD_FINALIZAR_ENSAYO,
    CMD_MEDICION_BALANZA,
    CMD_MEDICION_RELOJ,
    CMD_MEDICION_COMPLETA
} app_cmd_t;

app_cmd_t app_parse_command(const char *cmd_str);

#endif /* APP_PROTOCOL_H */
