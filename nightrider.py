def single_nightrider(pins):
  for item_counter in range(len(pins) + 4):
      input_state = GPIO.input(37)
        if input_state == True:
      return
    start_value = item_counter - 4
                for item_number in range(start_value ,start_value + 4):
            if item_number >= 0 and item_number < len(pins):
        GPIO.output(pins[item_number],GPIO.HIGH)
          sleep(0.15)
    led_low(pins)

def nightrider(pins):
    for _ in range(5):
      single_nightrider(pins)
  input_state = GPIO.input(37)
      if input_state == True:
    return
  sleep(0.4)
  single_nightrider(pins[::-1])
  input_state = GPIO.input(37)
  if input_state == True:
    return
  sleep(0.4)
    return