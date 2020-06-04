SHELLEYC = shelleyc
SHELLEYV = shelleyv

all: scy

pdf: led.pdf timer.pdf desklamp.pdf

scy: desklamp.scy

desklamp.scy: desklamp.yml timer.scy led.scy

%.scy: %.yml
	$(SHELLEYC) -u uses.yml -d $< -o $@


# Generate integration diagram (minimized)
# Example:
#   make desklamp-i-d.pdf
%-i-d.pdf: %.int
	$(SHELLEYV) --dfa --minimize --no-sink --format pdf $< -o $@


# Generate integration diagram (full)
# Example:
#   make desklamp-i-n.pdf
%-i-n.pdf: %.int
	$(SHELLEYV) --no-sink --format pdf $< -o $@

# Generate system diagram
# Example:
#   make desklamp.pdf
%.pdf: %.scy
	$(SHELLEYV) --format pdf $< -o $@

%.int:  %.yml
	$(SHELLEYC) -d $< --no-output -i $@ -u uses.yml

clean:
	rm -f *.scy *.pdf *.int

.PHONY: all pdf scy

.SUFFIXES: .yml .scy .int
