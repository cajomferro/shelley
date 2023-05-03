# Error explanation

For a composite system we accept empty operations' bodies but not for all of them. In that case, because the 
subsystem is never used the checker will complain about that.  

### DIRECT
```
Invalid device: Subsystem b is declared but no operation is invoked.
```

### NuSMV

WARNING: NuSMV doesn't check this!