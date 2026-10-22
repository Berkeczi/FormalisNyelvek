from collections import deque
from collections.abc import Mapping, Set
from types import MappingProxyType

from project.problems.dfa import DFA
from project.problems.finite_automaton import (
    FiniteAutomaton,
    State,
    StateTransitions,
    Symbol,
    Transitions,
)


class _NFAStateTransitions(StateTransitions[Set[State]]):
    def __init__(
        self,
        transitions: dict[tuple[State, Symbol], set[State]]
        | Mapping[tuple[State, Symbol], Set[State]],
        state: State,
        mutable_transitions: dict[tuple[State, Symbol], set[State]] | None,
    ) -> None:
        self._transitions = transitions
        self._state = state
        self._mutable_transitions = mutable_transitions

    def __setitem__(self, symbol: Symbol, destination: State) -> None:
        if self._mutable_transitions is None:
            raise TypeError("Transitions are immutable")
        destinations = self._mutable_transitions.setdefault(
            (self._state, symbol),
            set(),
        )
        destinations.add(destination)

    def __getitem__(self, symbol: Symbol) -> Set[State]:
        return self._transitions.get((self._state, symbol), set())


class _NFATransitions(Transitions[Set[State]]):
    def __init__(self) -> None:
        values: dict[tuple[State, Symbol], set[State]] = {}
        self._values: Mapping[
            tuple[State, Symbol],
            Set[State],
        ] = values
        self._mutable_values: dict[
            tuple[State, Symbol],
            set[State],
        ] | None = values

    def __getitem__(
        self,
        state: State,
    ) -> StateTransitions[Set[State]]:
        return _NFAStateTransitions(
            self._values,
            state,
            self._mutable_values,
        )

    def items(self):
        return self._values.items()

    def destinations(self, value: Set[State]) -> Set[State]:
        return value

    def freeze(self) -> None:
        if self._mutable_values is not None:
            self._values = MappingProxyType(
                {
                    key: frozenset(destinations)
                    for key, destinations in self._mutable_values.items()
                }
            )
            self._mutable_values = None


class NFA(FiniteAutomaton[Set[State]]):
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

            for symbol in sorted(self.alphabet):
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
