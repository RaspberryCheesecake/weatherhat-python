import weatherhat
import anvil.server
import os
import ST7789
from time import sleep
from PIL import Image, ImageDraw, ImageFont
from fonts.ttf import ManropeBold as UserFont

sensor = weatherhat.WeatherHAT()

print(f"""
anvil_uplink.py - Example showing how to send sensor data from Weather HAT into an Anvil web dashboard.
Sign up for an account at https://anvil.works/new-build to obtain a client uplink key.
Press Ctrl+C to exit!
""")

if "CLIENT_UPLINK_KEY" in os.environ:
    anvil.server.connect(os.environ["CLIENT_UPLINK_KEY"])
else:
    print("Woops, couldn't find uplink key - did you set one locally?")


SPI_SPEED_MHZ = 80

# Create LCD class instance.
disp = ST7789.ST7789(
    rotation=90,
    port=0,
    cs=1,
    dc=9,
    backlight=13,
    spi_speed_hz=SPI_SPEED_MHZ * 1000 * 1000
)

# Initialize display.
disp.begin()

# Width and height to calculate text position.
WIDTH = disp.width
HEIGHT = disp.height

# New canvas to draw on.
img = Image.new('RGB', (WIDTH, HEIGHT), color=(0, 0, 0))
draw = ImageDraw.Draw(img)

# Text settings.
font_size = 12
font = ImageFont.truetype(UserFont, font_size)
text_colour = (255, 255, 255)
back_colour = (0, 170, 170)

message = "Uploading weather data to Anvil️"
size_x, size_y = draw.textsize(message, font)

# Calculate text position
x = (WIDTH - size_x) / 2
y = (HEIGHT / 2) - (size_y / 2)

# Draw background rectangle and write text.
draw.rectangle((0, 0, WIDTH, HEIGHT), back_colour)
draw.text((x, y), message, font=font, fill=text_colour)
disp.display(img)

# Keep running
try:
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

except KeyboardInterrupt:
    print("Stopping.")
    img = Image.new('RGB', (WIDTH, HEIGHT), color=(0, 0, 0))
    disp.display(img)

