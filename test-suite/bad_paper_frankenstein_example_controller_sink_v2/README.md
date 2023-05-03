# README

This error is caught by the Direct and NuSMV checks. For a similar error detected by the parser see `bad_paper_frankenstein_example_controller_sink`.

### DIRECT

```
Invalid device: Unusable operation error
These operations do not reach a yield point: level4
```

### NUSMV

```
*** This is NuSMV 2.6.0 (compiled on Thu Mar  4 12:49:32 2021)
*** Enabled addons are: compass
*** For more information on NuSMV see <http://nusmv.fbk.eu>
*** or email to <nusmv-users@list.fbk.eu>.
*** Please report bugs to <Please report bugs to <nusmv-users@fbk.eu>>

*** Copyright (c) 2010-2014, Fondazione Bruno Kessler

*** This version of NuSMV is linked to the CUDD library version 2.4.1
*** Copyright (c) 1995-2004, Regents of the University of Colorado

*** This version of NuSMV is linked to the MiniSat SAT solver. 
*** See http://minisat.se/MiniSat.html
*** Copyright (c) 2003-2006, Niklas Een, Niklas Sorensson
*** Copyright (c) 2007-2010, Niklas Sorensson

-- specification EF ((_action = level1 & !_eos) & EF _eos)  is true
-- specification EF ((_action = level2 & !_eos) & EF _eos)  is true
-- specification EF ((_action = level4 & !_eos) & EF _eos)  is false
-- as demonstrated by the following execution sequence
Trace Description: CTL Counterexample 
Trace Type: Counterexample 
  -> State: 1.1 <-
    _eos = FALSE
    _action = _ainit
    _state = -1
-- specification EF ((_action = standby1 & !_eos) & EF _eos)  is true
-- specification EF ((_action = standby2 & !_eos) & EF _eos)  is true
-- specification  F _eos  is true
-- specification  G (_eos -> ( G _eos &  X _eos))  is true
```
