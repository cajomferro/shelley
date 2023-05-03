## AquamoteCore original

### Main files:
- aquamote_core_original.yml
 
### Goal
State machine from the aquamote core as described in the Case Study of the Frankestein paper.

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

