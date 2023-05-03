### DIRECT

```
Invalid device: integration error

* system: on, on
* integration: b.press, b.press
                        ^^^^^^^
Instance errors:

  'b': press, press
              ^^^^^
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

-- specification  F _eos  is true
-- specification  G (_eos -> ( G _eos &  X _eos))  is true
-- specification  G ((_action = b_press & !_eos) ->  X (((!(_action = b_press) & !(_action = b_release)) & !_eos) U ((_action = b_release & !_eos) | _eos)))  is false
-- as demonstrated by the following execution sequence
Trace Description: LTL Counterexample 
Trace Type: Counterexample 
  -> State: 1.1 <-
    _eos = FALSE
    _action = b_press
    _state = 0
  -> State: 1.2 <-
    _state = 2
  -- Loop starts here
  -> State: 1.3 <-
    _eos = TRUE
    _state = 3
  -- Loop starts here
  -> State: 1.4 <-
  -> State: 1.5 <-
-- specification  G ((_action = b_release & !_eos) ->  X (((!(_action = b_press) & !(_action = b_release)) & !_eos) U ((_action = b_press & !_eos) | _eos)))  is true
```
