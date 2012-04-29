#ifndef COMMANDS_FLASH_H
#define COMMANDS_FLASH_H



void commands_flash_init(void);

void commands_FLASH_START_READ(void);
void commands_FLASH_CONTINUE_READ(void);
void commands_FLASH_STOP_READ(void);
void commands_FLASH_START_WRITE(void);
void commands_FLASH_CONTINUE_WRITE(void);
void commands_FLASH_STOP_WRITE(void);

#endif