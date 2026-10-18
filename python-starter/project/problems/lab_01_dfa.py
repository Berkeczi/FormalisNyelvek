import argparse

from project.problem import Problem
from project.problems.dfa import DFA

class DFAProblem(Problem):

    def initialize_parser(self, parser: argparse.ArgumentParser):
        """
        Initialize the parser with the necessary arguments
        """
        parser.add_argument('--check')
    
    def is_chosen_problem(self, args):
        """
        Check if the problem is chosen
        """
        return bool(args.check)

    def run(self, args):
        """
        Run the program
        """
        with open(args.input, 'r') as input_file:
            dfa = DFA.from_file(input_file)

        with open(args.output, 'w') as output_file:
            for szo in args.check.split(','):
                if dfa.accepts(szo):
                    output_file.write("IGEN\n")
                else:
                    output_file.write("NEM\n")