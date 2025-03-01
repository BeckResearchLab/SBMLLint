"""Wraps methods that use Tellurium runs them in another process."""

import argparse
import subprocess
import sys

NUM_S1 = 2
NUM_S2 = 3
IGNORE_TEST = False
ANTIMONY_STG = '''
%dS1 -> %dS2; 1
S1 = 0
S2 = 0
''' % (NUM_S1, NUM_S2)

class TelluriumSandbox(object):
  """
  Runs python code in a separate process (sandbox).
  Note that there are two instances of this class that are
  created; one in the parent process (which uses the main and run
  methods) and one in the child (which uses the execute method).
  Usage:
    sandbox.run(method_name, string_argument)
  Outputs
    sandbox.return_code - should be 0
    sandbox.output - string result
  """

  def __init__(self):
    self.return_code = None
    self.output = None

  def echo(self, input_string):
    """
    Executes the sandboxed python codes in the child process.
    :param str input_string:
    :return str:
    Notes:
      1. Writes double newlines ("\n")
    """
    sys.stdout.writelines(input_string)

  @staticmethod
  def _convert(input_string):
    """
    Converts from io_wrapper to string
    """
    return ''.join([l for l in input_string])

  def getSBMLFromAntimony(self, input_string):
    """
    This method runs in a different process from the caller
    and so can import tellurium.
    """
    import tellurium as te
    # Convert input to string.
    inputs = self.__class__._convert(input_string)
    # Try different ways to load the model
    try:
      rr = te.loada(inputs)
    except:
      rr = te.loadSBMLModel(inputs)
    sbml = rr.getSBML()
    sys.stdout.writelines(sbml)

  def run(self, method, input_string):
    """
    Runs the child process from the parent process.
    Strips double newlines.
    """
    process = subprocess.run(['python', __file__, method],
        stdout=subprocess.PIPE,
        input=input_string, encoding='ascii')
    self.return_code = process.returncode
    self.output = process.stdout

  def main(self):
    """
    The first argument is the method to call.
    """
    cmd = "self.%s(sys.stdin)" % sys.argv[1]
    exec(cmd)


if __name__ == '__main__':
  sandbox = TelluriumSandbox()
  sandbox.main()
