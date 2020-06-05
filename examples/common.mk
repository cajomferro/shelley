SHELLEYC = shelleyc
SHELLEYV = shelleyv

%.scy: %.yml
	$(SHELLEYC) -u uses.yml -d $< -o $@

# Generate integration diagram (minimized)
# Example:
#   make trafficlightctrl-i-d.pdf
%-i-d.pdf: %.int
	$(SHELLEYV) --dfa --minimize --format pdf $< -o $@

# Generate integration diagram (minimized)
# Example:
#   make trafficlightctrl-i-d.png
%-i-d.png: %.int
	$(SHELLEYV) --dfa --minimize --format png $< -o $@

# Generate integration diagram (full)
# Example:
#   make trafficlightctrl-i-n.pdf
%-i-n.pdf: %.int
	$(SHELLEYV) --no-sink --format pdf $< -o $@

# Generate integration diagram (full)
# Example:
#   make trafficlightctrl-i-n.pdf
%-i-n.png: %.int
	$(SHELLEYV) --no-sink --format png $< -o $@

# Generate system diagram
# Example:
#   make trafficlightctrl.pdf
%.pdf: %.scy
	$(SHELLEYV) --format pdf $< -o $@

# Generate the integration diagram
%.int:  %.yml
	$(SHELLEYC) -d $< --no-output -i $@ -u uses.yml

.SUFFIXES: .yml .scy .int .pdf .png
