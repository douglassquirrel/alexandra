#! /usr/bin/python

from subprocess import Popen

class Member:
    def __init__(self, executable, options, cwd):
        self.executable = executable
        self.options = options
        self.cwd = cwd
        self.process = None

    def start(self):
        self.process = Popen([self.executable] + self.options, cwd=self.cwd)

    def stop(self):
        self.process.kill()

class Herd:
    def __init__(self):
        self._members = []

    def add(self, executable, options, cwd):
        self._members.append(Member(executable, options, cwd))

    def start(self):
        map(lambda m: m.start(), self._members)

    def stop(self):
        map(lambda m: m.stop(), self._members)
