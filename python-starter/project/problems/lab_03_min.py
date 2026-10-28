import argparse

from project.problem import Problem
from project.problems.dfa import DFA


class MiniProblem(Problem):

    def initialize_parser(self, parser: argparse.ArgumentParser):
        """
        Initialize the parser with the necessary arguments
        """
        parser.add_argument('--mini', action='store_true')

    def is_chosen_problem(self, args):
        """
        Check if the problem is chosen
        """
        return bool(args.mini)

    def run(self, args):
        """
        Run the program
        """
        with open(args.input, 'r') as input_file:
            dfa = DFA.from_file(input_file).minimize()

        with open(args.output, 'w') as output_file:
            output_file.write(str(dfa))
            output_file.write("\n")
