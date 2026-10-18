import argparse

from project.problem import Problem
from project.problems.nfa import NFA


class DetProblem(Problem):

    def initialize_parser(self, parser: argparse.ArgumentParser):
        """
        Initialize the parser with the necessary arguments
        """
        parser.add_argument('--det', action='store_true')
    
    def is_chosen_problem(self, args):
        """
        Check if the problem is chosen
        """
        return bool(args.det)

    def run(self, args):
        """
        Run the program
        """
        with open(args.input, 'r') as input_file:
            dfa = NFA.from_file(input_file).to_dfa()

        with open(args.output, 'w') as output_file:
            output_file.write(str(dfa))
            output_file.write("\n")