## Controller Final states
### Main files:
- controller_finalstates.yml
### Deps:
- ../aquamote_valve/valve.scy
- ../aquamote_magnetic/magnetic.scy
- ../aquamote_radio_simple/radio_finalstates.scy
- ../aquamote_lowpower/lowpower-strict-finalstates.scy

### Goal
Radio and LowPower modules restrict what are the possible final states. This forces Controller to be more restrictive.

---

## Controller using radio V1 and using a LowPower (not strict)
### Main files:
- controller_radio_v1.yml
### Deps:
- ../aquamote_valve/valve.scy
- ../aquamote_magnetic/magnetic.scy
- ../aquamote_radio_simple/radio_v1.scy
- ../aquamote_lowpower/lowpower.scy

### Goal
RadioV1 doesn't have integration.
LowPower is not restrictive in the sense that allows all operations to be initial and final. 

---

## Controller using radio V1 and using a LowPower (strict)
### Main files:
- controller_radio_v1_lp_strict.yml
### Deps:
- ../aquamote_valve/valve.scy
- ../aquamote_magnetic/magnetic.scy
- ../aquamote_radio_simple/radio_v1.scy
- ../aquamote_lowpower/lowpower-strict.scy

### Goal
RadioV1 doesn't have integration. 
LowPower is restrictive and only some operations are allowed to be initial or final. 

---

## Controller using radio V3 and using a LowPower (strict)
### Main files:
- controller_radio_v3_lp_strict.yml
### Deps:
- ../aquamote_valve/valve.scy
- ../aquamote_magnetic/magnetic.scy
- ../aquamote_radio_simple/radio_v3.scy --> ../aquamote_radio_simple/radio_v2.scy --> ../aquamote_radio_simple/radio_v1.scy
- ../aquamote_lowpower/lowpower-strict.scy

### Goal
RadioV3 uses integration (it depends on RadioV2 that depends on RadioV1). RadioV3 has the simplest API, in the sense 
that offers less operations because a lot of operations are hidden by its subsystems.
LowPower is restrictive and only some operations are allowed to be initial or final. 

---

## Controller using radio V3, using a LowPower (strict) and using a ValveHandler (without timer)
### Main files:
- controller_valvehandler.yml
### Deps:
- ../aquamote_valvehandler/valvehandler.scy --> ../aquamote_valve/valve.scy
- ../aquamote_magnetic/magnetic.scy
- ../aquamote_radio_simple/radio_v3.scy --> ../aquamote_radio_simple/radio_v2.scy --> ../aquamote_radio_simple/radio_v1.scy
- ../aquamote_lowpower/lowpower-strict.scy

### Goal
Same as controller_radio_v3_lp_strict.yml but now focusing on having a valve handler that simplifies API for controlling valves.

---

## Controller using radio V3, using a LowPower (strict) and using a ValveHandler (with timer)
### Main files:
- controller_valvehandlertimer.yml
### Deps:
- ../aquamote_valvehandlertimer/valvehandlertimer.scy --> (../aquamote_valve/valve.scy AND ../base/timer.scy)
- ../aquamote_magnetic/magnetic.scy
- ../aquamote_radio_simple/radio_v3.scy --> ../aquamote_radio_simple/radio_v2.scy --> ../aquamote_radio_simple/radio_v1.scy
- ../aquamote_lowpower/lowpower-strict.scy

### Goal
Same as controller_radio_v3_lp_strict.yml but now focusing on having a valve handler with a timer that simplifies API for controlling valves.

---

## Controller with RadioClient 
### Main files:
- controller_radioclient.yml

### Deps:
- ../aquamote_valvehandlertimer/valvehandlertimer.scy --> (../aquamote_valve/valve.scy AND ../base/timer.scy)
- ../aquamote_magnetic/magnetic.scy
- ../aquamote_radio_client/radioclient.scy  --> (../aquamote_radio_client/httpclient.scy AND ../aquamote_radio_client/wificlient.scy)
- ../aquamote_lowpower/lowpower-strict.scy

### Goal
RadioClient is a version of radio that better models a real-world scenario. It integrates on HTTPClient and WiFiClient modules.

### Comments
The "problem" of this controller is that, although it tolerates error situations, the way "RadioClient" is designed
forces to stop and restart the radioclient (this includes disconnecting from server and from Wi-Fi router) every time
an error occurs.

--

## Controller with RadioClientV2
### Main files:
- controller_radioclient_v2.yml

### Deps:
- ../aquamote_valvehandlertimer/valvehandlertimer.scy --> (../aquamote_valve/valve.scy AND ../base/timer.scy)
- ../aquamote_magnetic/magnetic.scy
- ../aquamote_radio_client_v2/radioclient.scy  --> (../aquamote_radio_client_v2/httpclient.scy AND ../aquamote_radio_client_v2/wificlient.scy)
- ../aquamote_lowpower/lowpower-strict.scy

### Goal
RadioClientV2 improves RadioClient by better handling error scenarios. We can now connect and disconnect from server while
keeping Wi-Fi connection.

### Comments
The only problem of this solution is that we must have more operations in order to support the error scenarios.