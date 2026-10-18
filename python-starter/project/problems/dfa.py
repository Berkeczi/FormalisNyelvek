from project.problems.finite_automaton import FiniteAutomaton


class DFA(FiniteAutomaton):
    @classmethod
    def from_file(cls, input_file):
        from project.problems.nfa import NFA

        nfa = NFA.from_file(input_file)
        for state in nfa.states:
            for symbol in nfa.alphabet:
                if len(nfa.transitions[state][symbol]) > 1:
                    raise ValueError(
                        f"Non-deterministic transition from {state!r} "
                        f"with {symbol!r}"
                    )

        return cls(
            nfa.states,
            nfa.alphabet,
            nfa.initial_state,
            nfa.accepting_states,
            nfa.transitions,
        )

    def delta(self, state, symbol):
        return next(iter(self.transitions[state][symbol]), None)

    def accepts(self, word):
        current_state = self.initial_state

        for symbol in word:
            current_state = self.delta(current_state, symbol)
            if current_state is None:
                return False

        return current_state in self.accepting_states
