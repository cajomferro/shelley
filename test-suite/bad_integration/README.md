### DIRECT
```
Invalid device: integration error

* system: level1
* integration: b.release, b.press, ledA.on, t.start
               ^^^^^^^^^                    ^^^^^^^
Instance errors:

  'b': release, press
       ^^^^^^^       
  't': start
       ^^^^^
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
-- specification  G ((_action = ledA_on & !_eos) ->  X (((!(_action = ledA_on) & !(_action = ledA_off)) & !_eos) U ((_action = ledA_off & !_eos) | _eos)))  is true
-- specification  G ((_action = ledA_off & !_eos) ->  X (((!(_action = ledA_on) & !(_action = ledA_off)) & !_eos) U ((_action = ledA_on & !_eos) | _eos)))  is true
-- specification  G ((_action = ledB_on & !_eos) ->  X (((!(_action = ledB_on) & !(_action = ledB_off)) & !_eos) U ((_action = ledB_off & !_eos) | _eos)))  is true
-- specification  G ((_action = ledB_off & !_eos) ->  X (((!(_action = ledB_on) & !(_action = ledB_off)) & !_eos) U ((_action = ledB_on & !_eos) | _eos)))  is true
-- specification  G ((_action = b_press & !_eos) ->  X (((!(_action = b_press) & !(_action = b_release)) & !_eos) U ((_action = b_release & !_eos) | _eos)))  is false
-- as demonstrated by the following execution sequence
Trace Description: LTL Counterexample 
Trace Type: Counterexample 
  -> State: 1.1 <-
    _eos = FALSE
    _action = b_release
    _state = 0
  -> State: 1.2 <-
    _action = b_press
    _state = 2
  -> State: 1.3 <-
    _action = ledA_on
    _state = 3
  -> State: 1.4 <-
    _action = t_start
    _state = 4
  -> State: 1.5 <-
    _action = b_press
    _state = 5
  -> State: 1.6 <-
    _action = b_release
    _state = 7
  -> State: 1.7 <-
    _action = ledB_on
    _state = 53
  -> State: 1.8 <-
    _action = t_cancel
    _state = 55
  -> State: 1.9 <-
    _action = t_start
    _state = 56
  -- Loop starts here
  -> State: 1.10 <-
    _eos = TRUE
    _action = b_press
    _state = 57
  -- Loop starts here
  -> State: 1.11 <-
  -> State: 1.12 <-
-- specification  G ((_action = b_release & !_eos) ->  X (((!(_action = b_press) & !(_action = b_release)) & !_eos) U ((_action = b_press & !_eos) | _eos)))  is false
-- as demonstrated by the following execution sequence
Trace Description: LTL Counterexample 
Trace Type: Counterexample 
  -> State: 2.1 <-
    _eos = FALSE
    _action = b_release
    _state = 0
  -> State: 2.2 <-
    _action = b_press
    _state = 2
  -> State: 2.3 <-
    _action = ledA_on
    _state = 3
  -> State: 2.4 <-
    _action = t_start
    _state = 4
  -> State: 2.5 <-
    _action = b_press
    _state = 5
  -> State: 2.6 <-
    _action = b_release
    _state = 7
  -> State: 2.7 <-
    _action = ledB_on
    _state = 53
  -> State: 2.8 <-
    _action = t_cancel
    _state = 55
  -> State: 2.9 <-
    _action = t_start
    _state = 56
  -> State: 2.10 <-
    _action = t_timeout
    _state = 57
  -> State: 2.11 <-
    _action = ledB_off
    _state = 24
  -> State: 2.12 <-
    _action = ledA_off
    _state = 26
  -> State: 2.13 <-
    _action = b_release
    _state = 27
  -> State: 2.14 <-
    _action = b_press
    _state = 28
  -> State: 2.15 <-
    _action = ledA_on
    _state = 29
  -> State: 2.16 <-
    _action = t_start
    _state = 30
  -- Loop starts here
  -> State: 2.17 <-
    _eos = TRUE
    _action = b_press
    _state = 31
  -- Loop starts here
  -> State: 2.18 <-
  -> State: 2.19 <-
-- specification  G ((_action = t_start & !_eos) ->  X ((((!(_action = t_start) & !(_action = t_cancel)) & !(_action = t_timeout)) & !_eos) U ((_action = t_cancel & !_eos) | (_action = t_timeout & !_eos))))  is false
-- as demonstrated by the following execution sequence
Trace Description: LTL Counterexample 
Trace Type: Counterexample 
  -> State: 3.1 <-
    _eos = FALSE
    _action = b_release
    _state = 0
  -> State: 3.2 <-
    _action = b_press
    _state = 2
  -> State: 3.3 <-
    _action = ledA_on
    _state = 3
  -> State: 3.4 <-
    _action = t_start
    _state = 4
  -- Loop starts here
  -> State: 3.5 <-
    _eos = TRUE
    _action = b_press
    _state = 5
  -- Loop starts here
  -> State: 3.6 <-
  -> State: 3.7 <-
-- specification  G ((_action = t_cancel & !_eos) ->  X ((((!(_action = t_start) & !(_action = t_cancel)) & !(_action = t_timeout)) & !_eos) U ((_action = t_start & !_eos) | _eos)))  is true
-- specification  G ((_action = t_timeout & !_eos) ->  X ((((!(_action = t_start) & !(_action = t_cancel)) & !(_action = t_timeout)) & !_eos) U ((_action = t_start & !_eos) | _eos)))  is true
```