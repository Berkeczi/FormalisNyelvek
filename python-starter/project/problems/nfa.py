from collections import deque
from types import MappingProxyType

from project.problems.dfa import DFA
from project.problems.finite_automaton import (
    FiniteAutomaton,
    State,
    StateTransitions,
    Symbol,
    Transitions,
)

class _NFAStateTransitions(StateTransitions[set[State]]):
    def __init__(
        self,
        transitions: dict[tuple[State, Symbol], set[State]]
        | MappingProxyType,
        state: State,
    ) -> None:
        self._transitions = transitions
        self._state = state

    def __setitem__(self, symbol: Symbol, destination: State) -> None:
        if not isinstance(self._transitions, dict):
            raise TypeError("Transitions are immutable")
        destinations = self._transitions.setdefault(
            (self._state, symbol),
            set(),
        )
        destinations.add(destination)

    def __getitem__(self, symbol: Symbol) -> set[State] | frozenset[State]:
        return self._transitions.get((self._state, symbol), set())


class _NFATransitions(Transitions[set[State]]):
    def __init__(self) -> None:
        self._values: dict[tuple[State, Symbol], set[State]] | MappingProxyType = {}

    def __getitem__(
        self,
        state: State,
    ) -> StateTransitions[set[State]]:
        return _NFAStateTransitions(self._values, state)

    def items(self):
        return self._values.items()

    def destinations(self, value: set[State]) -> frozenset[State]:
        return frozenset(value)

    def freeze(self) -> None:
        if isinstance(self._values, dict):
            self._values = MappingProxyType(
                {
                    key: frozenset(destinations)
                    for key, destinations in self._values.items()
                }
            )


class NFA(FiniteAutomaton[set[State]]):
    @classmethod
    def _new_transitions(cls) -> _NFATransitions:
        return _NFATransitions()

    def accepts(self, word: str) -> bool:
        current_states = {self.initial_state}

        for symbol in word:
            next_states = set()
            for state in current_states:
                next_states.update(self.transitions[state][symbol])
            current_states = next_states
            if not current_states:
                return False

        return bool(current_states & self.accepting_states)

    def to_dfa(self) -> DFA:
        initial_subset = frozenset({self.initial_state})
        subset_names: dict[frozenset[State], State] = {
            initial_subset: "s0"
        }
        states: set[State] = {"s0"}
        accepting_states: set[State] = set()
        transitions = DFA._new_transitions()
        pending_states: deque[frozenset[State]] = deque([initial_subset])

        while pending_states:
            current_subset = pending_states.popleft()
            current_state_name = subset_names[current_subset]

            if current_subset & self.accepting_states:
                accepting_states.add(current_state_name)

            for symbol in self.alphabet:
                next_subset = frozenset(
                    destination
                    for state in current_subset
                    for destination in self.transitions[state][symbol]
                )

                if not next_subset:
                    continue

                if next_subset not in subset_names:
                    next_state_name = f"s{len(subset_names)}"
                    subset_names[next_subset] = next_state_name
                    states.add(next_state_name)
                    pending_states.append(next_subset)

                transitions[current_state_name][symbol] = (
                    subset_names[next_subset]
                )

        return DFA(
            states,
            self.alphabet,
            "s0",
            accepting_states,
            transitions,
        )
