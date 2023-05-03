This is an attempt to model the gamma example in a richer way by adding explicit control of timers (begin, end, timeout).
Currently, "Controller" has errors because if "Timer" is restrict (less transitions on behavior) then "Controller"
cannot have "xor" to allow option between events of different timers.

This is an example of this "problem":

    - operating_priority_prepares:
        start: False
        final: False
        integration:
          seq:
            - xor:
              - seq: [InitTimeout5.timeout, PriorityControl.toggle]
              - seq: [PriorityTimeout4.timeout, PriorityControl.toggle]
            - PriorityPreparesTimeout6.begin

We can go to "operating_priority_prepares" from "operating_priority" or "operating_init". If comming from operating_init,
we will have a possible path with "PriorityTimeout4.timeout" without having "PriorityTimeout4.begin".
The solution to this is either change "Timer" to be less restrict or having different events on "Controller" macro
instead of xor.