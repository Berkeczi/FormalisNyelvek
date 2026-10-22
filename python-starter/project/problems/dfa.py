from project.problems.finite_automaton import FiniteAutomaton


class DFA(FiniteAutomaton):
    @classmethod
    def from_file(cls, input_file):
        definition = cls._read_definition(input_file)
        states, alphabet, initial_state, accepting_states, transitions = definition

        for state in states:
            for symbol in alphabet:
                if len(transitions[state][symbol]) > 1:
                    raise ValueError(
                        f"Non-deterministic transition from {state!r} "
                        f"with {symbol!r}"
                    )

        return cls(*definition)

    def delta(self, state, symbol):
        return next(iter(self.transitions[state][symbol]), None)

    def accepts(self, word):
        current_state = self.initial_state

        for symbol in word:
            current_state = self.delta(current_state, symbol)
            if current_state is None:
                return False

        return current_state in self.accepting_states
