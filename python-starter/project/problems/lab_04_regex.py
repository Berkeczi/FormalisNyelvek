from collections import Counter
from project.problem import Problem
import argparse
import re

class RegexProblem(Problem):

    def initialize_parser(self, parser: argparse.ArgumentParser):
        """
        Initialize the parser with the necessary arguments
        """
        parser.add_argument('--rgx', type=int, choices=range(1, 6))    

    def is_chosen_problem(self, args):
        """
        Check if the problem is chosen
        """
        return bool(args.rgx)

    def run(self, args):
        """
        Run the program
        """
        with open(args.input, 'r') as input_file:
            input_data = input_file.read()
            
        result = {
            1: self.problem1,
            2: self.problem2,
            3: self.problem3,
            4: self.problem4,
            5: self.problem5,
        }[args.rgx](input_data)
        
        with open(args.output, 'w') as output_file:
            output_file.write(result)
            

    # based on given (([0-9-]+ [0-9:.]+) +([0-9]+) +([0-9]+) ([IDVEFAW]) (.+?):(?: (.+))?)
    base_pattern = (
        r"(?P<entry>"
            r"(?P<timestamp>[0-9-]+ [0-9:.]+) +"
            r"(?P<pid>[0-9]+) +"
            r"(?P<tid>[0-9]+) "
            r"(?P<level>[IDVEFAW]) "
            r"(?P<tag>.+?):(?: (?P<message>.+))?"
        r")"
    )

    def problem1(self, input):
        patterns = [
            r"^10-15 ",
            r"^10-15 10:18:51",
            r"^.*:..:51",
            r"^.*lowmemorykiller:",
            r"^.*10:18:51.{7}221",
            r" E ",
            r"W PackageManager:",
            r"D .*ExoPlayer.*:",
            r" [EW] .*\.java:",
            r"^[^:]*:[^:]*:[^:]*:.*Thread"
        ]

        return "\n".join(
            str(sum(1 for _ in re.finditer(pattern, input, re.MULTILINE)))
            for pattern in patterns
        )

    def problem2(self, input):
        error_pattern = (
            r"(?P<entry>"
                r"(?P<timestamp>[0-9-]+ [0-9:.]+) +"
                r"(?P<pid>[0-9]+) +"
                r"(?P<tid>[0-9]+) "
                r"(?P<level>E) "
                r"(?P<tag>.+?): "
                r"(?P<message>.*?at +"
                    r"(?P<call>.+?)\("
                    r"(?P<file>.+?\.java):"
                    r"(?P<line>[0-9]+)\)"
                r")"
            r")"
        )

        files = [
            match.group("file")
            for match in re.finditer(error_pattern, input)
        ]
        return "\n".join(files)

    def problem3(self, input):
        pids = dict.fromkeys(
            match.group("pid")
            for match in re.finditer(self.base_pattern, input)
        )
        return "\n".join(pids)

    def problem4(self, input):
        error_counts = Counter(
            match.group("pid")
            for match in re.finditer(self.base_pattern, input)
            if match.group("level") == "E"
        )

        pid, count = error_counts.most_common(1)[0]
        return f"PID={pid} ({count} errors)"

    def problem5(self, input):
        main_thread_error_pattern = (
            r"(?P<entry>"
                r"(?P<timestamp>[0-9-]+ [0-9:.]+) +"
                r"(?P<pid>[0-9]+) +"
                r"(?P<tid>(?P=pid)) "
                r"E "
                r"(?P<tag>.+?):(?: (?P<message>.+))?"
            r")"
        )

        return str(sum(
            1
            for _ in re.finditer(main_thread_error_pattern, input)
        ))
