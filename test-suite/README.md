# shelley-examples

The Makefile in this folder is generated automatically. Do not change it manually.

All Makefiles inside each example are also automatically generated unless they are listed in the 
`exclude_create_makefiles.yml` file.

## Changing the validity check algorithm

### Checking validity using the automata-based algorithm
```
make examples VALIDITY_CHECKS=--skip-mc
```

### Checking validity using the specification-based algorithm (model checking)
```
make examples VALIDITY_CHECKS=--skip-direct
``` 


### Create Makefile for a specific example
```
shelley-makefile # when inside the example assumes current path

shelley-makefile aquamote_valve/

shelley-makefile-bad bad_trafficlight_gamma # for bad examples use this script instead
```

### Create Makefiles for all examples (including bad)  
```
python create_makefiles.py -x exclude_create_makefiles.yml
```

### Update the core Makefile (compiles all examples)
```
python update_makefile.py -x exclude.yml
make
```

