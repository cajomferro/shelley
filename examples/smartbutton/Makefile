PYTHON = PYTHONPATH=../../ python3
SHELLYC = $(PYTHON) -m appcompiler
SHELLYVIZ = $(PYTHON) -m appvizviewer

all: scy pdf

pdf: button.pdf smartbutton1.pdf smartbutton2.pdf smartbutton5.pdf

scy: smartbutton1.scy smartbutton2.scy smartbutton3.scy smartbutton4.scy smartbutton5.scy

smartbutton1.scy: smartbutton1.yaml button.scy
	$(SHELLYC) -d $< -u button.scy\:Button

smartbutton2.scy: smartbutton2.yaml button.scy timer.scy
	$(SHELLYC) -d $< -u button.scy\:Button timer.scy\:Timer

smartbutton3.scy: smartbutton3.yaml button.scy timer.scy
	# smartbutton3 expected error: missing declaration
	! $(SHELLYC) -d $< -u button.scy\:Button timer.scy\:Timer

smartbutton4.scy: smartbutton4.yaml button.scy timer.scy
	# smartbutton4 expected error: equivalent trigger rules
	! $(SHELLYC) -d $< -u button.scy\:Button timer.scy\:Timer

smartbutton5.scy: smartbutton5.yaml simple_button.scy
	# smartbutton5 expected error: https://paper.dropbox.com/doc/Formalizacao-da-especificacao-e-verificacao--Axi1jXHxQJ~TG8BNK71Pfy85Ag-ERTI2sygtyAIZVGH7HojK#:uid=584816747659115630502879&h2=Exemplo-5
	! $(SHELLYC) -d $< -u simple_button.scy\:SimpleButton

%.scy: %.yaml
	$(SHELLYC) -d $<

%.gv: %.scy
	$(SHELLYVIZ) $< -o $@

%.pdf: %.gv
	dot -Tpdf -o $@ $<

clean:
	rm -f *.scy *.pdf *.gv