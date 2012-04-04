
#include "GenericTypeDefs.h"
#include "Compiler.h"
#include "HardwareProfile.h"
#include "Drivers/currentADC.h"
#include "commands_adc.h"
#include "./Services/commands.h"

void commands_ADC_READ_IMMEDIATE() {
    currentADC_trigger();
    while(current_reading_high == CURRENT_READING_IN_PROGRESS);
    while(current_reading_low == CURRENT_READING_IN_PROGRESS);
    packet_buffer[0] = current_reading_low & 0xFF;
    packet_buffer[1] = (current_reading_low >> 8) & 0xFF;
    packet_buffer[2] = current_reading_high & 0xFF;
    packet_buffer[3] = (current_reading_high >> 8) & 0xFF;

    packet_send_len = 4;
}