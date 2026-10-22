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
        | MappingProxyType,
        state: State,
    ) -> None:
        self._transitions = transitions
        self._state = state

    def __getitem__(self, symbol: Symbol) -> State | None:
        return self._transitions.get((self._state, symbol))

    def __setitem__(self, symbol: Symbol, destination: State) -> None:
        key = (self._state, symbol)
        if not isinstance(self._transitions, dict):
            raise TypeError("Transitions are immutable")
        if key in self._transitions and self._transitions[key] != destination:
            raise ValueError(
                f"Non-deterministic transition from {self._state!r} "
                f"with {symbol!r}"
            )
        self._transitions[key] = destination


class _DFATransitions(Transitions[State]):
    def __init__(self) -> None:
        self._values: dict[tuple[State, Symbol], State] | MappingProxyType = {}

    def __getitem__(
        self,
        state: State,
    ) -> StateTransitions[State]:
        return _DFAStateTransitions(self._values, state)

    def items(self):
        return self._values.items()

    def destinations(self, value: State) -> tuple[State, ...]:
        return (value,)

    def freeze(self) -> None:
        if isinstance(self._values, dict):
            self._values = MappingProxyType(self._values)


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
