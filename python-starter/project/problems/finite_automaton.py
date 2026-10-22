from abc import ABC, abstractmethod
from collections.abc import Iterable, Iterator
from typing import Generic, TextIO, TypeAlias, TypeVar


State: TypeAlias = str
Symbol: TypeAlias = str

TValue = TypeVar("TValue")


class StateTransitions(Generic[TValue], ABC):
    @abstractmethod
    def __getitem__(self, symbol: Symbol) -> TValue:
        raise NotImplementedError

    @abstractmethod
    def __setitem__(self, symbol: Symbol, destination: TValue) -> None:
        raise NotImplementedError


class Transitions(Generic[TValue], ABC):
    @abstractmethod
    def __getitem__(
        self,
        state: State,
    ) -> StateTransitions[TValue]:
        raise NotImplementedError

    @abstractmethod
    def items(
        self,
    ) -> Iterator[tuple[tuple[State, Symbol], TValue]]:
        raise NotImplementedError

    @abstractmethod
    def destinations(self, value: TValue) -> Iterable[State]:
        raise NotImplementedError

    @abstractmethod
    def freeze(self) -> None:
        raise NotImplementedError


class FiniteAutomaton(Generic[TValue], ABC):
    def __init__(
        self,
        states: Iterable[State],
        alphabet: Iterable[Symbol],
        initial_state: State,
        accepting_states: Iterable[State],
        transitions: Transitions[TValue],
    ) -> None:
        self._states = frozenset(states)
        self._alphabet = frozenset(alphabet)
        self._initial_state = initial_state
        self._accepting_states = frozenset(accepting_states)
        transitions.freeze()
        self._transitions = transitions
        self._validate_definition()

    @property
    def states(self) -> frozenset[State]:
        return self._states

    @property
    def alphabet(self) -> frozenset[Symbol]:
        return self._alphabet

    @property
    def initial_state(self) -> State:
        return self._initial_state

    @property
    def accepting_states(self) -> frozenset[State]:
        return self._accepting_states

    @property
    def transitions(self) -> Transitions[TValue]:
        return self._transitions

    def _validate_definition(self) -> None:
        if self.initial_state not in self.states:
            raise ValueError(
                f"Initial state {self.initial_state!r} is not in states"
            )

        invalid_accepting_states = self.accepting_states - self.states
        if invalid_accepting_states:
            raise ValueError(
                "Accepting states are not in states: "
                f"{sorted(invalid_accepting_states)!r}"
            )

        for (source, symbol), value in self.transitions.items():
            if source not in self.states:
                raise ValueError(
                    f"Transition source {source!r} is not in states"
                )
            if symbol not in self.alphabet:
                raise ValueError(
                    f"Transition symbol {symbol!r} is not in alphabet"
                )

            destinations = self.transitions.destinations(value)
            invalid_destinations = set(destinations) - self.states
            if invalid_destinations:
                raise ValueError(
                    "Transition destinations are not in states: "
                    f"{sorted(invalid_destinations)!r}"
                )

    @classmethod
    def from_file(cls, input_file: TextIO):
        return cls(*cls._read_definition(input_file))

    @classmethod
    def _read_definition(cls, input_file: TextIO):
        lines = input_file.readlines()
        states = lines[0].split()
        alphabet = lines[1].split()
        initial_state = lines[2].strip()
        accepting_states = lines[3].split()
        transitions = cls._new_transitions()

        for line in lines[4:]:
            source, symbol, destination = line.split()
            if source not in states:
                raise ValueError(
                    f"Transition source {source!r} is not in states"
                )
            if symbol not in alphabet:
                raise ValueError(
                    f"Transition symbol {symbol!r} is not in alphabet"
                )
            if destination not in states:
                raise ValueError(
                    f"Transition destination {destination!r} is not in states"
                )
            transitions[source][symbol] = destination

        return (
            states,
            alphabet,
            initial_state,
            accepting_states,
            transitions,
        )

    @classmethod
    @abstractmethod
    def _new_transitions(cls) -> Transitions[TValue]:
        raise NotImplementedError

    def __str__(self) -> str:
        lines = [
            " ".join(sorted(self.states)),
            " ".join(self.alphabet),
            self.initial_state,
            " ".join(sorted(self.accepting_states)),
        ]

        for (source, symbol), value in sorted(self.transitions.items()):
            for destination in sorted(self.transitions.destinations(value)):
                lines.append(f"{source} {symbol} {destination}")

        return "\n".join(lines)

    @abstractmethod
    def accepts(self, word: str) -> bool:
        """Return whether the automaton accepts a word."""
        raise NotImplementedError
