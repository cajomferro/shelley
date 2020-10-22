```text

device Timer:
  actions:
    start, cancel
  events: 
    started, canceled, timeout 
  behaviour:
    begin -> start:started
    started -> cancel:canceled or timeout
    canceled -> start:started
    timeout -> start:started
```