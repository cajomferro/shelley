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

