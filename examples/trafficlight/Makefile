SHELLEYC = shelleyc
SHELLEYV = shelleyv

all: scy

pdf: led.pdf timer.pdf trafficlight.pdf

scy: trafficlight.scy

trafficlight.scy: trafficlight.yml timer.scy led.scy

%.scy: %.yml
	$(SHELLEYC) -u uses.yml -d $< -o $@


# Generate integration diagram (minimized)
# Example:
#   make trafficlight-i-d.pdf
%-i-d.pdf: %.int
	$(SHELLEYV) --dfa --minimize --no-sink --format pdf $< -o $@


# Generate integration diagram (full)
# Example:
#   make trafficlight-i-n.pdf
%-i-n.pdf: %.int
	$(SHELLEYV) --no-sink --format pdf $< -o $@

# Generate system diagram
# Example:
#   make trafficlight.pdf
%.pdf: %.scy
	$(SHELLEYV) --format pdf $< -o $@

%.int:  %.yml
	$(SHELLEYC) -d $< --no-output -i $@ -u uses.yml

clean:
	rm -f *.scy *.pdf *.int

.PHONY: all pdf scy

.SUFFIXES: .yml .scy .int
