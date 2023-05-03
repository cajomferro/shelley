### DIRECT
```
Invalid device: integration error

* system: write, fetch
* integration: b.write_0, b.read_1
                          ^^^^^^^^
Instance errors:

  'b': write_0, read_1
                ^^^^^^
```

### NuSMV

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

-- specification  F _eos  is true
-- specification  G (_eos -> ( G _eos &  X _eos))  is true
-- specification  G ((_action = b_write_0 & !_eos) ->  X (((((!(_action = b_write_0) & !(_action = b_write_1)) & !(_action = b_read_0)) & !(_action = b_read_1)) & !_eos) U (_action = b_read_0 & !_eos)))  is false
-- as demonstrated by the following execution sequence
Trace Description: LTL Counterexample 
Trace Type: Counterexample 
  -> State: 1.1 <-
    _eos = FALSE
    _action = b_write_0
    _state = 0
  -> State: 1.2 <-
    _action = b_read_1
    _state = 3
  -> State: 1.3 <-
    _action = b_write_0
    _state = 5
  -> State: 1.4 <-
    _action = b_read_1
    _state = 8
  -- Loop starts here
  -> State: 1.5 <-
    _eos = TRUE
    _action = b_read_0
    _state = 9
  -- Loop starts here
  -> State: 1.6 <-
  -> State: 1.7 <-
-- specification  G ((_action = b_write_1 & !_eos) ->  X (((((!(_action = b_write_0) & !(_action = b_write_1)) & !(_action = b_read_0)) & !(_action = b_read_1)) & !_eos) U (_action = b_read_1 & !_eos)))  is false
-- as demonstrated by the following execution sequence
Trace Description: LTL Counterexample 
Trace Type: Counterexample 
  -> State: 2.1 <-
    _eos = FALSE
    _action = b_write_0
    _state = 0
  -> State: 2.2 <-
    _action = b_read_0
    _state = 3
  -> State: 2.3 <-
    _action = b_write_1
    _state = 6
  -> State: 2.4 <-
    _action = b_read_0
    _state = 7
  -- Loop starts here
  -> State: 2.5 <-
    _eos = TRUE
    _state = 10
  -- Loop starts here
  -> State: 2.6 <-
  -> State: 2.7 <-
-- specification  G ((_action = b_read_0 & !_eos) ->  X (((((!(_action = b_write_0) & !(_action = b_write_1)) & !(_action = b_read_0)) & !(_action = b_read_1)) & !_eos) U (((_action = b_write_0 & !_eos) | (_action = b_write_1 & !_eos)) | _eos)))  is true
-- specification  G ((_action = b_read_1 & !_eos) ->  X (((((!(_action = b_write_0) & !(_action = b_write_1)) & !(_action = b_read_0)) & !(_action = b_read_1)) & !_eos) U (((_action = b_write_0 & !_eos) | (_action = b_write_1 & !_eos)) | _eos)))  is true
```