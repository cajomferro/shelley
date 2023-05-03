## AquamoteCore using other components directly and adding more operations (now using radio)
### Main files:
- aquamote_core_v4.yml
### Deps:
  - ../base/timer.scy \
 - ../aquamote_valve/valve.scy \
 - ../aquamote_valvehandlertimer/valvehandlertimer.scy \
 - ../aquamote_magnetic/magnetic.scy \
 - ../aquamote_radio_client_v2/radioclient.scy \
 - ../aquamote_lowpower/lowpower-strict.scy

### Goal
Same as aquamote_core_v3 but using radio instead of gprs and http.

### Commands and output

    shelleyc -u uses.yml -d aquamote_core_v4.yml -o aquamote_core_v4.scy
    shelleyv --format pdf aquamote_core_v4.scy -o aquamote_core_v4.pdf
    Input: 10
    make aquamote_core_v4.pdf  2.50s user 0.08s system 96% cpu 2.666 total

    shelleyc -u uses.yml -d aquamote_core_v4.yml --skip-checks --no-output -i aquamote_core_v4.int
    shelleyv --dfa --minimize --no-sink --format pdf aquamote_core_v4.int -o aquamote_core_v4-i-d.pdf
    Input: 53
    No sinks: 44
    DFA: 45
    Minimized DFA: 37
    NFA no sink: 19
    rm aquamote_core_v4.int

    shelleyc -u uses.yml -d aquamote_core_v4.yml --skip-checks --no-output -i aquamote_core_v4.int
    shelleyv --no-sink --format pdf aquamote_core_v4.int -o aquamote_core_v4-i-n.pdf
    Input: 53
    Remove sink states: 44
    rm aquamote_core_v4.int

## Notes

### PowerHandler
```
PowerHandler
initial final cancel -> sleep # this must be initial too
```
A PowerHandler device that doesn't declare `cancel` as final wouldn't be compatible with the Controller because it 
may happen that there is a manual wake up (from the magnetic button) in between, before the `wakeup` happens.

```
Invalid device: integration error

* system: wake_up_manual, start_http_err, follow_plan, sleep
* integration: m.locked, m.unlocked, p.cancel, w.begin_err, v.v1, v.v2, v.v3, v.v4, p.sleep
                                     ^^^^^^^^                                              
Instance errors:

  'p': cancel, sleep
       ^^^^^^  
```

