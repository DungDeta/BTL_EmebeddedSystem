import time

import lgpio

RELAY_PIN = 17
h = lgpio.gpiochip_open(0)

# Cấu hình chân relay là Output
lgpio.gpio_claim_output(h, RELAY_PIN)

try:
    while True:
        # BẬT relay
        lgpio.gpio_write(h, RELAY_PIN, 1)
        print("Relay is ON")
        time.sleep(1)

        # TẮT relay
        lgpio.gpio_write(h, RELAY_PIN, 0)
        print("Relay is OFF")
        time.sleep(1)

except KeyboardInterrupt:
    print("Stopping program...")

finally:
    lgpio.gpiochip_close(h)
