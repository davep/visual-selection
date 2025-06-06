# Visual Selection

## Introduction

Many moons ago, back in 2008, while in a debate on an atheist-oriented phpBB
site (as was the fashion back then), I ended up writing [a couple of
scripts](https://github.com/davep/selection), in ruby, to illustrate a point
about how mutation and selection can, given enough time, result in something
with the appearance of design.

The code was far from a mic-drop body of evidence (it wasn't meant to be), I
think it did an okay job of showing how nothing more than just mutating
something and selecting for the "fitter" options can get you somewhere
meaningful given enough time.

No matter, either you get the illustration or you don't. That's not
important.

Fast forward 15 years and I was thinking that a Textual version of the code
might be fun.

![Visual Selection](https://raw.githubusercontent.com/davep/visual-selection/main/visual-selection.png)

This is a version of
[`selection`](https://github.com/davep/selection/blob/master/selection).
Turns out it *is* fun!

## Installation

### pipx

The package can be installed using [`pipx`](https://pypa.github.io/pipx/):

```sh
$ pipx install visual-selection
```

### Homebrew

The package can be installed using Homebrew. Use the following commands to
install:

```sh
$ brew tap davep/homebrew
$ brew install visual-selection
```

## Running

Once installed run the `visual-selection` command.

[//]: # (README.md ends here)
