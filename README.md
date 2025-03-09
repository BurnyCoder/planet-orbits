# Orbiting Planets Simulation

This project simulates planets orbiting in a solar system using Python and Pygame. It demonstrates gravitational interactions between celestial bodies in a 2D space with an interactive interface.

![image](https://github.com/user-attachments/assets/483a2f81-b20b-482e-97d7-ab3c63663597)

## Features

- Gravitational forces between celestial bodies
- Realistic collision detection between all types of celestial bodies
- Customizable masses, positions, and velocities
- Interactive mode to add planets with a click
- Asteroid creation with elliptical orbits
- "Alien Physics" mode with 7 different creative physics simulations
- Event message log system for feedback
- Semi-transparent UI elements
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
- **O key**: Toggle orbit display
- **T key**: Toggle orbit trails
- **C key**: Toggle orbit correction
- **P key**: Toggle alien physics mode
- **A key**: Add asteroid with elliptical orbit
- **+/- keys**: Change simulation speed
- **S key**: Reset simulation speed to normal
- **Close window**: Exit the program

## Advanced Features

### Collision System
The simulation includes a sophisticated collision detection system that handles:
- Sun-Planet collisions (sun destroys planets)
- Sun-Asteroid collisions (sun destroys asteroids)
- Planet-Asteroid collisions (planets absorb asteroids)

### Alien Physics
When enabled, the simulation cycles through 7 different physics modes every 10 seconds:
- Magnetic Ballet
- Orbital Waltz
- Vibration Samba
- Quantum Tango
- Choreographed Orbits
- Spiral Dance
- Rhythmic Pulsation

Each mode creates unique and visually interesting orbital patterns that defy conventional physics.

### Message Log System
A message log in the bottom left corner provides real-time feedback on events in the simulation, including:
- New celestial body creation
- Collisions and destructions
- Physics mode changes
- Setting toggles

### Visual Design
- Semi-transparent text for a cleaner interface
- Color-coded status indicators
- Planet trails and orbit visualization options
- Dynamic planet and asteroid naming

## Customization

You can modify the parameters in the script to create your own solar systems:

- Change the mass of the sun (`Sun` class instantiation)
- Modify how planets are created (the `add_random_planet` function)
- Adjust the initial number of planets
- Change the speed parameter for more stable or chaotic orbits
- Customize the alien physics modes in the `calculate_gravity` method

## How It Works

The simulation consists of four main classes:

1. **Body**: Base class for all celestial bodies with physics properties
2. **Sun**: Central gravitational body that other objects orbit around
3. **Planet**: Regular orbital bodies that can have different colors and sizes
4. **Asteroid**: Smaller bodies with elliptical orbits and special rendering
5. **SolarSystem**: Manages all bodies and their interactions

The simulation primarily implements Newton's law of universal gravitation (`force = GRAVITY_STRENGTH * first.mass * second.mass / (distance * distance + DISTANCE_DAMPING)`), Newton's second law (`acceleration = force / mass`), orbital velocity inspired by Kepler's laws (`orbital_speed = math.sqrt(sun.mass / distance) * orbital_speed_factor`), basic kinematics for position and velocity updates, distance calculation using the Euclidean formula, and orbital correction formulas to maintain stable planetary orbits.
