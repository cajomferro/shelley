SHELLEYC = shelleyc
SHELLEYV = shelleyv
SHELLEYS = shelleys
SHELLEYMC = shelleymc
SHELLEYPY = shelleypy

DFA_OPTS = --dfa --minimize --nfa-no-sink --dfa-no-sink # nfa-no-sink yields faster DFA minimizatiion
#DFA_OPTS = --dfa --no-sink --dfa-no-empty-string # these are the fsm2smv exact parameters
NFA_OPTS = --nfa-no-sink
STATS_OPTS = --int-nfa # --int-dfa --int-nfa-no-sink --int-dfa-min-no-sink
USES = -u uses.yml
DEBUG =
SHELLEYPY_OPTS =
#VALIDITY_CHECKS=--skip-direct
#VALIDITY_CHECKS=--skip-mc
VALIDITY_CHECKS =

%.shy: %.py
	$(SHELLEYPY) $< $(SHELLEYPY_OPTS) -o $@

%.scy: %.shy
	$(SHELLEYMC) $(USES) -s $< $(VALIDITY_CHECKS) $(DEBUG)

# Generate integration diagram (minimized)
# Example:
#   make trafficlightctrl-i-d.pdf
%-i-d.pdf: %-i.scy
	$(SHELLEYV) $(DFA_OPTS) --format pdf $< -o $@ $(DEBUG)

# Generate integration diagram (minimized)
# Example:
#   make trafficlightctrl-i-d.png
%-i-d.png: %-i.scy
	$(SHELLEYV) $(DFA_OPTS) --format png $< -o $@ $(DEBUG)

# Generate integration diagram (full)
# Example:
#   make trafficlightctrl-i-n.pdf
%-i-n.pdf: %-i.scy
	$(SHELLEYV) $(NFA_OPTS) --format pdf $< -o $@ $(DEBUG)

# Generate integration diagram (full)
# Example:
#   make trafficlightctrl-i-n.pdf
%-i-n.png: %-i.scy
	$(SHELLEYV) $(NFA_OPTS) --format png $< -o $@ $(DEBUG)

# Generate system diagram (minimized DFA)
# Example:
#   make trafficlightctrl.pdf
%-d.pdf: %-i.scy
	$(SHELLEYV) $(DFA_OPTS) --format pdf $< -o $@ $(DEBUG)

# Generate system diagram
# Example:
#   make trafficlightctrl.pdf
%.pdf: %.scy
	$(SHELLEYV) --format pdf $< -o $@ $(DEBUG)

# Generate system diagram
# Example:
#   make trafficlightctrl.png
%.png: %.scy
	$(SHELLEYV) --format png $< -o $@ $(DEBUG)

# Generate the integration diagram
%-i.scy:  %.shy
	$(SHELLEYC) $(USES) -d $< --skip-checks --no-output -i $@ $(DEBUG)

# Generate FSM stats
%-stats.json: %.scy %-i.scy
	$(SHELLEYS) $^ -o $@ $(STATS_OPTS) $(DEBUG) # generate NFA by default when there is integration


.SUFFIXES: *.scy .pdf .png .json *.smv
