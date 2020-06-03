SHELLEYC = shelleyc
SHELLEYV = shelleyv

all: scy

pdf: valve.pdf valve_macro1.pdf valve_macro2.pdf valve_macro3.pdf # valve_macro4.pdf TOO SLOW!

scy: valve_macro1.scy valve_macro2.scy valve_macro3.scy valve_macro4.scy

valve_macro1.scy: valve_macro1.yml valve.scy

valve_macro2.scy: valve_macro2.yml valve.scy

valve_macro3.scy: valve_macro3.yml valve.scy

valve_macro4.scy: valve_macro4.yml valve.scy

# Generate integration diagram (minimized)
# Example:
#   make NAME-i-d.pdf
%-i-d.pdf: %.int
	$(SHELLEYV) --dfa --minimize --no-sink --format pdf $< -o $@


# Generate integration diagram (full)
# Example:
#   make NAME-i-n.pdf
%-i-n.pdf: %.int
	$(SHELLEYV) --no-sink --format pdf $< -o $@

# Generate system diagram
# Example:
#   make NAME.pdf
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
