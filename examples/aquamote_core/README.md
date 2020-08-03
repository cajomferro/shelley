## AquamoteCore using other components directly, namely the RadioClientV2
### Main files:
- aquamote_core.yml
### Deps:
 - ../base/timer.scy \
 - ../aquamote_valve/valve.scy \
 - ../aquamote_valvehandlertimer/valvehandlertimer.scy \
 - ../aquamote_magnetic/magnetic.scy \
 - ../aquamote_radio_client_v2/radioclient.scy \
 - ../aquamote_lowpower/lowpower-strict.scy \
 
### Goal
Strictly following AquamoteCore implementation (each state in AquamoteCore is a Shelley operation).
The problem here is that several scenarios are not contemplated (e.g., error cases) because
this info is encoded in AquamoteCore states. Shelley doesn't have state info so extra
operations are required to deal with these cases.

### Commands and output

    shelleyc -u uses.yml -d aquamote_core.yml -o aquamote_core.scy
    shelleyv --format pdf aquamote_core.scy -o aquamote_core.pdf
    Input: 7
    make aquamote_core.pdf  1.90s user 0.10s system 71% cpu 2.800 total
        
    shelleyc -u uses.yml -d aquamote_core.yml --skip-checks --no-output -i aquamote_core.int
    shelleyv --dfa --minimize --no-sink --format pdf aquamote_core.int -o aquamote_core-i-d.pdf
    Input: 40
    No sinks: 34
    DFA: 35
    Minimized DFA: 31
    NFA no sink: 18
    rm aquamote_core.int
    make aquamote_core-i-d.pdf  2.34s user 0.10s system 81% cpu 2.997 total

    shelleyc -u uses.yml -d aquamote_core.yml --skip-checks --no-output -i aquamote_core.int
    shelleyv --no-sink --format pdf aquamote_core.int -o aquamote_core-i-n.pdf
    Input: 40
    Remove sink states: 34
    rm aquamote_core.int
    make aquamote_core-i-n.pdf  2.23s user 0.07s system 99% cpu 2.311 total

---

## AquamoteCore using controller_radioclient_v2 instead of separate components
### Main files:
- aquamote_core_v2.yml
### Deps:
 - ../aquamote_controller/controller_radioclient_v2.scy

### Goal
This example overcomes the earlier described limitations by adding more Shelley operations.
We try here to re-use the already implemented controller_radioclient_v2 Shelley specification
which simplifies the specification in terms of micro operations. However, abstracting operations
with other subsystems may render it impossible to deal with some low-level cases. For example, a
generic error in controller means an HTTP error? Or a GPRS error? 

### Commands and output

    shelleyc -u uses.yml -d aquamote_core_v2.yml --skip-checks --no-output -i aquamote_core_v2.int
    shelleyv --dfa --minimize --no-sink --format pdf aquamote_core_v2.int -o aquamote_core_v2-i-d.pdf
    Input: 39
    No sinks: 30
    DFA: 31
    Minimized DFA: 28
    NFA no sink: 10
    rm aquamote_core_v2.int
    make aquamote_core_v2-i-d.pdf  0.74s user 0.07s system 98% cpu 0.820 total

    shelleyc -u uses.yml -d aquamote_core_v2.yml --skip-checks --no-output -i aquamote_core_v2.int
    shelleyv --dfa --minimize --no-sink --format pdf aquamote_core_v2.int -o aquamote_core_v2-i-d.pdf
    Input: 39
    No sinks: 30
    DFA: 31
    Minimized DFA: 28
    NFA no sink: 10
    rm aquamote_core_v2.int
    make aquamote_core_v2-i-d.pdf  0.74s user 0.07s system 98% cpu 0.820 total

    shelleyc -u uses.yml -d aquamote_core_v2.yml --skip-checks --no-output -i aquamote_core_v2.int
    shelleyv --no-sink --format pdf aquamote_core_v2.int -o aquamote_core_v2-i-n.pdf
    Input: 39
    Remove sink states: 30
    rm aquamote_core_v2.int
    make aquamote_core_v2-i-n.pdf  0.74s user 0.07s system 98% cpu 0.819 total

---

## AquamoteCore using other components directly and adding more operations
### Main files:
- aquamote_core_v3.yml
### Deps:
  - ../base/timer.scy \
 - ../aquamote_valve/valve.scy \
 - ../aquamote_valvehandlertimer/valvehandlertimer.scy \
 - ../aquamote_magnetic/magnetic.scy \
 - ../aquamote_radio_client_v2/httpclient.scy \
 - ../aquamote_radio_client_v2/gprsclient.scy \
 - ../aquamote_lowpower/lowpower-strict.scy \

### Goal
This is a mixture of ther previous experiments. We use as subsystems other components directly 
(as opposed to using controller_radioclient_v2). We go even further by not using radioclient but 
using HTTP and GPRS clients directly. This gives us more flexibility in how to deal with micro events.
However, integration is more complex and it takes more time to compute. We also have more operations
as in aquamote_core_v2 in an attempt to better specify all scenarios in the original AquamoteCore.

### Commands and output

    shelleyc -u uses.yml -d aquamote_core_v3.yml -o aquamote_core_v3.scy
    shelleyv --format pdf aquamote_core_v3.scy -o aquamote_core_v3.pdf
    Input: 10
    make aquamote_core_v3.pdf  6.97s user 0.08s system 99% cpu 7.084 total

    shelleyc -u uses.yml -d aquamote_core_v3.yml --skip-checks --no-output -i aquamote_core_v3.int
    shelleyv --dfa --minimize --no-sink --format pdf aquamote_core_v3.int -o aquamote_core_v3-i-d.pdf
    Input: 57
    No sinks: 48
    DFA: 49
    Minimized DFA: 41
    NFA no sink: 23
    rm aquamote_core_v3.int
    make aquamote_core_v3-i-d.pdf  7.74s user 0.09s system 99% cpu 7.870 total

    shelleyc -u uses.yml -d aquamote_core_v3.yml --skip-checks --no-output -i aquamote_core_v3.int
    shelleyv --no-sink --format pdf aquamote_core_v3.int -o aquamote_core_v3-i-n.pdf
    Input: 57
    Remove sink states: 48
    rm aquamote_core_v3.int
    make aquamote_core_v3-i-n.pdf  7.56s user 0.10s system 87% cpu 8.732 total
