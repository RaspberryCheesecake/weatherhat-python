import weatherhat
import anvil.server
import os
import ST7789
from time import sleep
from PIL import Image

sensor = weatherhat.WeatherHAT()

print(f"""
anvil_uplink.py - Example showing how to send sensor data from Weather HAT into an Anvil web dashboard.
Sign up for an account at https://anvil.works/new-build to obtain a client uplink key.
Press Ctrl+C to exit!
""")

if "CLIENT_UPLINK_KEY" in os.environ:
    # Works if you've saved the uplink key on your Raspberry Pi already
    CLIENT_UPLINK_KEY = os.environ["CLIENT_UPLINK_KEY"]
else:
    # Alternatively, fill in your Anvil app's Client Uplink Key here:
    CLIENT_UPLINK_KEY = "YOUR CLIENT UPLINK KEY HERE"
    # Remember, your key is a secret, so make sure not to share it when you publish this code!

# Read the BME280 and discard the initial nonsense readings
sensor.update(interval=10.0)
temperature = sensor.temperature
humidity = sensor.relative_humidity
pressure = sensor.pressure
print("Discarding the first few BME280 readings (they aren't accurate)...")
sleep(10.0)

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
WIDTH = disp.width
HEIGHT = disp.height

# Open and resize uploading indicator image
my_path = os.path.abspath(os.path.dirname(__file__))
image_path = os.path.join(my_path, "icons/anvil-uploading.png")
status_image = Image.open(image_path)
status_image = status_image.resize((WIDTH, HEIGHT))

try:
    disp.display(status_image)

    while True:
        sensor.temperature_offset = -7.6
        sensor.update(interval=60.0)
        wind_direction_cardinal = sensor.degrees_to_cardinal(sensor.wind_direction)

        weather_data_dict = {
            'Temperature': sensor.temperature,
            'Humidity': sensor.humidity,
            'Dewpoint': sensor.dewpoint,
            'Wind': sensor.wind_speed * 1.944,  # m/s -> knots
            'Wind Direction': wind_direction_cardinal,
            'Rainfall': sensor.rain,  # mm/sec
            'Pressure': sensor.pressure,
            }

        try:
            anvil.server.connect(CLIENT_UPLINK_KEY)
            anvil.server.call('store_latest_weather_hat_data', weather_data_dict)
            print(f"""
                Uploading weather data...

                {weather_data_dict}
                
                Will measure again in 5 min
                Ctrl+C to exit

                """)
        except Exception as e:
            print("Upload failed due to: {}".format(e))

        sleep(300.0)  # Then attempt to store data again every 5 min

except KeyboardInterrupt:
    print("Finished data upload. Restart script to continue.")

finally:
    anvil.server.disconnect()
    done_image = Image.new('RGB', (WIDTH, HEIGHT), color=(0, 0, 0))
    disp.display(done_image)
