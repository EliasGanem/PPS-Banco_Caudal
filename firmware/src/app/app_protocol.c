#include "app/app_protocol.h"
#include <string.h>

app_cmd_t app_parse_command(const char *cmd_str) {
    if (strcmp(cmd_str, "INICIAR ENSAYO") == 0) {
        return CMD_INICIAR_ENSAYO;
    } else if (strcmp(cmd_str, "FINALIZAR ENSAYO") == 0) {
        return CMD_FINALIZAR_ENSAYO;
    } else if (strcmp(cmd_str, "MEDICION BALANZA") == 0) {
        return CMD_MEDICION_BALANZA;
    } else if (strcmp(cmd_str, "MEDICION RELOJ") == 0) {
        return CMD_MEDICION_RELOJ;
    } else if (strcmp(cmd_str, "MEDICION COMPLETA") == 0) {
        return CMD_MEDICION_COMPLETA;
    }
    return CMD_NONE;
}
