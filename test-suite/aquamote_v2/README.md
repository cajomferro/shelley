

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
This is a mixture of their previous experiments. We use as subsystems other components directly 
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

