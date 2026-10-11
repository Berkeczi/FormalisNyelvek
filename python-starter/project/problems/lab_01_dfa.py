from project.problem import Problem
import argparse

class SumProblem(Problem):

    def initialize_parser(self, parser: argparse.ArgumentParser):
        """
        Initialize the parser with the necessary arguments
        """
        parser.add_argument('--check', nargs='+')
    
    def is_chosen_problem(self, args):
        """
        Check if the problem is chosen
        """
        return bool(args.check)

    def run(self, args):
        """
        Run the program
        """
        # Access the input and output file paths
        input_file = args.input
        output_file = args.output

        input_file = open(input_file, 'r')
        output_file = open(output_file, 'w')

        allapotok = input_file.readline().split()
        abece = input_file.readline().split()
        kezdo = input_file.readline().strip()
        vegallapotok = input_file.readline().split()
        atmenetek = {}

        for line in input_file:
            indul, betu, eljut = line.split()
            atmenetek[indul] = atmenetek.get(indul, {})
            atmenetek[indul][betu] = eljut

        for szo in args.check:
            aktualis = kezdo
            for betu in szo:
                if aktualis not in atmenetek or betu not in atmenetek[aktualis]:
                    aktualis = None
                    break
                aktualis = atmenetek[aktualis][betu]
            if aktualis in vegallapotok:
                output_file.write("IGEN\n")
            else:
                output_file.write("NEM\n")