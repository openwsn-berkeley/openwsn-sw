
#include <string.h>
#include "./Services/usb2serial.h"
#include "./Services/commands.h"
#include "./Services/commands_flash.h"
#include "Microchip/Include/Compiler.h"

#include "./Drivers/leds.h"
#include "Drivers/atflash.h"


void commands_flash_init(void) {
}

void commands_FLASH_START_READ(void) {
    AT45ADDR addr = *((AT45ADDR*)(packet_buffer + 1));
    int bytes_done = 0;
    atflash_cancel();
    atflash_start_read(addr);
    while(bytes_done < 256) {
        packet_buffer[bytes_done] = atflash_cont_read();
        bytes_done++;
    }
    
    packet_send_len = bytes_done;
}

void commands_FLASH_CONTINUE_READ(void) {
    unsigned int bytes_done = 0;

    while(bytes_done < 256) {
        packet_buffer[bytes_done] = atflash_cont_read();
        bytes_done++;
    }

    packet_send_len = bytes_done;
}

void commands_FLASH_STOP_READ(void) {
    atflash_stop_read();
}

void commands_FLASH_START_WRITE(void) {
    AT45ADDR addr = *((AT45ADDR*)(packet_buffer + 1));
    unsigned int bytes_done = 0;
    atflash_cancel();
    atflash_start_write(addr);
    
    while(bytes_done + 5 < packet_buffer_len) {
        atflash_cont_write(packet_buffer[bytes_done + 5]);
        bytes_done++;
    }
}

void commands_FLASH_CONTINUE_WRITE(void) {
    unsigned int bytes_done = 0;

    while ( bytes_done + 1 < packet_buffer_len ) {
        atflash_cont_write( packet_buffer[bytes_done + 1] );
        bytes_done++;
    }
}

void commands_FLASH_STOP_WRITE(void) {
    atflash_stop_write();
}