SHELLEYC = shelleyc
SHELLEYV = shelleyv

DFA_OPTS = --dfa --minimize --no-sink
NFA_OPTS = --no-sink

%.scy: %.yml
	$(SHELLEYC) -u uses.yml -d $< -o $@

# Generate integration diagram (minimized)
# Example:
#   make trafficlightctrl-i-d.pdf
%-i-d.pdf: %.int
	$(SHELLEYV) $(DFA_OPTS) --format pdf $< -o $@

# Generate integration diagram (minimized)
# Example:
#   make trafficlightctrl-i-d.png
%-i-d.png: %.int
	$(SHELLEYV) $(DFA_OPTS) --format png $< -o $@

# Generate integration diagram (full)
# Example:
#   make trafficlightctrl-i-n.pdf
%-i-n.pdf: %.int
	$(SHELLEYV) $(NFA_OPTS) --format pdf $< -o $@

# Generate integration diagram (full)
# Example:
#   make trafficlightctrl-i-n.pdf
%-i-n.png: %.int
	$(SHELLEYV) $(NFA_OPTS) --format png $< -o $@

# Generate system diagram
# Example:
#   make trafficlightctrl.pdf
%.pdf: %.scy
	$(SHELLEYV) --format pdf $< -o $@

# Generate system diagram
# Example:
#   make trafficlightctrl.png
%.png: %.scy
	$(SHELLEYV) --format png $< -o $@

# Generate the integration diagram
%.int:  %.yml
	$(SHELLEYC) -d $< --skip-checks --no-output -i $@ -u uses.yml

.SUFFIXES: .yml .scy .int .pdf .png
