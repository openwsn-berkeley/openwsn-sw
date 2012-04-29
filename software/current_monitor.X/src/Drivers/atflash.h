#ifndef ATFLASH_H
#define ATFLASH_H

typedef unsigned long long AT45ADDR;
#define MEM_PER_CHIP 0x400000l
#define PAGE_BOUNDARY 0x200

#define AT45_PAGE_READ 0xD2
#define AT45_CONTINUOUS_READ 0xE8
#define AT45_PROGRAM_THROUGH_BUF1 0x82
#define AT45_PROGRAM_THROUGH_BUF2 0x85

#define AT45_WRITE_BUF1 0x84
#define AT45_WRITE_BUF2 0x87
#define AT45_BUF1_TO_MEM 0x83
#define AT45_BUF2_TO_MEM 0x86

#define AT45_READ_STATUS 0xD7

#define atflash_initCS() { TRISBbits.TRISB1 = 0; TRISBbits.TRISB5 = 0; }
#define CSL1 LATBbits.LATB1 = 0
#define CSH1 LATBbits.LATB1 = 1
#define CSL2 LATBbits.LATB5 = 0
#define CSH2 LATBbits.LATB5 = 1

void atflash_sendcmd(unsigned char cmd);

void atflash_sendaddr(AT45ADDR addr);

void atflash_init(void);

void atflash_stop_write(void);

void atflash_stop_read(void);

void atflash_start_write(AT45ADDR addr);

void atflash_cont_write(unsigned char dat);

void atflash_start_read(AT45ADDR addr);

char atflash_cont_read(void);

void atflash_poll_busy(void);

char atflash_getch(void);

void atflash_dummy(char num);

char atflash_busy(void);

void atflash_cancel(void);

#endif