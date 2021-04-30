include common.mk

all: scy

png: valve.png timer.png controller.png

scy: valve.scy timer.scy controller.scy

USES = -u uses.yml

deps: valve.scy timer.scy

controller.scy: deps controller.shy

stats: controller-stats.json

clean:
	rm -f *.scy *.pdf *.gv *-stats.json *.int

.PHONY: all pdf scy deps clean
