"""
Solar System Simulation using Pygame
This is an alternative to the turtle-based simulation that doesn't rely on tkinter.
"""
import math
import random
import sys

try:
    import pygame
except ImportError:
    print("This simulation requires pygame. Please install it with:")
    print("pip install pygame")
    sys.exit(1)

# Initialize pygame
pygame.init()

# Screen setup
WIDTH, HEIGHT = 1400, 900
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Solar System Simulation")

# Global time factor to control simulation speed
TIME_SCALE = 0.25  # Lower values = slower simulation

# Gravitational force scaling - lower value = less gravitational pull
GRAVITY_STRENGTH = 0.5  # Reduced from implicit 1.0

# Numerical stability parameters
DISTANCE_DAMPING = 10.0  # Higher value reduces gravitational force at close distances
ORBIT_CORRECTION = 0.02  # Increased from 0.01 for better stability

# Define colors with alpha channel
BLACK = (0, 0, 0, 255)  # Fully opaque black
YELLOW = (255, 255, 0, 128)  # Semi-transparent yellow
RED = (255, 0, 0, 128)  # Semi-transparent red
GREEN = (0, 255, 0, 128)  # Semi-transparent green
BLUE = (0, 0, 255, 128)  # Semi-transparent blue
WHITE = (255, 255, 255, 128)  # Semi-transparent white

# Planet colors with alpha
MERCURY_COLOR = (169, 169, 169, 128)  # Gray
VENUS_COLOR = (244, 226, 181, 128)    # Pale yellow/cream
EARTH_COLOR = (0, 128, 255, 128)      # Blue
MARS_COLOR = (188, 39, 50, 128)       # Red-brown
JUPITER_COLOR = (255, 196, 148, 128)  # Light orange
SATURN_COLOR = (236, 205, 151, 128)   # Pale gold
URANUS_COLOR = (172, 230, 236, 128)   # Pale cyan
NEPTUNE_COLOR = (41, 95, 153, 128)    # Deep blue

# Planet colors for random planets
PLANET_COLORS = [RED, GREEN, BLUE]

# Asteroid colors with alpha
ASTEROID_COLOR_BASE = (150, 140, 120, 128)  # Brownish-gray
ASTEROID_BELT_COLOR = (100, 100, 100, 128)  # Dark gray for orbit paths

# Clock for controlling frame rate
clock = pygame.time.Clock()
FPS = 60

# Global lists for random planet name generation
PLANET_NAME_PREFIXES = [
    "Nova", "Astro", "Cosmo", "Stella", "Lumi", "Orbi", "Chrono", "Galax", 
    "Nebula", "Void", "Sol", "Luna", "Aster", "Celest", "Empyr", "Ether",
    "Merc", "Plu", "Sat", "Jup", "Mar", "Ter", "Ven", "Zeus", "Hades", "Posei"
]

PLANET_NAME_SUFFIXES = [
    "on", "ia", "ius", "us", "ius", "ix", "or", "um", "ean", "aris", "oid",
    "ite", "ese", "nia", "ria", "sia", "tis", "mus", "pus", "ter", "cus", "tus",
    "rus", "nox", "rax", "lax", "ton", "tron", "za", "ga", "na", "ma", "tha"
]

PLANET_NAME_MODIFIERS = [
    "Prime", "Alpha", "Beta", "Gamma", "Delta", "Minor", "Major", "Superior",
    "Inferior", "Proxima", "Ultima", "Nova", "Maximus", "Minimus", "Secundus"
]

# Global lists for random asteroids
ASTEROID_NAME_PREFIXES = ["Ceres", "Vesta", "Pallas", "Juno", "Hygiea", "Ida", "Eros", "Gaspra"]
ASTEROID_NAME_SUFFIXES = ["is", "oid", "ia", "us", "a", "e", "os", "ium", "onia"]

def generate_random_planet_name():
    """Generate a random planet name using combinations of prefixes and suffixes."""
    name_type = random.randint(1, 3)
    
    if name_type == 1:
        # Simple name: prefix + suffix (e.g., "Astron")
        name = random.choice(PLANET_NAME_PREFIXES) + random.choice(PLANET_NAME_SUFFIXES)
    elif name_type == 2:
        # Double name: prefix + suffix + space + prefix + suffix (e.g., "Nebularis Voidtron")
        name = random.choice(PLANET_NAME_PREFIXES) + random.choice(PLANET_NAME_SUFFIXES)
        name += " " + random.choice(PLANET_NAME_PREFIXES) + random.choice(PLANET_NAME_SUFFIXES)
    else:
        # Modified name: prefix + suffix + space + modifier (e.g., "Stellion Prime")
        name = random.choice(PLANET_NAME_PREFIXES) + random.choice(PLANET_NAME_SUFFIXES)
        name += " " + random.choice(PLANET_NAME_MODIFIERS)
    
    # Sometimes add a number designation
    if random.random() < 0.3:  # 30% chance
        name += " " + str(random.randint(1, 999))
    
    return name

def generate_random_asteroid_name():
    """Generate a random asteroid name."""
    if random.random() < 0.5:
        name = random.choice(ASTEROID_NAME_PREFIXES) + random.choice(ASTEROID_NAME_SUFFIXES)
    else:
        name = random.choice(ASTEROID_NAME_PREFIXES) + "-" + str(random.randint(1, 9999))
    
    return name

