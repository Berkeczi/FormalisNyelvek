from __future__ import annotations

from collections import deque
from collections.abc import Iterable, Mapping
from types import MappingProxyType
from typing import TypeAlias

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


class _Sink:
    pass


_CompletedState: TypeAlias = State | _Sink
_CompletedTransitions: TypeAlias = dict[
    _CompletedState,
    dict[Symbol, _CompletedState],
]


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

    def is_complete(self) -> bool:
        return all(
            self.transitions[state][symbol] is not None
            for state in self.states
            for symbol in self.alphabet
        )

    def _reachable_states(self) -> set[State]:
        reachable = {self.initial_state}
        pending_states = deque([self.initial_state])

        while pending_states:
            state = pending_states.popleft()
            for symbol in self.alphabet:
                destination = self.transitions[state][symbol]
                if destination is not None and destination not in reachable:
                    reachable.add(destination)
                    pending_states.append(destination)

        return reachable

    def _complete_transitions(
        self,
        states: Iterable[State],
    ) -> tuple[_Sink, _CompletedTransitions]:
        sink = _Sink()
        completed = {
            state: {
                symbol: (
                    self.transitions[state][symbol]
                    if self.transitions[state][symbol] is not None
                    else sink
                )
                for symbol in self.alphabet
            }
            for state in states
        }
        completed[sink] = {
            symbol: sink
            for symbol in self.alphabet
        }
        return sink, completed

    def minimize(self) -> DFA:
        reachable = self._reachable_states()
        sink, completed_transitions = self._complete_transitions(reachable)
        complete_states: list[_CompletedState] = sorted(reachable) + [sink]
        table: dict[_CompletedState, dict[_CompletedState, bool]] = {
            first: {second: False for second in complete_states}
            for first in complete_states
        }

        def mark_pair(
            first: _CompletedState,
            second: _CompletedState,
        ) -> None:
            table[first][second] = True
            table[second][first] = True

        for position, first in enumerate(complete_states):
            for second in complete_states[position + 1:]:
                if (
                    (first in self.accepting_states)
                    != (second in self.accepting_states)
                ):
                    mark_pair(first, second)

        changed = True
        while changed:
            changed = False
            for position, first in enumerate(complete_states):
                for second in complete_states[position + 1:]:
                    if table[first][second]:
                        continue
                    for symbol in self.alphabet:
                        first_destination = completed_transitions[first][symbol]
                        second_destination = completed_transitions[second][symbol]
                        if table[first_destination][second_destination]:
                            mark_pair(first, second)
                            changed = True
                            break

        classes = [{state} for state in complete_states]
        class_by_state = {
            state: state_class
            for state_class in classes
            for state in state_class
        }

        for position, first in enumerate(complete_states):
            for second in complete_states[position + 1:]:
                if table[first][second]:
                    continue

                first_class = class_by_state[first]
                second_class = class_by_state[second]
                if first_class is second_class:
                    continue

                first_class.update(second_class)
                for state in second_class:
                    class_by_state[state] = first_class
                classes.remove(second_class)

        label_by_state: dict[State, State] = {}
        representatives: dict[State, State] = {}
        accepting_states: set[State] = set()
        for state_class in classes:
            actual_states = state_class & reachable
            if not actual_states:
                continue
            label = f"s{min(int(state[1:]) for state in actual_states)}"
            representative = min(actual_states)
            representatives[label] = representative
            for state in actual_states:
                label_by_state[state] = label
            if actual_states & self.accepting_states:
                accepting_states.add(label)

        initial_state = label_by_state[self.initial_state]
        transitions = self._new_transitions()

        for state, representative in representatives.items():
            for symbol in sorted(self.alphabet):
                destination = completed_transitions[representative][symbol]
                if destination is sink:
                    continue
                destination = label_by_state[destination]
                transitions[state][symbol] = destination

        states = set(representatives)

        return DFA(
            states,
            self.alphabet,
            initial_state,
            accepting_states,
            transitions,
        )
