all: update examples

include examples.mk

examples: good bad

update: update_examples_makefiles update_examples_list

update_examples_makefiles:
	python create_makefiles.py -x exclude_create_makefiles.yml

update_examples_list:
	python update_makefile.py -x exclude.yml
