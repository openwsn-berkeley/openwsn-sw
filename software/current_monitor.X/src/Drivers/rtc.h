#ifndef RTC_H
#define RTC_H

extern volatile UINT32 current_time_s;
void rtc_init();

void rtc_set_time(UINT32 time);

#endif