```text

device SmartButton:
  events: 
    buttonPressedOnce, buttonPressedTwice, buttonPressedLong
  behaviour:
    begin -> all
    buttonPressedOnce -> all
    buttonPressedTwice -> all
    buttonPressedLong -> all
  devices:
    Timer t
    Button b
  triggers:
    buttonPressedOnce <- b.pressed; t.started; b.released; t.canceled; t.started; t.timeout
    buttonPressedTwice <- b.pressed; t.started; b.released; t.canceled; t.started; b.pressed; (t.canceled and b.released)
    buttonPressedLong <- b.pressed; t.started; t.timeout; b.released
```