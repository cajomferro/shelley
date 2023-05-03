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

smv: button.smv \
	led.smv \
	led_strict.smv \
	pressed_button.smv \
	simple_button.smv \
	timer.smv

base-stats.json: button-stats.json led-stats.json led_strict-stats.json pressed_button-stats.json simple_button-stats.json timer-stats.json

USES = -u uses.yml

clean:
	rm -f *.scy *.smv *.pdf *.png *.int *.gv

.PHONY: all pdf scy
