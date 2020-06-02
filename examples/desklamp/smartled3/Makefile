SHELLEYC = shelleyc
SHELLEYV = shelleyv

all: scy

pdf: led.pdf timer.pdf

scy: smartled.scy

smartled.scy: smartled.yml timer.scy led.scy

# Generate integration diagram (minimized)
# Example:
#   make smartled-i-d.pdf
%-i-d.png: %.int
	$(SHELLEYV) --dfa --minimize --no-sink --format png $< -o $@

# Generate integration diagram (full)
# Example:
#   make smartled-i-n.pdf
%-i-n.png: %.int
	$(SHELLEYV) --no-sink --format png $< -o $@

# Generate system diagram
# Example:
#   make smartled.pdf
%.png: %.scy
	$(SHELLEYV) --format png $< -o $@

%.int:  %.yml
	$(SHELLEYC) -d $< --no-output -i $@ -u uses.yml

%.scy: %.yml
	$(SHELLEYC) -u uses.yml -d $< -o $@

clean:
	rm -f *.scy *.pdf *.png *.int

.PHONY: all pdf scy

.SUFFIXES: .yml .scy .int
