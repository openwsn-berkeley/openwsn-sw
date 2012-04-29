#include "Microchip/Include/Compiler.h"
#include "../Drivers/atflash.h"
#include "SPI.h"
#include "delays.h"
#include "TimeDelay.h"

AT45ADDR current_address;
#define SPI_DUMMY 0x00

unsigned char atflash_sel;
#define CSH {if(atflash_sel) { CSH1; } else {CSH2;}}
#define CSL {if(atflash_sel) { CSL1; } else {CSL2;}}

enum{
    IDLE,
    READING,
    WRITING
} atflash_state;

char need_to_open_page = 0;

void atflash_sendcmd(unsigned char cmd) {
    CSL;
    spi_write(cmd);
}

void atflash_sendaddr(AT45ADDR addr) {
    addr &= MEM_PER_CHIP - 1;
    spi_write(addr>>15);
    spi_write((addr>>7)&0xFC | ((addr>>8)&0x1)); // BA8 is always 0
    spi_write(addr&0xFF);
}

void atflash_init() {
    CSH1;
    CSH2;
    atflash_initCS();
    // wait 20mS
    Delay10KTCYx(24);
    atflash_sel = 0;
    atflash_poll_busy();
    atflash_sel = 1;
    atflash_poll_busy();
    atflash_state = IDLE;
}

void atflash_start_write(AT45ADDR addr) {
    if ( addr & MEM_PER_CHIP) {
        atflash_sel = 1;
    } else {
        atflash_sel = 0;
    }
    addr ^= addr & (PAGE_BOUNDARY-1);

    current_address = addr;
    atflash_sendcmd(AT45_PROGRAM_THROUGH_BUF1);
    atflash_sendaddr(addr);
    need_to_open_page = 0;
    atflash_state = WRITING;
}

void atflash_cont_write(unsigned char dat) {
        if ( need_to_open_page ) {
            CSH;
            atflash_poll_busy();
            atflash_start_write(current_address);
            need_to_open_page = 0;
        }

        spi_write(dat);
        current_address++;

	if ( 0 == (current_address & (PAGE_BOUNDARY-1)) ){ // closeout page
            need_to_open_page = 1;
	}
}

void atflash_start_read(AT45ADDR addr) {
    if ( addr & MEM_PER_CHIP) {
        atflash_sel = 1;
    } else {
        atflash_sel = 0;
    }

    current_address = addr;
    atflash_sendcmd(AT45_PAGE_READ);
    atflash_sendaddr(addr);
    atflash_dummy(4);
    atflash_state = READING;
}

char atflash_cont_read() {
    char ch = spi_write(SPI_DUMMY);
    current_address++;

    if ( 0 == (current_address & (PAGE_BOUNDARY-1)) ){ // closeout page
            CSH;
            atflash_start_read(current_address);
    }

    return ch;
}

void atflash_stop_write() {
    CSH;
    atflash_poll_busy();
    atflash_state = IDLE;
}

void atflash_stop_read() {
    CSH;
    atflash_state = IDLE;
}

char atflash_getch() {
    return spi_write(SPI_DUMMY);;
}

void atflash_dummy(char num) {
    while(num) {
        spi_write(SPI_DUMMY);
        num--;
    }
}

void atflash_poll_busy() {
    char stat = 0;

    atflash_sendcmd(AT45_READ_STATUS);

    do {
        stat = atflash_getch();
    } while ( 0 == (stat & 0x80) );
    CSH;
}

char atflash_busy(void) {
    return atflash_state != IDLE;
}

void atflash_cancel(void) {
    switch (atflash_state) {
        case IDLE:
            return;
        case READING:
            atflash_stop_read();
            break;
        case WRITING:
            atflash_stop_write();
            break;
    }
}