from .context import shelley

from appcompiler import create_parser


def test_single_device():
    src = 'examples/button.yaml'
    parser = create_parser()
    args = parser.parse_args([src])
    assert args.name is None
    assert args.outdir is None
    assert args.src == src
    assert args.uses == None

def test_single_device_binary():
    src = 'examples/button.yaml'
    parser = create_parser()
    args = parser.parse_args(['-b', src])
    assert args.name is None
    assert args.outdir is None
    assert args.src == src
    assert args.uses == None
    assert args.binary is True

def test_single_device_user_defined_name():
    src = 'examples/button.yaml'
    name = 'Button'
    parser = create_parser()
    args = parser.parse_args([src, '--name', name])
    assert args.name == name
    assert args.outdir is None
    assert args.src == src
    assert args.uses == None


def test_single_device_user_defined_outdir():
    src = 'examples/button.yaml'
    name = 'Button'
    outdir = 'compiled/'
    parser = create_parser()
    args = parser.parse_args([src, '--name', name, '--outdir', outdir])
    assert args.name == name
    assert args.outdir[0] == outdir
    assert len(args.outdir) == 1
    assert args.src == src
    assert args.uses == None


def test_composite_device():
    src = 'examples/desklamp.yaml'
    name = 'Desklamp'
    outdir = 'compiled/'
    uses_button = 'examples/desklamp.yaml Button'
    uses_led = 'examples/desklamp.yaml Led'
    uses_timer = 'examples/desklamp.yaml Timer'
    parser = create_parser()
    args = parser.parse_args(
        ['--outdir', outdir, '--uses', uses_button, '--uses', uses_led, '--uses', uses_timer, src, '--name', name])
    print(args)
    assert args.name == name
    assert args.outdir[0] == outdir
    assert len(args.outdir) == 1
    assert args.src == src
    assert len(args.uses) == 3
    assert args.uses[0][0] == uses_button
    assert args.uses[1][0] == uses_led
    assert args.uses[2][0] == uses_timer
