import argparse
import os
import sys
from contextlib import contextmanager
from pathlib import Path
from itertools import chain

import automaton
import automaton.render_nfa
import automaton.render_dfa
import regex


class App:
    def __init__(self):
        self.save_dfa_dot = automaton.render_dfa.save_tex
        self.save_dfa_reduction_dot = automaton.render_dfa.save_reduction_dot
        self.save_nfa_dot = automaton.render_nfa.save_tex
        self.save_nfa_reduction_dot = automaton.render_nfa.save_reduction_dot
        self.save_gnfa_dot = regex.save_tex
        self.save_nfa_to_regex_dot = regex.save_nfa_to_regex_dot

    def add_file(self, filename):
        pass

    def tear_down(self):
        pass

    def add_files(self, *args):
        pass


class Run:
    def __init__(self, lst, handler):
        self.lst = lst
        self.handler = handler

    def __call__(self, *args, **kwargs):
        kwargs["dry_run"] = True
        result = self.handler(*args, **kwargs)
        if isinstance(result, str):
            self.lst.append(result)
        else:
            self.lst.extend(result)


def rename_ext(iters, ext):
    for file in iters:
        yield os.path.splitext(file)[0] + ext


class DryRun:
    def __init__(self, git_ignore=False):
        self.app = App()
        self.git_ignore = git_ignore
        self.files = []
        self.skipped = []
        self.manual = []
        self.methods = set(x for x in dir(self.app) if not x.startswith("_"))
        self.skip = {
            "save_cfg_tex",
        }
        self.methods.remove("tear_down")
        for f in self.skip:
            self.methods.remove(f)
        if not git_ignore:
            # XXX: trickery not to contaminate the output, as deps requires it clean
            self.out = sys.stdout, sys.stderr
            sys.stderr = sys.stdout = open(os.devnull, "w")

    def add_file(self, filename):
        self.manual.append(filename)

    def add_files(self, *filenames, **kwargs):
        for file in filenames:
            self.add_file(file, **kwargs)

    def __getattr__(self, attr):
        if attr in self.skip:
            return Run(self.skipped, getattr(self.app, attr))
        if attr in self.methods:
            return Run(self.files, getattr(self.app, attr))

    def get_input_files(self):
        return self.files

    def get_output_files(self):
        return chain(rename_ext(self.files, ".svg"),
                     rename_ext(self.manual, ".svg"))

    def get_skipped_files(self):
        return self.skipped

    def get_all_files(self):
        return chain(self.get_input_files(), self.get_output_files(),
                     self.get_skipped_files())

    def get_ignored_files(self):
        base_dir = Path(os.getcwd())
        try:
            with open(base_dir / ".gitignore") as fp:
                for file in fp:
                    file = file.strip()
                    if file.startswith("/"):
                        yield file
        except FileNotFoundError:
            pass

    def tear_down_list(self):
        base_dir = Path(os.getcwd())
        for file in self.get_input_files():
            print(base_dir.name + "/" + file)

    def tear_down_git_ignore(self):
        base_dir = Path(os.getcwd())
        found = set(self.get_ignored_files())
        with open(base_dir / ".gitignore", "a") as out:
            for file in self.get_all_files():
                file = "/" + file
                if file not in found:
                    print(file, file=out)

    def revert_out(self):
        if not self.git_ignore:
            sys.stdout, sys.stderr = self.out

    def tear_down(self):
        self.revert_out()
        if self.git_ignore:
            self.tear_down_git_ignore()
        else:
            self.tear_down_list()


@contextmanager
def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('--deps', action='store_true')
    parser.add_argument('--git-ignore', action='store_true')
    args = parser.parse_args()
    run_app = not args.deps and not args.git_ignore
    app = App() if run_app else DryRun(args.git_ignore)
    try:
        yield app
    finally:
        app.tear_down()
