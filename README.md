# Orbiting Planets Simulation

This project simulates planets orbiting in a solar system using Python and Pygame. It demonstrates gravitational interactions between celestial bodies in a 2D space with an interactive interface.

## Features

- Gravitational forces between celestial bodies
- Collision detection
- Customizable masses, positions, and velocities
- Interactive mode to add planets with a click
- Smooth animation with Pygame

## Requirements

- Python 3.6+
- Pygame module (install with `pip install pygame`)

## How to Run

1. Make sure you have Python installed on your system
2. Install Pygame if you haven't already:
   ```bash
   pip install pygame
   ```
3. Run the simulation:
   ```bash
   python solar_system.py
   ```

## Controls

- **Click anywhere**: Add a new planet at that position
- **ESC key**: Quit the simulation
- **Close window**: Exit the program

## Customization

You can modify the parameters in the script to create your own solar systems:

- Change the mass of the sun (`Sun` class instantiation)
- Modify how planets are created (the `add_random_planet` function)
- Adjust the initial number of planets
- Change the speed parameter for more stable or chaotic orbits

## How It Works

The simulation consists of three main classes:

1. **Body**: Base class for all celestial bodies with physics properties
2. **Sun** and **Planet**: Specialized body types with different appearances
3. **SolarSystem**: Manages all bodies and their interactions