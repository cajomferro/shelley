```text

device Led:
    actions:
        turn_on, turn_off
    events: 
        on, off
    behaviour:
        begin -> turnOn:on or turnOff:off
        on  -> turnOff:off
        off -> turnOn:on or turnOff:off
```