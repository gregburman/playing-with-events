# Playing With Events

Toy project for testing background activity event filter. Based on Tkinter, the only dependency is numpy.

A demonstration is shown in demo.mp4. Note that the outputs are as follows:

- top left: noise event stream
- top right: Signal (S) stream
- bottom left: combined stream
- bottom right: combined stream with noise filter applied.

## Installation

The only requirement is `tkinter`. It comes pre-installed on most systems, however if it's missing on your system you can install it with your package manager, e.g. on Arch Linux:

```
sudo pacman -S tk
```

## Running

Run the following source file:

```
python run.py --timesteps <timesteps> --framerate <framerate> --noise-bounds <lower-bound> <upper-bound> --hide-grid-outline
```

where

- `<timesteps>` is the number of time steps the simulation runs over (default: 100)
- `<framerate>` is the speed at which the timesteps are processed and displayed (default: 30)
- `<lower-bound>` and `<upper-bound>` are the lower and upper bounds for the number of randomly-generated events per timestep (default: 2 10)

and `--hide-grid-outline` simply hides the white pixel outlines (shown by default).
