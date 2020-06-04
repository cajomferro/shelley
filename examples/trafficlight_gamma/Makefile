SHELLEYC = shelleyc
SHELLEYV = shelleyv

all: scy

pdf: control.pdf timer.pdf policeinterrupt.pdf lightcommands.pdf trafficlightctrl.pdf

scy: trafficlightctrl.scy

trafficlightctrl.scy: trafficlightctrl.yml timer.scy control.scy policeinterrupt.scy lightcommands.scy

%.scy: %.yml
	$(SHELLEYC) -u uses.yml -d $< -o $@


# Generate integration diagram (minimized)
# Example:
#   make trafficlightctrl-i-d.pdf
%-i-d.pdf: %.int
	$(SHELLEYV) --dfa --minimize --no-sink --format pdf $< -o $@


# Generate integration diagram (full)
# Example:
#   make trafficlightctrl-i-n.pdf
%-i-n.pdf: %.int
	$(SHELLEYV) --no-sink --format pdf $< -o $@

# Generate system diagram
# Example:
#   make trafficlightctrl.pdf
%.pdf: %.scy
	$(SHELLEYV) --format pdf $< -o $@

%.int:  %.yml
	$(SHELLEYC) -d $< --no-output -i $@ -u uses.yml

clean:
	rm -f *.scy *.pdf *.int

.PHONY: all pdf scy

.SUFFIXES: .yml .scy .int
