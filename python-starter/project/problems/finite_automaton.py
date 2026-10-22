from abc import ABC, abstractmethod


class _StateTransitions:
    def __init__(self, transitions, state):
        self._transitions = transitions
        self._state = state

    def __setitem__(self, symbol, destination):
        destinations = self._transitions.setdefault((self._state, symbol), set())
        destinations.add(destination)

    def __getitem__(self, symbol):
        return self._transitions.get((self._state, symbol), set())


class _Transitions:
    def __init__(self):
        self._values = {}

    def __getitem__(self, state):
        return _StateTransitions(self._values, state)

    def items(self):
        return self._values.items()


class FiniteAutomaton(ABC):
    def __init__(
        self,
        states,
        alphabet,
        initial_state,
        accepting_states,
        transitions,
    ):
        self.states = states
        self.alphabet = alphabet
        self.initial_state = initial_state
        self.accepting_states = set(accepting_states)
        self.transitions = transitions

    @classmethod
    def from_file(cls, input_file):
        return cls(*cls._read_definition(input_file))

    @staticmethod
    def _read_definition(input_file):
        lines = input_file.readlines()
        states = lines[0].split()
        alphabet = lines[1].split()
        initial_state = lines[2].strip()
        accepting_states = lines[3].split()
        transitions = _Transitions()

        for line in lines[4:]:
            source, symbol, destination = line.split()
            transitions[source][symbol] = destination

        return (
            states,
            alphabet,
            initial_state,
            accepting_states,
            transitions,
        )

    @staticmethod
    def _new_transitions():
        return _Transitions()

    def __str__(self):
        lines = [
            " ".join(sorted(self.states)),
            " ".join(self.alphabet),
            self.initial_state,
            " ".join(sorted(self.accepting_states)),
        ]

        for (source, symbol), destinations in sorted(self.transitions.items()):
            for destination in sorted(destinations):
                lines.append(f"{source} {symbol} {destination}")

        return "\n".join(lines)

    @abstractmethod
    def delta(self, state, symbol):
        """Return the state or states reached by reading a symbol."""
        raise NotImplementedError

    @abstractmethod
    def accepts(self, word):
        """Return whether the automaton accepts a word."""
        raise NotImplementedError
