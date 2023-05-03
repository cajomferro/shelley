# Error explanation

```
# initial boot -> start_http_ok, start_http_err {
#  {m.locked; m.unlocked; p.cancel;}
# }
 initial wake_up -> start_http_ok, start_http_err {
  {m.locked; m.unlocked; p.cancel;} + {p.wakeup;}
 }
```

By omitting the `Controller.boot` operation it is possible to observe a `p.wakeup` before a `p.sleep`or `p.cancel`.

This is wrong according to the `PowerHandler`spec.

### DIRECT

```
Invalid device: integration error

* system: wake_up, start_http_err, follow_plan, sleep
* integration: p.wakeup, w.begin_err, v.v1, v.v2, v.v3, v.v4, p.sleep
               ^^^^^^^^                                              
Instance errors:

  'p': wakeup, sleep
       ^^^^^^ 
```

### NUSMV

```
Error in specification: USAGE VALIDITY FOR p: PowerHandler
Formula: (ε | cancel) | sleep
Counter example: wakeup; sleep
```