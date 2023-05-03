# Error explanation

```
 initial boot -> start_http_ok, start_http_err {
  {m.locked; m.unlocked; p.cancel;}
 }
 initial wake_up -> start_http_ok, start_http_err {
  {m.locked; m.unlocked; p.cancel;} + {p.wakeup;}
 }
 ```
Both the `boot` and `wake_up`operations start with the exact same sub-operations. How do we decide?! This is ambiguous!

By omitting the `Controller.boot` operation it is possible to observe a `p.wakeup` before a `p.sleep`or `p.cancel`.

This is wrong according to the `PowerHandler`spec.

### DIRECT

```
Invalid device: AmbiguityFailure(micro_trace=('m.locked', 'm.unlocked', 'p.cancel'), macro_traces=(('wake_up',), ('boot',)))
```

### NUSMV

WARNING: NuSMV is does not check ambiguity!