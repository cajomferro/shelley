### DIRECT

```
Invalid integration: integration error

* system: on
* integration: b1.press, led1.on, b1.press, led1.on
                                            ^^^^^^^
Instance errors:

  'led1': on, on
              ^^
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
-- specification  G ((_action = led1_on & !_eos) ->  X (((!(_action = led1_on) & !(_action = led1_off)) & !_eos) U ((_action = led1_off & !_eos) | _eos)))  is false
-- as demonstrated by the following execution sequence
Trace Description: LTL Counterexample 
Trace Type: Counterexample 
  -> State: 1.1 <-
    _eos = FALSE
    _action = b1_press
    _state = 0
  -> State: 1.2 <-
    _action = led1_on
    _state = 2
  -> State: 1.3 <-
    _action = b1_press
    _state = 3
  -> State: 1.4 <-
    _action = led1_on
    _state = 4
  -- Loop starts here
  -> State: 1.5 <-
    _eos = TRUE
    _action = b1_press
    _state = 5
  -- Loop starts here
  -> State: 1.6 <-
  -> State: 1.7 <-
-- specification  G ((_action = led1_off & !_eos) ->  X (((!(_action = led1_on) & !(_action = led1_off)) & !_eos) U ((_action = led1_on & !_eos) | _eos)))  is true
-- specification  G ((_action = b1_press & !_eos) ->  X ((!(_action = b1_press) & !_eos) U ((_action = b1_press & !_eos) | _eos)))  is true
```
