This is an attempt to model the gamma example without changing (too much) the example's original philosophy.
I am merging "crossroad" and "controller" as a single entity because in the original example, crossroad is just
a connector, it doesn't have any behavior. By modelling this example using Shelley, the controller "kind of incorporates"
the two trafficlights and thus the controller is also the crossroad.

I had to differentiate bettwen police "on" and "off". Otherwise it would be more difficult to model the example without
having ambiguity.