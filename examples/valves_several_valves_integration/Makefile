include ../common.mk

all: scy

pdf: valve.pdf 4valves.pdf 8valves.pdf 2x4valves.pdf 3x4valves.pdf 8x4valves.pdf 4x2x4valves.pdf 12valves.pdf 13valves.pdf 16valves.pdf # 24valves.pdf 32valves.pdf

scy: 4valves.scy 8valves.scy 2x4valves.scy 3x4valves.scy 8x4valves.scy 4x2x4valves.scy 12valves.scy 13valves.scy 16valves.scy # 24valves.scy 32valves.scy

USES = -u uses.yml

valve.scy: valve.yml

2x4valves.scy: 2x4valves.yml 4valves.scy

3x4valves.scy: 3x4valves.yml 4valves.scy

8x4valves.scy: 8x4valves.yml 4valves.scy

4x2x4valves.scy: 4x2x4valves.yml 2x4valves.scy

clean:
	rm -f *.scy *.pdf *.gv


.SUFFIXES: .yml .scy
