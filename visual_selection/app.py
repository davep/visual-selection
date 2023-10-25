"""Simple evolution by mutation in a fitness landscape example."""

##############################################################################
# Be future-proof.
from __future__ import annotations

##############################################################################
# Python imports.
from dataclasses import dataclass
from random import choices, randint
from typing_extensions import Self

##############################################################################
# Textual imports.
from textual import on, work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal
from textual.message import Message
from textual.widgets import Button, Footer, Input, Label, ProgressBar, RichLog
from textual.worker import get_current_worker

##############################################################################
# Textual Plotext imports.
from textual_plotext import PlotextPlot

##############################################################################
# Rich imports.
from rich.markup import escape
from rich.text import Text

CHARACTERS = [chr(n) for n in range(32, 126)]
"""The characters that will be used as the parts of the things to evolve."""


##############################################################################
class Entity:
    """An entity in the landscape."""

    def __init__(self, genome: list[str] | int) -> None:
        """Initialise the entity.

        Args:
            genome: Either the genome of the entity, or its size.

        Note:
            If a size is given, a totally random genome is created.
        """
        self._genome = (
            choices(CHARACTERS, k=genome) if isinstance(genome, int) else list(genome)
        )

    def mutate(self) -> Self:
        """Add a random mutation to the entity's genome.

        Returns:
            Self;
        """
        self._genome[randint(0, len(self._genome) - 1)] = choices(CHARACTERS, k=1)[0]
        return self

    @property
    def genome(self) -> list[str]:
        """A copy of the entity's genome."""
        return list(self._genome)

    def __repr__(self) -> str:
        return "".join(self._genome)


##############################################################################
def breed(first: Entity, second: Entity) -> Entity:
    """Breed two entities, giving a third.

    Args:
        first: The first parent.
        second: The second parent.

    Returns:
        The offspring of the pairing.

    In this version of breeding, a random section of the genome is taken
    from the first parent, and placed into that of the second parent, giving
    an offspring, point mutation is then applied.
    """
    new_genome = first.genome
    start = randint(0, len(first.genome) - 1)
    end = randint(start, len(first.genome))
    new_genome[start:end] = second.genome[start:end]
    return Entity(new_genome).mutate()


##############################################################################
def difference(first: Entity | str, second: Entity | str) -> int:
    """Calculate the difference between two genomes.

    Args:
        first: The first entity to look at.
        second: The second entity to look at.

    Returns:
        The count of differences.

    In other words: the hamming distance.
    """
    return sum(
        base1 != base2
        for base1, base2 in zip(
            first if isinstance(first, str) else first.genome,
            second if isinstance(second, str) else second.genome,
        )
    )


##############################################################################
class Environment:
    """The environment in which the evolution will take place."""

    def __init__(self, landscape: str) -> None:
        """Initialise the landscape.

        Args:
            landscape: The target string, the 'best' fit for the landscape.
        """
        self._landscape = landscape
        self._best = Entity(len(self._landscape))
        self._next_best = Entity(len(self._landscape))

    def shit_happens(self) -> Self:
        """No. I'm, I'm simply saying that life, uh... finds a way."""

        # Breed the two most-fit parents and get a new child.
        child = breed(self._best, self._next_best)

        # Work out how different the family is from the landscape.
        child_score = difference(child, self._landscape)
        best_score = difference(self._best, self._landscape)
        next_best_score = difference(self._next_best, self._landscape)

        # If the child is better than the absolute best...
        if child_score < best_score:
            # ...shuffle the pack so it's the best and the previous best is
            # the next best.
            self._next_best = self._best
            self._best = child
        elif child_score < next_best_score:
            # It's not the best, but it is the next best.
            self._next_best = child

        return self

    @property
    def landscape(self) -> list[str]:
        """The fitness landscape."""
        return list(self._landscape)

    @property
    def best(self) -> tuple[Entity, Entity]:
        """A tuple of the best and next best entities found."""
        return self._best, self._next_best

    @property
    def distances(self) -> tuple[int, int]:
        """The distances of the best and next best entity, from the target."""
        return difference(self._best, self._landscape), difference(
            self._next_best, self._landscape
        )

    @property
    def best_fit_found(self) -> bool:
        """Has the best fit been found?"""
        return difference(self._best, self._landscape) == 0


