include ../common.mk

all: scy

pdf: button.pdf \
	led.pdf \
	led_strict.pdf \
	pressed_button.pdf \
	simple_button.pdf \
	timer.pdf

scy: button.scy \
	led.scy \
	led_strict.scy \
	pressed_button.scy \
	simple_button.scy \
	timer.scy

USES = -u uses.yml

clean:
	rm -f *.scy *.pdf *.gv

.PHONY: all pdf scy
