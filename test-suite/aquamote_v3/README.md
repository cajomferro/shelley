## AquamoteCore using controller_radioclient_v2 instead of separate components
### Main files:
- aquamote_core_v2.yml
### Deps:
 - ../aquamote_controller/controller_radioclient_v2.scy

### Goal
This example overcomes some of the limitations of aquamote_controller_v1 (see limitations before) by adding more Shelley operations.
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
