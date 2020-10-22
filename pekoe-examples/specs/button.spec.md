```text

device Button:
  events:
    pressed, released
  behaviour:
    begin -> pressed
    pressed -> released
    released -> pressed
```