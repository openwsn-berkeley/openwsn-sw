
#include <string.h>
#include "./Services/usb2serial.h"
#include "./Services/commands.h"
#include "./Services/commands_flash.h"
#include "Microchip/Include/Compiler.h"

#include "./Drivers/leds.h"
#include "Drivers/atflash.h"

AT45ADDR bytes_done;
AT45ADDR request_len;

void commands_flash_init(void) {
    bytes_done = 0;
}

void commands_FLASH_START_READ(void) {
    AT45ADDR addr = *((AT45ADDR*)(packet_buffer + 1));
    request_len = *((AT45ADDR*)(packet_buffer + 5));
    atflash_cancel();
    atflash_start_read(addr);
    bytes_done = 0;
    while(bytes_done < 256 && bytes_done < request_len) {
        packet_buffer[bytes_done] = atflash_cont_read();
        bytes_done++;
    }

    if ( bytes_done == request_len ) {
        atflash_stop_read();
    }
    
    packet_send_len = bytes_done;
}

void commands_FLASH_CONTINUE_READ(void) {
    unsigned int pack_pos, pack_len;

    pack_pos = 0;
    if ( request_len - bytes_done > 256)  {
        pack_len = 256;
    } else {
        pack_len = request_len-bytes_done;
    }
    while ( pack_pos < pack_len ) {
        packet_buffer[pack_pos] = atflash_cont_read();
        pack_pos++;
    }
    bytes_done += pack_len;

    if ( bytes_done == request_len ) {
        atflash_stop_read();
    }
    packet_send_len = pack_len;
}

void commands_FLASH_STOP_READ(void) {
    atflash_stop_read();
}

void commands_FLASH_START_WRITE(void) {
    AT45ADDR addr = *((AT45ADDR*)(packet_buffer + 1));
    request_len = *((AT45ADDR*)(packet_buffer + 5));
    // at position 7 now
    atflash_cancel();
    atflash_start_write(addr);

    bytes_done = 0;
    while(bytes_done + 7 < packet_buffer_len && bytes_done < request_len) {
        atflash_cont_write(packet_buffer[bytes_done + 9]);
        bytes_done++;
    }

    if ( bytes_done == request_len ) {
        atflash_stop_write();
    }
}

void commands_FLASH_CONTINUE_WRITE(void) {
    unsigned int pack_pos = 0, pack_len;
    if ( request_len - bytes_done > 255)  {
        pack_len = 255;
    } else {
        pack_len = request_len-bytes_done;
    }
    while ( pack_pos < pack_len && pack_pos + 1 < packet_buffer_len ) {
        atflash_cont_write( packet_buffer[pack_pos + 1] );
        pack_pos++;
    }
    bytes_done += pack_pos;

    if ( bytes_done == request_len ) {
        atflash_stop_write();
    }
}

void commands_FLASH_STOP_WRITE(void) {
    atflash_stop_write();
}