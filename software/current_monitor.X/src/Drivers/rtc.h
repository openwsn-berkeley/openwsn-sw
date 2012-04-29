#ifndef RTC_H
#define RTC_H

extern volatile UINT32 current_time_s;
void rtc_init(void);

void rtc_set_time(UINT32 time);

void T1_interrupt(void);
#endif