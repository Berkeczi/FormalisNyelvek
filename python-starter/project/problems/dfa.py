from collections.abc import Mapping
from types import MappingProxyType

from project.problems.finite_automaton import (
    FiniteAutomaton,
    State,
    StateTransitions,
    Symbol,
    Transitions,
)


class _DFAStateTransitions(StateTransitions[State]):
    def __init__(
        self,
        transitions: dict[tuple[State, Symbol], State]
        | Mapping[tuple[State, Symbol], State],
        state: State,
        mutable_transitions: dict[tuple[State, Symbol], State] | None,
    ) -> None:
        self._transitions = transitions
        self._state = state
        self._mutable_transitions = mutable_transitions

    def __getitem__(self, symbol: Symbol) -> State | None:
        return self._transitions.get((self._state, symbol))

    def __setitem__(self, symbol: Symbol, destination: State) -> None:
        key = (self._state, symbol)
        if self._mutable_transitions is None:
            raise TypeError("Transitions are immutable")
        if (
            key in self._mutable_transitions
            and self._mutable_transitions[key] != destination
        ):
            raise ValueError(
                f"Non-deterministic transition from {self._state!r} "
                f"with {symbol!r}"
            )
        self._mutable_transitions[key] = destination


class _DFATransitions(Transitions[State]):
    def __init__(self) -> None:
        values: dict[tuple[State, Symbol], State] = {}
        self._values: Mapping[tuple[State, Symbol], State] = values
        self._mutable_values: dict[tuple[State, Symbol], State] | None = values

    def __getitem__(
        self,
        state: State,
    ) -> StateTransitions[State]:
        return _DFAStateTransitions(
            self._values,
            state,
            self._mutable_values,
        )

    def items(self):
        return self._values.items()

    def destinations(self, value: State) -> tuple[State, ...]:
        return (value,)

    def freeze(self) -> None:
        if self._mutable_values is not None:
            self._values = MappingProxyType(self._mutable_values)
            self._mutable_values = None


class DFA(FiniteAutomaton[State]):
    @classmethod
    def _new_transitions(cls) -> _DFATransitions:
        return _DFATransitions()

    def accepts(self, word: str) -> bool:
        current_state = self.initial_state

        for symbol in word:
            current_state = self.transitions[current_state][symbol]
            if current_state is None:
                return False

        return current_state in self.accepting_states
