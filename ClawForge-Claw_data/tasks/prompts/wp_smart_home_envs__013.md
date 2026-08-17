Hi,

I'm Jane, a resident in a smart home. I have asthma, so the indoor climate matters a lot. Right now it's 14:30, peak electricity hours, and I need to check which devices are running that conflict with my health conditions. I've dumped all the system data into the working directory: health profiles in `data/health/`, device info in `data/devices/`, current device status in `data/devices/status.json`, electricity rates in `data/electricity/`, and the current time in `current_time.txt`. Also there's weather data in `data/weather/`.

Can you please analyze and produce a list of devices that are both active during peak hours and whose current settings are out of my health comfort zone? I need the result saved as `ops/conflicts.json`, with each entry containing the `device_id` and a brief reason for the conflict. Just the essentials, no extra fluff. Thanks!