class Body:
    """Base class for all celestial bodies."""
    min_display_size = 5  # Smaller minimum size
    display_log_base = 1.5  # Increased log base for more size difference
    
    def __init__(self, mass, position=(0, 0), velocity=(0, 0), color=WHITE):
        self.mass = mass
        self.position = position  # (x, y)
        self.velocity = velocity  # (vx, vy)
        self.color = color
        self.display_size = max(
            int(math.log(self.mass, self.display_log_base)),
            self.min_display_size,
        )
    
    def move(self):
        """Update position based on velocity, using the global time scale."""
        x, y = self.position
        vx, vy = self.velocity
        # Apply time scale to velocity
        self.position = (x + vx * TIME_SCALE, y + vy * TIME_SCALE)
    
    def draw(self, surface):
        """Draw the body on the given surface."""
        x, y = self.position
        screen_x = int(x + WIDTH // 2)
        screen_y = int(y + HEIGHT // 2)
        pygame.draw.circle(surface, self.color, (screen_x, screen_y), self.display_size)
    
    def distance_to(self, other):
        """Calculate distance to another body."""
        x1, y1 = self.position
        x2, y2 = other.position
        return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    
    def angle_to(self, other):
        """Calculate angle to another body in radians."""
        x1, y1 = self.position
        x2, y2 = other.position
        return math.atan2(y2 - y1, x2 - x1)

class Sun(Body):
    """A sun in the solar system."""
    def __init__(self, mass, position=(0, 0), velocity=(0, 0)):
        super().__init__(mass, position, velocity, YELLOW)

class Planet(Body):
    """A planet in the solar system."""
    def __init__(self, mass, position=(0, 0), velocity=(0, 0), color=None, has_rings=False):
        if color is None:
            color = random.choice(PLANET_COLORS)
        super().__init__(mass, position, velocity, color)
        self.has_rings = has_rings
        self.ring_color = (200, 200, 170)  # Light gray for rings
    
    def draw(self, surface):
        """Draw the planet and its rings if it has any."""
        x, y = self.position
        screen_x = int(x + WIDTH // 2)
        screen_y = int(y + HEIGHT // 2)
        
        # Draw the planet
        pygame.draw.circle(surface, self.color, (screen_x, screen_y), self.display_size)
        
        # Draw rings if the planet has them (like Saturn)
        if self.has_rings:
            # Calculate ring dimensions based on planet size
            ring_width = int(self.display_size * 1.0)  # Wider rings
            
            # Outer ring
            ring_rect = pygame.Rect(
                screen_x - self.display_size - ring_width,
                screen_y - self.display_size // 3,
                (self.display_size + ring_width) * 2,
                self.display_size * 2 // 3
            )
            # Draw an ellipse for the rings
            pygame.draw.ellipse(surface, self.ring_color, ring_rect, 1)
            
            # Inner ring - slightly smaller
            inner_rect = pygame.Rect(
                screen_x - self.display_size - ring_width//2,
                screen_y - self.display_size // 4,
                (self.display_size + ring_width//2) * 2,
                self.display_size * 2 // 4
            )
            pygame.draw.ellipse(surface, self.ring_color, inner_rect, 1)

class Asteroid(Body):
    """An asteroid in the solar system."""
    def __init__(self, mass, position=(0, 0), velocity=(0, 0), eccentricity=0.3):
        """Initialize an asteroid with given properties and random color variation."""
        # Create subtle color variation for asteroids
        color_variation = random.uniform(-20, 20)
        color = (
            min(255, max(0, ASTEROID_COLOR_BASE[0] + color_variation)),
            min(255, max(0, ASTEROID_COLOR_BASE[1] + color_variation)),
            min(255, max(0, ASTEROID_COLOR_BASE[2] + color_variation))
        )
        super().__init__(mass, position, velocity, color)
        self.eccentricity = eccentricity  # Orbit eccentricity (0 = circular, higher = more elliptical)
        
    def draw(self, surface):
        """Draw the asteroid as a small irregular shape."""
        x, y = self.position
        screen_x = int(x + WIDTH // 2)
        screen_y = int(y + HEIGHT // 2)
        
        # Draw a small dot for the asteroid
        pygame.draw.circle(surface, self.color, (screen_x, screen_y), self.display_size)
        
        # Add a small irregular shape to make it look more like an asteroid
        # Rather than a perfect circle
        points = []
        for i in range(5):  # Create a rough pentagon
            angle = 2 * math.pi * i / 5 + random.uniform(-0.2, 0.2)
            point_x = screen_x + math.cos(angle) * (self.display_size - 1)
            point_y = screen_y + math.sin(angle) * (self.display_size - 1)
            points.append((point_x, point_y))
        
        # Draw the irregular shape
        if len(points) >= 3:  # Need at least 3 points for a polygon
            pygame.draw.polygon(surface, self.color, points)

class SolarSystem:
    """Manages all the bodies in the solar system and their interactions."""
    def __init__(self):
        self.bodies = []
        self.planet_names = {}  # Dictionary to store planet names
        self.show_orbits = True  # Flag to show orbit paths
        self.show_trails = True  # Flag to show celestial body trails
        self.body_trails = {}  # Dictionary to store body trail points
        self.initial_distances = {}  # Store initial distances from sun for orbit correction
        self.orbit_correction_enabled = True  # Flag to toggle orbit correction
        self.alien_physics_enabled = False  # Flag to toggle alien physics mode
        self.current_physics_mode = 0  # Track the current physics mode for oscillation
        self.message_log = []  # List to store game messages for display
        self.max_log_messages = 5  # Maximum number of messages to display at once
    
    def add_body(self, body, name=None):
        """Add a body to the solar system."""
        self.bodies.append(body)
        if name:
            self.planet_names[body] = name
            # Initialize empty trail for the planet or asteroid
            if isinstance(body, Planet) or isinstance(body, Asteroid):
                self.body_trails[body] = []
                
                # Store initial distance from sun for orbit correction
                sun = None
                for b in self.bodies:
                    if isinstance(b, Sun):
                        sun = b
                        break
                
                if sun:
                    distance = body.distance_to(sun)
                    self.initial_distances[body] = distance
    
    def remove_body(self, body):
        """Remove a body from the solar system."""
        # Get the body name if it exists
        name = self.planet_names.get(body, "unnamed")
        
        # Log removal with appropriate body type
        body_type = "Body"
        if isinstance(body, Sun): body_type = "Sun"
        elif isinstance(body, Planet): body_type = "Planet"
        elif isinstance(body, Asteroid): body_type = "Asteroid"
        
        # Print log message 
        print(f"{body_type} {name} was destroyed!")
        
        # Remove from planet names dictionary
        if body in self.planet_names:
            self.planet_names.pop(body)
            
        # Remove from trails dictionary
        if body in self.body_trails:
            self.body_trails.pop(body)
            
        # Remove from initial distances dictionary
        if body in self.initial_distances:
            self.initial_distances.pop(body)
            
        # Only call clear() if it's available (SolarSystemBody class from turtle)
        if hasattr(body, 'clear'):
            body.clear()
        
        self.bodies.remove(body)
    
    def update_all(self, surface):
        """Update and draw all bodies."""
        # Draw orbit circles first (if enabled)
        if self.show_orbits:
            # Find the sun to center orbits
            sun_pos = (0, 0)
            for body in self.bodies:
                if isinstance(body, Sun):
                    sun_pos = body.position
                    break
            
            sun_screen_x = int(sun_pos[0] + WIDTH // 2)
            sun_screen_y = int(sun_pos[1] + HEIGHT // 2)
            
            # Draw orbit circles for each planet
            for body in self.bodies:
                if isinstance(body, Planet):
                    # Calculate distance from sun to planet
                    dx = body.position[0] - sun_pos[0]
                    dy = body.position[1] - sun_pos[1]
                    distance = math.sqrt(dx*dx + dy*dy)
                    
                    # Draw orbit circle (very thin, light gray)
                    orbit_color = (50, 50, 50)  # Dark gray
                    pygame.draw.circle(surface, orbit_color, (sun_screen_x, sun_screen_y), 
                                      int(distance), 1)
        
        # Draw trails for celestial bodies first (so they appear behind the bodies)
        if self.show_trails:
            for body, trail_points in self.body_trails.items():
                if len(trail_points) >= 2:  # Need at least 2 points to draw a line
                    # Use the body's color but with reduced alpha for the trail
                    trail_color = body.color
                    # Draw lines connecting trail points
                    pygame.draw.lines(surface, trail_color, False, trail_points, 1)
        
        # Update and draw all bodies
        for body in self.bodies:
            # Update position
            body.move()
            
            # Record trail for bodies
            if body in self.body_trails:
                # Add current position to trail
                x, y = body.position
                screen_x = int(x + WIDTH // 2)
                screen_y = int(y + HEIGHT // 2)
                self.body_trails[body].append((screen_x, screen_y))
                
                # Limit trail length
                max_trail_length = 50
                if len(self.body_trails[body]) > max_trail_length:
                    self.body_trails[body] = self.body_trails[body][-max_trail_length:]
            
            # Draw body
            body.draw(surface)
            
            # If the body has a name, display it
            if body in self.planet_names:
                x, y = body.position
                screen_x = int(x + WIDTH // 2)
                screen_y = int(y + HEIGHT // 2)
                
                # Create a small font for the planet names
                font = pygame.font.SysFont('Arial', 12)
                # Render the name with white
                text = font.render(self.planet_names[body], True, WHITE)
                
                # Create a transparent surface for the text
                label_surface = pygame.Surface(text.get_size(), pygame.SRCALPHA)
                label_surface.set_alpha(128)
                label_surface.blit(text, (0, 0))
                
                # Position the text just above the planet
                text_rect = label_surface.get_rect(center=(screen_x, screen_y - body.display_size - 5))
                surface.blit(label_surface, text_rect)
    
    def calculate_gravity(self, first, second):
        """Calculate gravitational effect between two bodies."""
        # Skip if the bodies are too close to avoid division by zero
        distance = first.distance_to(second)
        if distance < 1:
            return
        
        # Calculate angle before any physics calculations
        angle = first.angle_to(second)
        
        # Calculate force based on masses and distance with additional damping
        if self.alien_physics_enabled:
            # ALIEN PHYSICS: Now oscillates between different modes over time
            
            # Determine physics mode based on time rather than body pairs
            # Change modes every few seconds
            mode_duration = 10  # seconds per mode
            time_seconds = pygame.time.get_ticks() / 1000
            current_mode = int(time_seconds / mode_duration) % 7  # Cycle through all 7 modes
            
            # Check if mode has changed and log the change
            if current_mode != self.current_physics_mode:
                mode_names = [
                    "Magnetic Ballet",
                    "Orbital Waltz",
                    "Vibration Samba",
                    "Quantum Tango",
                    "Choreographed Orbits",
                    "Spiral Dance",
                    "Rhythmic Pulsation"
                ]
                
                # Add message about mode change with appropriate color
                mode_colors = [
                    (255, 100, 100),  # Red for magnetic ballet
                    (100, 255, 100),  # Green for orbital waltz
                    (100, 100, 255),  # Blue for vibration samba
                    (255, 255, 100),  # Yellow for quantum tango
                    (255, 100, 255),  # Magenta for choreographed orbits
                    (255, 100, 100),  # Red for spiral dance
                    (100, 100, 255)   # Blue for rhythmic pulsation
                ]
                
                # Log the mode change with the color of the new mode
                self.add_message(f"Physics mode changed to: {mode_names[current_mode]}", mode_colors[current_mode])
            
            # Store the current mode for display
            self.current_physics_mode = current_mode
            
            # Set physics mode for calculations
            physics_mode = current_mode
            
            if physics_mode == 0:
                # Magnetic Ballet
                # Magnetic field - repulsion and attraction based on "charge"
                # Use mass parity as a proxy for charge (odd vs even)
                charge_first = first.mass % 2
                charge_second = second.mass % 2
                
                # Like charges repel, unlike charges attract - but with reduced force
                attraction_factor = 0.15  # Reduced attraction/repulsion strength
                if charge_first == charge_second:
                    # Repulsion - inverted gravity but gentler
                    force = -attraction_factor * GRAVITY_STRENGTH * first.mass * second.mass / (distance * distance + DISTANCE_DAMPING)
                else:
                    # Attraction but weaker than normal gravity
                    force = attraction_factor * GRAVITY_STRENGTH * first.mass * second.mass / (distance * distance + DISTANCE_DAMPING)
                original_angle = angle
                
            elif physics_mode == 1:
                # Orbital dance - perpendicular forces create rotation without attraction
                # Reduced force strength for gentler motion
                dance_strength = 0.15  # Reduced from default
                force = dance_strength * GRAVITY_STRENGTH * first.mass * second.mass / (distance * distance + DISTANCE_DAMPING)
                original_angle = angle
                # Set angle perpendicular to create pure rotation
                angle = angle + math.pi / 2
                
            elif physics_mode == 2:
                # Vibration system - oscillating force based on distance
                # Gentler oscillation with lower amplitude
                frequency = 0.02  # Controls how quickly force oscillates with distance
                oscillation_amplitude = 0.2  # Reduced amplitude
                oscillation = oscillation_amplitude * math.sin(distance * frequency)
                force = GRAVITY_STRENGTH * first.mass * second.mass * oscillation / (distance + DISTANCE_DAMPING)
                original_angle = angle
                
            elif physics_mode == 3:
                # Quantum tunneling - force jumps between attraction and repulsion
                # Use positions to create a deterministic but varied pattern
                position_hash = (hash(str(first.position[0] * 10)) + hash(str(second.position[1] * 10))) % 100
                force_sign = 0.15 if position_hash > 50 else -0.15  # Reduced magnitude
                force = force_sign * GRAVITY_STRENGTH * first.mass * second.mass / (distance * distance + DISTANCE_DAMPING)
                original_angle = angle
                
            elif physics_mode == 4:
                # Choreographed orbits - each body follows a circular pattern
                # No direct force between bodies, just a tendency to move in circular patterns
                force = 0  # No direct force
                original_angle = angle
                
                # This will be handled in the acceleration section with more dance-like movements
                
            elif physics_mode == 5:
                # Spiral dance - bodies spiral outward and then back inward
                # Find center of the system as a reference point
                
                # Calculate distances from center first
                first_dist_from_center = math.sqrt(first.position[0]**2 + first.position[1]**2)
                second_dist_from_center = math.sqrt(second.position[0]**2 + second.position[1]**2)
                
                # Calculate spiral force - varies based on distance from center
                phase_first = (first_dist_from_center / 100) % (2 * math.pi)
                phase_second = (second_dist_from_center / 100) % (2 * math.pi)
                
                # No direct force, we'll apply individual forces in the acceleration section
                force = 0
                original_angle = angle
                
            else:
                # Rhythmic pulsation - bodies periodically attract and repel based on a shared rhythm
                # Using the sum of positions to create a shared rhythm
                position_sum = first.position[0] + first.position[1] + second.position[0] + second.position[1]
                time_factor = pygame.time.get_ticks() / 1000  # Time in seconds
                
                # Create a rhythmic pulsation with period based on position
                rhythm_period = 2 + (position_sum % 3)  # Period between 2-4 seconds
                rhythm_phase = time_factor % rhythm_period / rhythm_period  # 0 to 1
                
                # Force oscillates between attraction and repulsion
                force_scale = 0.2 * math.sin(rhythm_phase * 2 * math.pi)  # -0.2 to 0.2
                force = force_scale * GRAVITY_STRENGTH * first.mass * second.mass / (distance * distance + DISTANCE_DAMPING)
                original_angle = angle
        else:
            # Normal Newtonian physics (inverse square law)
            force = GRAVITY_STRENGTH * first.mass * second.mass / (distance * distance + DISTANCE_DAMPING)
            
        # Apply acceleration to both bodies in opposite directions
        # First body
        acc1 = force / first.mass
        # Limit maximum acceleration for numerical stability
        acc1 = min(acc1, 0.5)  # Reduced for stability
        # Apply time scale to acceleration
        acc1 *= TIME_SCALE
        
        # Apply acceleration in appropriate direction
        if self.alien_physics_enabled:
            if physics_mode == 0:  # Magnetic field
                # Standard direction, but force already accounts for attraction/repulsion
                acc1_x = acc1 * math.cos(angle)
                acc1_y = acc1 * math.sin(angle)
                
            elif physics_mode == 1:  # Orbital dance
                # Pure perpendicular force
                acc1_x = acc1 * math.cos(angle)
                acc1_y = acc1 * math.sin(angle)
                
            elif physics_mode == 2 or physics_mode == 3:  # Vibration or Quantum
                # Use standard direction, force already has sign
                acc1_x = acc1 * math.cos(angle)
                acc1_y = acc1 * math.sin(angle)
                
            elif physics_mode == 4:  # Choreographed orbits
                # Apply a gentle choreographed movement
                # Each body follows a pattern around its current position
                
                # Time-dependent pattern
                time_factor = pygame.time.get_ticks() / 2000  # Slow rotation
                
                # Create a unique pattern factor for this body based on its mass
                pattern_factor = (hash(str(first.mass)) % 5) / 5  # 0 to 0.8 in steps of 0.2
                
                # Calculate pattern movement:
                # 1. Circle pattern with radius proportional to mass
                circle_radius = 0.1 * pattern_factor
                circle_x = circle_radius * math.cos(time_factor + pattern_factor * 2 * math.pi)
                circle_y = circle_radius * math.sin(time_factor + pattern_factor * 2 * math.pi)
                
                # 2. Figure-8 pattern
                figure8_scale = 0.1 * (1 - pattern_factor)
                figure8_x = figure8_scale * math.sin(time_factor * 2)
                figure8_y = figure8_scale * math.sin(time_factor) * math.cos(time_factor)
                
                # Combine patterns
                acc1_x = (circle_x + figure8_x) * TIME_SCALE
                acc1_y = (circle_y + figure8_y) * TIME_SCALE
                    
            elif physics_mode == 5:  # Spiral dance
                # Create spiral-like motion that depends on position
                current_dist = math.sqrt(first.position[0]**2 + first.position[1]**2)
                
                # Angle from center
                center_angle = math.atan2(first.position[1], first.position[0])
                
                # Determine spiral direction based on distance
                # This creates a pattern of spiraling inward when far out and outward when close in
                ideal_dist = 200  # A "comfortable" distance from center
                spiral_strength = 0.08  
                
                # Tangential component (creates spiral)
                tangential_angle = center_angle + math.pi/2
                
                # Radial component (toward or away from center)
                radial_direction = 1 if current_dist < ideal_dist else -1
                radial_strength = min(0.05, abs(current_dist - ideal_dist) / 1000)
                
                # Combined motion
                acc1_x = (spiral_strength * math.cos(tangential_angle) + 
                         radial_direction * radial_strength * math.cos(center_angle)) * TIME_SCALE
                acc1_y = (spiral_strength * math.sin(tangential_angle) + 
                         radial_direction * radial_strength * math.sin(center_angle)) * TIME_SCALE
                
            else:  # Rhythmic pulsation
                # Standard direction with force that changes over time
                acc1_x = acc1 * math.cos(angle)
                acc1_y = acc1 * math.sin(angle)
        else:
            # Standard direction
            acc1_x = acc1 * math.cos(angle)
            acc1_y = acc1 * math.sin(angle)
        
        vx1, vy1 = first.velocity
        first.velocity = (vx1 + acc1_x, vy1 + acc1_y)
        
        # Second body (opposite direction for most physics modes)
        acc2 = force / second.mass
        # Limit maximum acceleration for numerical stability
        acc2 = min(acc2, 0.5)  # Reduced for stability
        # Apply time scale to acceleration
        acc2 *= TIME_SCALE
        
        # Apply acceleration in appropriate direction (opposite of first body in most cases)
        if self.alien_physics_enabled:
            if physics_mode == 0:  # Magnetic field
                # Standard opposite direction, force already accounts for sign
                acc2_x = acc2 * math.cos(angle + math.pi)
                acc2_y = acc2 * math.sin(angle + math.pi)
                
            elif physics_mode == 1:  # Orbital dance
                # Perpendicular force in opposite direction
                acc2_x = acc2 * math.cos(angle + math.pi)
                acc2_y = acc2 * math.sin(angle + math.pi)
                
            elif physics_mode == 2 or physics_mode == 3:  # Vibration or Quantum
                # Use standard direction, force already has sign
                acc2_x = acc2 * math.cos(angle + math.pi)
                acc2_y = acc2 * math.sin(angle + math.pi)
                
            elif physics_mode == 4:  # Choreographed orbits
                # Apply a gentle choreographed movement
                # Similar to first body but with different phase
                
                # Time-dependent pattern
                time_factor = pygame.time.get_ticks() / 2000  # Slow rotation
                
                # Create a unique pattern factor for this body based on its mass
                pattern_factor = (hash(str(second.mass)) % 5) / 5  # 0 to 0.8 in steps of 0.2
                
                # Calculate pattern movement with phase shift:
                # 1. Circle pattern with radius proportional to mass
                circle_radius = 0.1 * pattern_factor
                circle_x = circle_radius * math.cos(time_factor + pattern_factor * 2 * math.pi + math.pi)  # Phase shift
                circle_y = circle_radius * math.sin(time_factor + pattern_factor * 2 * math.pi + math.pi)  # Phase shift
                
                # 2. Figure-8 pattern
                figure8_scale = 0.1 * (1 - pattern_factor)
                figure8_x = figure8_scale * math.sin(time_factor * 2 + math.pi)
                figure8_y = figure8_scale * math.sin(time_factor + math.pi) * math.cos(time_factor + math.pi)
                
                # Combine patterns
                acc2_x = (circle_x + figure8_x) * TIME_SCALE
                acc2_y = (circle_y + figure8_y) * TIME_SCALE
                
            elif physics_mode == 5:  # Spiral dance
                # Create spiral-like motion, similar to first body but with parameter variations
                current_dist = math.sqrt(second.position[0]**2 + second.position[1]**2)
                
                # Angle from center
                center_angle = math.atan2(second.position[1], second.position[0])
                
                # Determine spiral direction based on distance
                ideal_dist = 200  # A "comfortable" distance from center
                spiral_strength = 0.08  
                
                # Tangential component (creates spiral)
                tangential_angle = center_angle + math.pi/2
                
                # Radial component (toward or away from center)
                radial_direction = 1 if current_dist < ideal_dist else -1
                radial_strength = min(0.05, abs(current_dist - ideal_dist) / 1000)
                
                # Combined motion
                acc2_x = (spiral_strength * math.cos(tangential_angle) + 
                         radial_direction * radial_strength * math.cos(center_angle)) * TIME_SCALE
                acc2_y = (spiral_strength * math.sin(tangential_angle) + 
                         radial_direction * radial_strength * math.sin(center_angle)) * TIME_SCALE
                
            else:  # Rhythmic pulsation
                # Standard direction with force that changes over time
                acc2_x = acc2 * math.cos(angle + math.pi)
                acc2_y = acc2 * math.sin(angle + math.pi)
        else:
            # Standard opposite direction
            acc2_x = acc2 * math.cos(angle + math.pi)
            acc2_y = acc2 * math.sin(angle + math.pi)
        
        vx2, vy2 = second.velocity
        second.velocity = (vx2 + acc2_x, vy2 + acc2_y)
        
        # Apply velocity dampening in alien physics mode to prevent objects from flying away
        if self.alien_physics_enabled:
            # Limit maximum velocity for bodies in alien physics mode
            max_velocity = 2.0  # Reduced from 5.0 for tighter containment
            
            # First body velocity limiting
            v1_magnitude = math.sqrt(first.velocity[0]**2 + first.velocity[1]**2)
            if v1_magnitude > max_velocity:
                scale_factor = max_velocity / v1_magnitude
                first.velocity = (first.velocity[0] * scale_factor, first.velocity[1] * scale_factor)
                
            # Second body velocity limiting
            v2_magnitude = math.sqrt(second.velocity[0]**2 + second.velocity[1]**2)
            if v2_magnitude > max_velocity:
                scale_factor = max_velocity / v2_magnitude
                second.velocity = (second.velocity[0] * scale_factor, second.velocity[1] * scale_factor)
                
            # Apply containment force to keep bodies within a reasonable distance from center
            # This creates a "dance floor" effect where bodies can't stray too far
            containment_radius = 500  # Maximum allowed distance from center
            
            # First body containment
            first_dist_from_center = math.sqrt(first.position[0]**2 + first.position[1]**2)
            if first_dist_from_center > containment_radius:
                # Calculate angle from center to body
                angle_to_center = math.atan2(first.position[1], first.position[0])
                
                # Apply inward force proportional to how far beyond the boundary
                beyond_boundary = first_dist_from_center - containment_radius
                containment_force = min(0.2, beyond_boundary / 100)  # Cap at 0.2 for stability
                
                # Add velocity component pointing back toward center
                vx1, vy1 = first.velocity
                first.velocity = (
                    vx1 - containment_force * math.cos(angle_to_center) * TIME_SCALE,
                    vy1 - containment_force * math.sin(angle_to_center) * TIME_SCALE
                )
                
            # Second body containment
            second_dist_from_center = math.sqrt(second.position[0]**2 + second.position[1]**2)
            if second_dist_from_center > containment_radius:
                # Calculate angle from center to body
                angle_to_center = math.atan2(second.position[1], second.position[0])
                
                # Apply inward force proportional to how far beyond the boundary
                beyond_boundary = second_dist_from_center - containment_radius
                containment_force = min(0.2, beyond_boundary / 100)  # Cap at 0.2 for stability
                
                # Add velocity component pointing back toward center
                vx2, vy2 = second.velocity
                second.velocity = (
                    vx2 - containment_force * math.cos(angle_to_center) * TIME_SCALE,
                    vy2 - containment_force * math.sin(angle_to_center) * TIME_SCALE
                )
    
    def check_collision(self, first, second):
        """Check if two bodies have collided."""
        # Skip collision check between two planets or two asteroids
        if (isinstance(first, Planet) and isinstance(second, Planet)) or \
           (isinstance(first, Asteroid) and isinstance(second, Asteroid)):
            return
        
        if first.distance_to(second) < first.display_size/2 + second.display_size/2:
            # Get names for better collision messages
            first_name = self.planet_names.get(first, "unnamed")
            second_name = self.planet_names.get(second, "unnamed")
            
            # Handle sun-planet and sun-asteroid collisions
            if isinstance(first, Sun) and (isinstance(second, Planet) or isinstance(second, Asteroid)):
                message = f"{first_name} destroyed {second_name}!"
                self.add_message(message, (255, 200, 0))  # Yellow-orange for sun destruction
                self.remove_body(second)
            elif isinstance(second, Sun) and (isinstance(first, Planet) or isinstance(first, Asteroid)):
                message = f"{second_name} destroyed {first_name}!"
                self.add_message(message, (255, 200, 0))  # Yellow-orange for sun destruction
                self.remove_body(first)
            # Handle planet-asteroid collisions (asteroid gets absorbed)
            elif isinstance(first, Planet) and isinstance(second, Asteroid):
                message = f"Planet {first_name} absorbed asteroid {second_name}!"
                self.add_message(message, (150, 255, 150))  # Light green for absorption
                self.remove_body(second)
            elif isinstance(first, Asteroid) and isinstance(second, Planet):
                message = f"Planet {second_name} absorbed asteroid {first_name}!"
                self.add_message(message, (150, 255, 150))  # Light green for absorption
                self.remove_body(first)
    
    def handle_all_interactions(self):
        """Handle all gravitational interactions and collisions."""
        # Create a copy to avoid modification during iteration
        bodies = self.bodies.copy()
        
        # First apply gravity between all bodies
        for i, first in enumerate(bodies):
            for second in bodies[i+1:]:
                self.calculate_gravity(first, second)
                self.check_collision(first, second)
        
        # Then apply orbit correction to maintain stable circular orbits
        if self.orbit_correction_enabled:
            sun = None
            for body in bodies:
                if isinstance(body, Sun):
                    sun = body
                    break
            
            if sun:
                for body in bodies:
                    if isinstance(body, Planet) and body in self.initial_distances:
                        # Get the initial distance (ideal orbit)
                        ideal_distance = self.initial_distances[body]
                        
                        # Get current distance from sun
                        current_distance = body.distance_to(sun)
                        
                        # Skip if distances are close enough
                        if abs(current_distance - ideal_distance) < 0.5:
                            continue
                        
                        # Calculate angle to sun
                        angle_to_sun = body.angle_to(sun)
                        
                        # Calculate correction force vector direction
                        # If too close, force should push away from sun
                        # If too far, force should pull toward sun
                        if current_distance < ideal_distance:
                            # Push away from sun
                            correction_angle = angle_to_sun + math.pi
                            # Apply stronger correction when too close to prevent collisions
                            correction_strength = abs(current_distance - ideal_distance) * ORBIT_CORRECTION * 2.0
                        else:
                            # Pull toward sun
                            correction_angle = angle_to_sun
                            correction_strength = abs(current_distance - ideal_distance) * ORBIT_CORRECTION
                        
                        # Apply correction force to velocity
                        vx, vy = body.velocity
                        vx += correction_strength * math.cos(correction_angle) * TIME_SCALE
                        vy += correction_strength * math.sin(correction_angle) * TIME_SCALE
                        body.velocity = (vx, vy)

    def add_message(self, message, color=None):
        """Add a message to the log with an optional color."""
        if color is None:
            color = (255, 255, 255)  # Default to white text
        
        # Add timestamp to message
        timestamp = pygame.time.get_ticks() / 1000  # Time in seconds
        formatted_time = f"{timestamp:.1f}s"
        timestamped_message = f"[{formatted_time}] {message}"
        
        # Add to log with color
        self.message_log.append((timestamped_message, color))
        
        # Trim log if it gets too long
        if len(self.message_log) > self.max_log_messages:
            self.message_log.pop(0)  # Remove oldest message
        
        # Also print to console for debugging
        print(f"LOG: {timestamped_message}")

    def display_message_log(self, surface, font, start_x, start_y):
        """Display the message log on the screen."""
        # Calculate the y-position for the log section header
        header_y = start_y
        
        # Display a header for the log section if there are any messages
        if self.message_log:
            # Create text with transparency
            log_header = font.render("Event Log:", True, (200, 200, 200))
            # Create a surface with per-pixel alpha
            header_surface = pygame.Surface(log_header.get_size(), pygame.SRCALPHA)
            # Set transparency (128 = semi-transparent)
            header_surface.set_alpha(128)
            # Blit the text onto the transparent surface
            header_surface.blit(log_header, (0, 0))
            # Blit the transparent surface onto the main surface
            surface.blit(header_surface, (start_x, header_y))
            
            # Start displaying messages below the header
            message_y = header_y + 25
            
            # Display each message with its color
            for message, color in self.message_log:
                # Create text with the specified color
                message_display = font.render(message, True, color)
                # Create a surface with per-pixel alpha
                message_surface = pygame.Surface(message_display.get_size(), pygame.SRCALPHA)
                # Set transparency (128 = semi-transparent)
                message_surface.set_alpha(128)
                # Blit the text onto the transparent surface
                message_surface.blit(message_display, (0, 0))
                # Blit the transparent surface onto the main surface
                surface.blit(message_surface, (start_x, message_y))
                message_y += 20  # Spacing between messages

def add_random_planet(solar_system, pos):
    """Add a planet at the given position with appropriate velocity and a random name."""
    x, y = pos
    # Convert to coordinates relative to center
    x -= WIDTH // 2
    y -= HEIGHT // 2
    
    # Calculate distance from center
    distance = math.sqrt(x*x + y*y)
    
    # Enforce minimum distance from sun
    if distance < 70:  # Reduced from 100 to match new scale
        # Too close to center - place it at minimum distance in same direction
        angle = math.atan2(y, x)
        distance = 70
        x = math.cos(angle) * distance
        y = math.sin(angle) * distance
    
    # Find the sun to calculate appropriate orbital velocity
    sun = None
    for body in solar_system.bodies:
        if isinstance(body, Sun):
            sun = body
            break
    
    if sun:
        # Calculate velocity based on Kepler's laws for a circular orbit
        # Apply the same scaling factors as the main planets
        orbital_speed_factor = 0.7
        
        # Reduce velocity for planets closer to the sun
        if distance < 300:
            orbital_speed_factor = 0.65
            
        orbital_speed = math.sqrt(sun.mass / distance) * orbital_speed_factor
        
        # Calculate velocity perpendicular to radius vector for circular orbit
        # We normalize the (x,y) vector to get the direction, then rotate 90 degrees
        # Rotating (x,y) by 90 degrees gives (-y,x) when normalized
        vx = -y / distance * orbital_speed
        vy = x / distance * orbital_speed
    else:
        # Fallback if no sun is found (should not happen)
        orbital_speed = 2.0  # Reduced from 2.5
        vx = -y / distance * orbital_speed
        vy = x / distance * orbital_speed
    
    # Random mass between 1 and 2 (smaller range for stability)
    mass = random.uniform(1, 2)
    
    # Create and add the planet
    planet = Planet(mass, (x, y), (vx, vy))
    # Set a smaller size for user-added planets
    planet.display_size = 3
    
    # Generate random name
    planet_name = generate_random_planet_name()
    
    # Add the planet to the system and log the event
    solar_system.add_body(planet, planet_name)
    solar_system.add_message(f"New planet {planet_name} added at distance {distance:.1f}", (100, 200, 255))
    
    return planet, planet_name

def add_elliptical_asteroid(solar_system, min_distance, max_distance, eccentricity=None):
    """Add an asteroid with an elliptical orbit between min and max distance from the sun."""
    # Find the sun
    sun = None
    for body in solar_system.bodies:
        if isinstance(body, Sun):
            sun = body
            break
    
    if not sun:
        print("Cannot add asteroid: No sun found in the solar system")
        return
    
    # Random distance within the specified range
    distance = random.uniform(min_distance, max_distance)
    
    # Random angle for position
    angle = random.uniform(0, 2 * math.pi)
    x = math.cos(angle) * distance
    y = math.sin(angle) * distance
    
    # Calculate base orbital velocity for a circular orbit
    orbital_speed = math.sqrt(sun.mass / distance) * 0.7
    
    # Generate random eccentricity if not specified
    if eccentricity is None:
        eccentricity = random.uniform(0.2, 0.7)  # Higher values = more elliptical
    
    # Modify velocity direction to create an elliptical orbit
    # For an elliptical orbit, we add a radial component to the velocity
    tangent_angle = angle + math.pi/2  # Perpendicular to radius (for circular orbit)
    
    # Adjust the velocity angle based on eccentricity
    # This creates a velocity that's not perfectly perpendicular to radius vector
    velocity_angle = tangent_angle + (random.choice([-1, 1]) * eccentricity * math.pi/4)
    
    # Calculate velocity components
    vx = math.cos(velocity_angle) * orbital_speed
    vy = math.sin(velocity_angle) * orbital_speed
    
    # Generate a small random mass for the asteroid
    mass = random.uniform(0.01, 0.1)
    
    # Create and add the asteroid
    asteroid = Asteroid(mass, (x, y), (vx, vy), eccentricity)
    
    # Asteroids are small, so set a fixed small size
    asteroid.display_size = random.randint(1, 3)
    
    # Generate a name for the asteroid
    asteroid_name = generate_random_asteroid_name()
    
    # Add to solar system and log the event
    solar_system.add_body(asteroid, asteroid_name)
    solar_system.add_message(f"New asteroid {asteroid_name} added, eccentricity: {eccentricity:.2f}", (200, 200, 200))
    
    return asteroid, asteroid_name

def main():
    # Create solar system
    solar_system = SolarSystem()
    
    # Add welcome messages
    solar_system.add_message("Welcome to the Solar System Simulator!", (255, 255, 100))
    solar_system.add_message("Click: Add planet | ESC: Quit | O: Toggle orbits | C: Toggle orbit correction", (200, 200, 200))
    solar_system.add_message("P: Toggle alien physics | A: Add asteroid | +/-: Change speed | S: Reset speed | T: Toggle trails", (200, 200, 200))
    
    # Create the sun at the center
    sun = Sun(10000)  # Large mass for stable orbits
    sun.display_size = 50  # Fixed display size for sun
    solar_system.add_body(sun, "Sun")
    solar_system.add_message("Sun created at the center", (255, 200, 0))
    
    # Scale down the distance values to fit all planets on screen
    # Maintain the same relative distances between planets but reduce absolute distances
    
    # Define planet data for our solar system with improved spacing
    # Format: name, distance from sun, mass, color, size_scale, has_rings
    # Using a more logarithmic scale for distances to better represent the solar system
    planets_data = [
        # Name       Distance  Mass    Color           Size Scale  Rings
        ("Mercury",  80,       0.055,  MERCURY_COLOR,  0.38,       False),
        ("Venus",    120,      0.815,  VENUS_COLOR,    0.95,       False),
        ("Earth",    160,      1.0,    EARTH_COLOR,    1.0,        False),
        ("Mars",     200,      0.107,  MARS_COLOR,     0.53,       False),
        ("Jupiter",  280,      317.8,  JUPITER_COLOR,  11.2,       False),
        ("Saturn",   350,      95.2,   SATURN_COLOR,   9.45,       True),
        ("Uranus",   420,      14.6,   URANUS_COLOR,   4.0,        False),
        ("Neptune",  480,      17.2,   NEPTUNE_COLOR,  3.88,       False)
    ]
    
    # Base size for Earth - everything else will be relative to this
    base_earth_size = 8
    
    # Add the planets
    for name, distance, relative_mass, color, size_scale, has_rings in planets_data:
        # Distribute planets evenly around the sun rather than random positions
        # This creates a more balanced system and better visualization
        if name == "Mercury":
            angle = 0
        elif name == "Venus":
            angle = math.pi / 4  # 45 degrees
        elif name == "Earth":
            angle = math.pi / 2  # 90 degrees
        elif name == "Mars":
            angle = 3 * math.pi / 4  # 135 degrees
        elif name == "Jupiter":
            angle = math.pi  # 180 degrees
        elif name == "Saturn":
            angle = 5 * math.pi / 4  # 225 degrees
        elif name == "Uranus":
            angle = 3 * math.pi / 2  # 270 degrees
        elif name == "Neptune":
            angle = 7 * math.pi / 4  # 315 degrees
        else:
            angle = random.uniform(0, 2 * math.pi)
            
        x = math.cos(angle) * distance
        y = math.sin(angle) * distance
        
        # Calculate orbital velocity based on Kepler's laws
        # Scale mass appropriately - smaller planets need relatively
        # larger masses to be visible, so we use a logarithmic scale
        mass = 1.0 + math.log(1 + relative_mass) * 2
        
        # v = sqrt(GM/r) where G is absorbed into the sun's mass
        # Improved orbital speed calculation for better stability
        # Additional scaling factor for distance to ensure stable orbits
        orbital_speed_factor = 0.7
        
        # Reduce velocity slightly for planets closer to the sun for more stability
        if distance < 300:
            orbital_speed_factor = 0.65
            
        orbital_speed = math.sqrt(sun.mass / distance) * orbital_speed_factor
        
        # Velocity perpendicular to radius vector (for circular orbit)
        vx = -y / distance * orbital_speed 
        vy = x / distance * orbital_speed
        
        # Create the planet - pass the size_scale and rings info
        planet = Planet(mass, (x, y), (vx, vy), color, has_rings)
        
        # Directly set the display size based on Earth's base size and the relative scale
        # This gives us better control over planet sizes
        planet.display_size = max(int(base_earth_size * size_scale * 0.15), 2)
        
        # Reduce Jupiter and Saturn further
        if name in ["Jupiter", "Saturn"]:
            planet.display_size = int(planet.display_size * 0.5)
        
        solar_system.add_body(planet, name)
        
        # Debug info
        print(f"Added {name}: distance={distance}, mass={mass}, size={planet.display_size}, orbital speed={orbital_speed:.2f}")
    
    # Add just 2 asteroids instead of a full belt
    print("\n# Adding initial asteroids:")
    # One medium elliptical asteroid
    add_elliptical_asteroid(solar_system, 200, 250, 0.4)
    # One highly elliptical asteroid
    add_elliptical_asteroid(solar_system, 180, 300, 0.7)
    
    # Add one random planet in a stable orbit
    print("\n# Adding initial random planet:")
    # Create a random planet at a safe distance with stable orbital properties
    random_distance = random.uniform(220, 300)
    angle = random.uniform(0, 2 * math.pi)
    x = math.cos(angle) * random_distance
    y = math.sin(angle) * random_distance
    
    # Calculate proper orbital velocity for stability
    orbital_speed_factor = 0.7
    orbital_speed = math.sqrt(sun.mass / random_distance) * orbital_speed_factor
    
    # Velocity perpendicular to radius for circular orbit
    vx = -y / random_distance * orbital_speed 
    vy = x / random_distance * orbital_speed
    
    # Create planet with random properties
    mass = random.uniform(1, 3)
    planet = Planet(mass, (x, y), (vx, vy))
    
    # Generate and assign random name
    planet_name = generate_random_planet_name()
    print(f"Added random planet: {planet_name} at distance {random_distance:.1f}")
    
    solar_system.add_body(planet, planet_name)
    
    # Add font for instructions
    font = pygame.font.SysFont('Arial', 18)
    
    # Global for time scale
    global TIME_SCALE
    
    # Main loop
    running = True
    while running:
        screen.fill(BLACK)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_o:  # Toggle orbits with 'o' key
                    solar_system.show_orbits = not solar_system.show_orbits
                    status = 'Enabled' if solar_system.show_orbits else 'Disabled'
                    solar_system.add_message(f"Orbit display: {status}", (150, 150, 150))
                    print(f"Orbit display: {status}")
                elif event.key == pygame.K_t:  # Toggle trails with 't' key
                    solar_system.show_trails = not solar_system.show_trails
                    status = 'Enabled' if solar_system.show_trails else 'Disabled'
                    solar_system.add_message(f"Orbit trails: {status}", (150, 150, 150))
                    print(f"Orbit trails display: {status}")
                elif event.key == pygame.K_c:  # Toggle orbit correction with 'c' key
                    solar_system.orbit_correction_enabled = not solar_system.orbit_correction_enabled
                    status = 'Enabled' if solar_system.orbit_correction_enabled else 'Disabled'
                    solar_system.add_message(f"Orbit correction: {status}", (150, 150, 150))
                    print(f"Orbit correction: {status}")
                elif event.key == pygame.K_p:  # Toggle alien physics with 'p' key
                    solar_system.alien_physics_enabled = not solar_system.alien_physics_enabled
                    status = 'Enabled' if solar_system.alien_physics_enabled else 'Disabled'
                    
                    # If enabling alien physics, disable orbit correction for more interesting effects
                    if solar_system.alien_physics_enabled:
                        solar_system.orbit_correction_enabled = False
                        solar_system.add_message(f"Alien physics: {status} (orbit correction disabled)", (180, 100, 255))
                    else:
                        solar_system.add_message(f"Alien physics: {status}", (150, 150, 150))
                    
                    print(f"Alien physics: {status}")
                elif event.key == pygame.K_PLUS or event.key == pygame.K_KP_PLUS or event.key == pygame.K_EQUALS:
                    # Increase speed - use larger multiplier at higher speeds
                    if TIME_SCALE < 1.0:
                        TIME_SCALE *= 1.25  # Gentle increase at lower speeds
                    elif TIME_SCALE < 10.0:
                        TIME_SCALE *= 1.5   # Medium increase for moderate speeds
                    else:
                        TIME_SCALE *= 2.0   # Double the speed for high speeds
                    
                    solar_system.add_message(f"Speed increased to {TIME_SCALE:.2f}x", (255, 255, 255))
                    print(f"Speed: {TIME_SCALE:.2f}x")
                elif event.key == pygame.K_MINUS or event.key == pygame.K_KP_MINUS:
                    # Decrease speed - use appropriate scaling based on current speed
                    if TIME_SCALE > 10.0:
                        TIME_SCALE *= 0.5   # Halve the speed for high speeds
                    elif TIME_SCALE > 1.0:
                        TIME_SCALE *= 0.67  # Medium decrease for moderate speeds
                    else:
                        TIME_SCALE *= 0.8   # Gentle decrease at lower speeds
                    
                    # Ensure minimum speed
                    TIME_SCALE = max(TIME_SCALE, 0.01)
                    
                    solar_system.add_message(f"Speed decreased to {TIME_SCALE:.2f}x", (255, 255, 255))
                    print(f"Speed: {TIME_SCALE:.2f}x")
                elif event.key == pygame.K_s:  # 'S' key to reset speed to normal
                    TIME_SCALE = 1.0
                    solar_system.add_message("Speed reset to 1.00x (normal)", (255, 255, 255))
                    print(f"Speed reset to {TIME_SCALE:.2f}x (normal)")
                elif event.key == pygame.K_a:  # 'A' key to add random asteroid
                    # Add a random asteroid with elliptical orbit
                    min_distance = 120  # Min distance from sun
                    max_distance = 400  # Max distance from sun
                    add_elliptical_asteroid(solar_system, min_distance, max_distance)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    add_random_planet(solar_system, event.pos)
        
        # Calculate physics
        solar_system.handle_all_interactions()
        
        # Update and draw
        solar_system.update_all(screen)
        
        # Draw instructions (split into two lines)
        instruction_text1 = font.render("Click: Add planet | ESC: Quit | O: Toggle orbits | C: Toggle orbit correction", True, (200, 200, 200))
        instruction_text2 = font.render("P: Toggle alien physics | A: Add asteroid | +/-: Change speed | S: Reset speed | T: Toggle trails", True, (200, 200, 200))
        
        # Create transparent surfaces
        text_surface1 = pygame.Surface(instruction_text1.get_size(), pygame.SRCALPHA)
        text_surface1.set_alpha(128)
        text_surface1.blit(instruction_text1, (0, 0))
        
        text_surface2 = pygame.Surface(instruction_text2.get_size(), pygame.SRCALPHA)
        text_surface2.set_alpha(128)
        text_surface2.blit(instruction_text2, (0, 0))
        
        # Blit the transparent surfaces
        screen.blit(text_surface1, (10, 10))
        screen.blit(text_surface2, (10, 35))
        
        # Display current speed with appropriate formatting for large values
        speed_text = ""
        if TIME_SCALE < 5:
            speed_text = f"Speed: {TIME_SCALE:.2f}x"
            speed_color = (255, 255, 255)
        elif TIME_SCALE < 10:
            speed_text = f"Speed: {TIME_SCALE:.2f}x"
            speed_color = (255, 150, 0)
        else:
            speed_text = f"Speed: {TIME_SCALE:.2f}x"
            speed_color = (255, 50, 50)
        
        # Create transparent speed display
        speed_display = font.render(speed_text, True, speed_color)
        speed_surface = pygame.Surface(speed_display.get_size(), pygame.SRCALPHA)
        speed_surface.set_alpha(128)
        speed_surface.blit(speed_display, (0, 0))
        screen.blit(speed_surface, (10, 60))
        
        # Display orbit correction status
        orbit_correction_text = f"Orbit Correction: {'On' if solar_system.orbit_correction_enabled else 'Off'}"
        orbit_correction_color = (0, 255, 0) if solar_system.orbit_correction_enabled else (255, 50, 50)
        
        # Create transparent orbit correction display
        orbit_correction_display = font.render(orbit_correction_text, True, orbit_correction_color)
        orbit_surface = pygame.Surface(orbit_correction_display.get_size(), pygame.SRCALPHA)
        orbit_surface.set_alpha(128)
        orbit_surface.blit(orbit_correction_display, (0, 0))
        screen.blit(orbit_surface, (10, 85))
        
        # Display orbit trails status
        trails_text = f"Orbit Trails: {'On' if solar_system.show_trails else 'Off'}"
        trails_color = (0, 255, 0) if solar_system.show_trails else (255, 50, 50)
        
        # Create transparent trails display
        trails_display = font.render(trails_text, True, trails_color)
        trails_surface = pygame.Surface(trails_display.get_size(), pygame.SRCALPHA)
        trails_surface.set_alpha(128)
        trails_surface.blit(trails_display, (0, 0))
        screen.blit(trails_surface, (10, 110))
        
        # Display alien physics status
        alien_text = f"Alien Physics: {'On' if solar_system.alien_physics_enabled else 'Off'}"
        alien_color = (180, 100, 255) if solar_system.alien_physics_enabled else (255, 50, 50)
        
        # Create transparent alien physics display
        alien_display = font.render(alien_text, True, alien_color)
        alien_surface = pygame.Surface(alien_display.get_size(), pygame.SRCALPHA)
        alien_surface.set_alpha(128)
        alien_surface.blit(alien_display, (0, 0))
        screen.blit(alien_surface, (10, 135))
        
        # Display active physics modes if alien physics is enabled
        if solar_system.alien_physics_enabled:
            # Add explanation of alien physics
            explanation_text = "Alien physics oscillates between modes every 10 seconds"
            explanation_display = font.render(explanation_text, True, (150, 150, 150))
            explanation_surface = pygame.Surface(explanation_display.get_size(), pygame.SRCALPHA)
            explanation_surface.set_alpha(128)
            explanation_surface.blit(explanation_display, (0, 0))
            screen.blit(explanation_surface, (10, 180))
            
            mode_names = [
                "Magnetic Ballet",
                "Orbital Waltz",
                "Vibration Samba",
                "Quantum Tango",
                "Choreographed Orbits",
                "Spiral Dance",
                "Rhythmic Pulsation"
            ]
            
            # Display currently active mode
            current_mode = solar_system.current_physics_mode
            current_mode_name = mode_names[current_mode]
            
            # Calculate time remaining in current mode
            mode_duration = 10  # seconds (must match the value in calculate_gravity)
            time_seconds = pygame.time.get_ticks() / 1000
            time_in_current_mode = time_seconds % mode_duration
            time_remaining = mode_duration - time_in_current_mode
            
            # Display current mode with time remaining
            mode_colors = [
                (255, 100, 100),  # Red for magnetic ballet
                (100, 255, 100),  # Green for orbital waltz
                (100, 100, 255),  # Blue for vibration samba
                (255, 255, 100),  # Yellow for quantum tango
                (255, 100, 255),  # Magenta for choreographed orbits
                (255, 100, 100),  # Red for spiral dance
                (100, 100, 255)   # Blue for rhythmic pulsation
            ]
            
            mode_text = f"Current Mode: {current_mode_name} ({time_remaining:.1f}s remaining)"
            mode_color = mode_colors[current_mode]
            
            # Create transparent mode display
            mode_display = font.render(mode_text, True, mode_color)
            mode_surface = pygame.Surface(mode_display.get_size(), pygame.SRCALPHA)
            mode_surface.set_alpha(128)
            mode_surface.blit(mode_display, (0, 0))
            screen.blit(mode_surface, (10, 205))  # Adjust position
            
            # Display next mode
            next_mode = (current_mode + 1) % 7
            next_mode_name = mode_names[next_mode]
            next_mode_text = f"Next Mode: {next_mode_name}"
            
            # Create transparent next mode display
            next_mode_display = font.render(next_mode_text, True, (180, 180, 180))
            next_mode_surface = pygame.Surface(next_mode_display.get_size(), pygame.SRCALPHA)
            next_mode_surface.set_alpha(128)
            next_mode_surface.blit(next_mode_display, (0, 0))
            screen.blit(next_mode_surface, (10, 235))  # Adjust position
        
        # Display message log in the bottom left corner
        solar_system.display_message_log(screen, font, 10, HEIGHT - 150)
        
        # Update display
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main() 
