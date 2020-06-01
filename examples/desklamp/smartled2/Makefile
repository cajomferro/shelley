SHELLEYC = shelleyc
SHELLEYV = shelleyv

all: scy

pdf: led.pdf timer.pdf

scy: smartled.scy

smartled.scy: smartled.yml timer.scy led.scy

# Generate integration diagram (minimized)
# Example:
#   make smartled-i-d.pdf
%-i-d.pdf: %.int
	$(SHELLEYV) --dfa --minimize --no-sink --format pdf $< -o $@


# Generate integration diagram (full)
# Example:
#   make smartled-i-n.pdf
%-i-n.pdf: %.int
	$(SHELLEYV) --no-sink --format pdf $< -o $@

# Generate system diagram
# Example:
#   make smartled.pdf
%.pdf: %.scy
	$(SHELLEYV) --format pdf $< -o $@

%.int:  %.yml
	$(SHELLEYC) -d $< --no-output -i $@ -u uses.yml

%.scy: %.yml
	$(SHELLEYC) -u uses.yml -d $< -o $@

clean:
	rm -f *.scy *.pdf *.int

.PHONY: all pdf scy

.SUFFIXES: .yml .scy .int
