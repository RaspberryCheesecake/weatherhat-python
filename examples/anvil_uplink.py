import weatherhat
import anvil.server
import os
from time import sleep

sensor = weatherhat.WeatherHAT()

print(f"""
Connect to uplink and give stored weather table results from the sensors
Press Ctrl+C to exit!
""")

if "CLIENT_UPLINK_KEY" in os.environ:
    anvil.server.connect(os.environ["CLIENT_UPLINK_KEY"])
else:
    print("Woops, couldn't find uplink key - did you set one locally?")

while True:
    sensor.update(interval=60.0)

    wind_direction_cardinal = sensor.degrees_to_cardinal(sensor.wind_direction)

    weather_data_dict = {
        'Temperature': sensor.temperature,  # TODO double check if offset ok for my setup (sensor.temperature_offset)
        'Humidity': sensor.humidity,
        'Dewpoint': sensor.dewpoint,
        'Wind': sensor.wind_speed * 1.944,  # m/s -> knots
        'Wind Direction': wind_direction_cardinal,
        'Rainfall': sensor.rain,  # mm/sec
        'Pressure': sensor.pressure,
        }

    anvil.server.call('store_latest_weather_hat_data', weather_data_dict)

    print(f"""
System temp: {sensor.device_temperature:0.2f} *C
Temperature: {sensor.temperature:0.2f} *C

Humidity:    {sensor.humidity:0.2f} %
Dew point:   {sensor.dewpoint:0.2f} *C

Light:       {sensor.lux:0.2f} Lux

Pressure:    {sensor.pressure:0.2f} hPa

Wind (avg):  {sensor.wind_speed:0.2f} m/sec

Rain:        {sensor.rain:0.2f} mm/sec

Wind (avg):  {sensor.wind_direction:0.2f} degrees ({wind_direction_cardinal})

""")

    sleep(30.0)  # Then store data again