##############################################################################
class SelectionApp(App[None]):
    """Simple application to show off mutation in a fitness landscape."""

    CSS = """
    #input, #status-bar {
        height: auto;
        background: $panel;
    }

    #input > Input {
        width: 1fr;
    }

    #status-bar {
        padding: 1;
    }

    #status-bar .label {
        padding-left: 4;
    }

    RichLog {
        height: 2fr;
        background: $panel;
        border: round $background;
    }

    RichLog:focus {
        border: round $accent;
    }

    PlotextPlot {
        height: 1fr;
        background: $panel;
        color: $accent;
    }

    ProgressBar {
        background: $panel;
        width: 1fr;
        padding: 0 1 0 1;
    }

    ProgressBar Bar {
        width: 1fr;
    }
    """

    BINDINGS = [Binding("ctrl+q", "quit", "Quit")]

    def __init__(self) -> None:
        """Initialise the application."""
        super().__init__()
        self._progress: list[tuple[int, float]] = []

    def compose(self) -> ComposeResult:
        """Compose the layout of the application."""
        with Horizontal(id="input"):
            yield Input(placeholder="Fitness landscape phrase")
            yield Button("Evolve!")
        with Horizontal(id="status-bar"):
            yield Label("Generations: ")
            yield Label("0", id="iterations")
            yield Label("Best: ", classes="label")
            yield Label("", id="best")
        yield ProgressBar()
        yield RichLog()
        yield PlotextPlot()
        yield Footer()

    def on_mount(self) -> None:
        """Set up the plot on mount."""
        plot = self.query_one(PlotextPlot)
        plot.plt.title("Percentage match vs generations")
        plot.plt.xlabel("Generations")
        plot.plt.ylabel("%age match")
        plot.plt.ylim(0, 100)
        plot.plt.yticks([0, 25, 50, 75, 100], ["0%", "25%", "50%", "75%", "100%"])
        self.refresh_plot()

    def refresh_plot(self) -> None:
        """Refresh the data for the plot."""
        plt = self.query_one(PlotextPlot).plt
        plt.cld()
        plt.ylim(0, 100)
        plt.plot(*zip(*self._progress), marker="braille")

    @on(Button.Pressed)
    @on(Input.Submitted)
    def start_world(self) -> None:
        """Kick off a new evolution."""
        if target := self.query_one(Input).value:
            self.run_world(target)
        else:
            self.query_one(Input).value = (
                "Ca-Caw! Ca-Caw! Ca-Caw! Ah Ah Ee Ee Tookie Tookie! "
                "Tookie Tookie! Ca-Caw Ca-ca-caw-ca-caw-caw-caw! Ca-ca-caw!"
            )
            self.start_world()

    @dataclass
    class WorldUpdate(Message):
        """Message sent when a world gets an update."""

        environment: Environment
        """The environment that the world exists in."""

        iterations: int
        """The number of iterations that have taken place."""

        best: Entity
        """The most-fit entity encountered so far."""

        next_best: Entity
        """The second-most-ft entity encountered so far."""

        def diff(self) -> Text:
            """Create a colour-coded diff of the best entity vs the fitness landscape.

            Returns:
                A rich `Text` object that highlights the differences.
            """
            colours = {True: "green", False: "red"}
            return Text.from_markup(
                "".join(
                    f"[{colours[entity_base == landscape_base]}]{escape(entity_base)}[/]"
                    for entity_base, landscape_base in zip(
                        self.best.genome, self.environment.landscape
                    )
                )
            )

    @dataclass
    class Finished(Message):
        """Message sent when fitness has been achieved."""

        iterations: int
        """The number of iterations it took."""

    @on(WorldUpdate)
    def show_progress(self, event: WorldUpdate) -> None:
        """Show the current progress.

        Args:
            event: The update event.
        """
        self.query_one("#iterations", Label).update(str(event.iterations))
        self.query_one("#best", Label).update(event.diff())
        if event.iterations == 0:
            self._progress = [(0, 0)]
            self.query_one(RichLog).clear()
            self.query_one(ProgressBar).total = len(event.environment.landscape)
            self.query_one(ProgressBar).progress = 0
        else:
            self._progress.append(
                (
                    event.iterations,
                    (100.0 / len(event.environment.landscape))
                    * (
                        len(event.environment.landscape)
                        - event.environment.distances[0]
                    ),
                )
            )
        self.query_one(RichLog).write(event.diff())
        self.query_one(ProgressBar).progress = (
            len(event.environment.landscape) - event.environment.distances[0]
        )
        self.refresh_plot()
        self.query_one(PlotextPlot).refresh()

    @on(Finished)
    def show_result(self, event: Finished) -> None:
        """Show the final result.

        Args:
            event: The finishing result.
        """
        self.notify(
            f"Target fitness match achieved after {event.iterations} generations."
        )
        self.bell()

    @work(thread=True, exclusive=True)
    def run_world(self, target: str) -> None:
        """Run the world.

        Args:
            target: The target landscape fitness phrase.
        """
        worker = get_current_worker()
        environment = Environment(target)
        iterations = 0
        self.post_message(self.WorldUpdate(environment, iterations, *environment.best))
        while not worker.is_cancelled and not environment.best_fit_found:
            environment.shit_happens()
            iterations += 1
            if (iterations % 1000) == 0 or environment.best_fit_found:
                self.post_message(
                    self.WorldUpdate(environment, iterations, *environment.best)
                )
        if environment.best_fit_found:
            self.post_message(self.Finished(iterations))


### app.py ends here
