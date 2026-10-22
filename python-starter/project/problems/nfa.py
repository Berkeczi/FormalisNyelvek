from collections import deque

from project.problems.dfa import DFA
from project.problems.finite_automaton import FiniteAutomaton


class NFA(FiniteAutomaton):
    def delta(self, states, symbol):
        destinations = set()
        for state in states:
            destinations.update(self.transitions[state][symbol])
        return destinations

    def accepts(self, word):
        current_states = {self.initial_state}

        for symbol in word:
            current_states = self.delta(current_states, symbol)
            if not current_states:
                return False

        return bool(current_states & self.accepting_states)

    def to_dfa(self):
        initial_subset = frozenset({self.initial_state})
        subset_names = {initial_subset: "s0"}
        states = {"s0"}
        accepting_states = set()
        transitions = self._new_transitions()
        pending_states = deque([initial_subset])

        while pending_states:
            current_subset = pending_states.popleft()
            current_state = subset_names[current_subset]

            if current_subset & self.accepting_states:
                accepting_states.add(current_state)

            for symbol in self.alphabet:
                next_subset = frozenset(
                    self.delta(current_subset, symbol)
                )

                if not next_subset:
                    continue

                if next_subset not in subset_names:
                    next_state = f"s{len(subset_names)}"
                    subset_names[next_subset] = next_state
                    states.add(next_state)
                    pending_states.append(next_subset)

                transitions[current_state][symbol] = subset_names[next_subset]

        return DFA(
            states,
            self.alphabet,
            "s0",
            accepting_states,
            transitions,
        )
