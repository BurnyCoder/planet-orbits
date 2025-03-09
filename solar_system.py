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

# Colors
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)

# Planet colors (more realistic)
MERCURY_COLOR = (169, 169, 169)  # Gray
VENUS_COLOR = (244, 226, 181)    # Pale yellow/cream
EARTH_COLOR = (0, 128, 255)      # Blue
MARS_COLOR = (188, 39, 50)       # Red-brown
JUPITER_COLOR = (255, 196, 148)  # Light orange
SATURN_COLOR = (236, 205, 151)   # Pale gold
URANUS_COLOR = (172, 230, 236)   # Pale cyan
NEPTUNE_COLOR = (41, 95, 153)    # Deep blue

# Planet colors for random planets
PLANET_COLORS = [RED, GREEN, BLUE]

# Colors for celestial bodies
ASTEROID_COLOR_BASE = (150, 140, 120)  # Brownish-gray
ASTEROID_BELT_COLOR = (100, 100, 100)  # Dark gray for orbit paths

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
        self.planet_trails = {}  # Dictionary to store planet trail points
        self.initial_distances = {}  # Store initial distances from sun for orbit correction
    
    def add_body(self, body, name=None):
        """Add a body to the solar system."""
        self.bodies.append(body)
        if name:
            self.planet_names[body] = name
            # Initialize empty trail for the planet
            if isinstance(body, Planet):
                self.planet_trails[body] = []
                
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
        # Print information about the destroyed body
        body_type = "Unknown"
        if isinstance(body, Planet):
            body_type = "Planet"
        elif isinstance(body, Asteroid):
            body_type = "Asteroid"
        elif isinstance(body, Sun):
            body_type = "Sun"
            
        # Get the body name if it exists
        name = self.planet_names.get(body, "unnamed")
        
        print(f"🔥 {body_type} {name} was destroyed!")
        
        # Remove from planet names dictionary
        if body in self.planet_names:
            self.planet_names.pop(body)
            
        # Remove from trails dictionary
        if body in self.planet_trails:
            self.planet_trails.pop(body)
            
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
        
        # Update and draw all planets
        for body in self.bodies:
            # Update position
            body.move()
            
            # Record trail for planets
            if body in self.planet_trails:
                # Add current position to trail
                x, y = body.position
                screen_x = int(x + WIDTH // 2)
                screen_y = int(y + HEIGHT // 2)
                self.planet_trails[body].append((screen_x, screen_y))
                
                # Limit trail length
                max_trail_length = 50
                if len(self.planet_trails[body]) > max_trail_length:
                    self.planet_trails[body] = self.planet_trails[body][-max_trail_length:]
            
            # Draw body
            body.draw(surface)
            
            # If the body has a name, display it
            if body in self.planet_names:
                x, y = body.position
                screen_x = int(x + WIDTH // 2)
                screen_y = int(y + HEIGHT // 2)
                
                # Create a small font for the planet names
                font = pygame.font.SysFont('Arial', 12)
                # Render the name in white
                text = font.render(self.planet_names[body], True, WHITE)
                # Position the text just above the planet
                text_rect = text.get_rect(center=(screen_x, screen_y - body.display_size - 5))
                surface.blit(text, text_rect)
    
    def calculate_gravity(self, first, second):
        """Calculate gravitational effect between two bodies."""
        # Skip if the bodies are too close to avoid division by zero
        distance = first.distance_to(second)
        if distance < 1:
            return
        
        # Calculate force based on masses and distance with additional damping
        # Adding larger damping factor to prevent extreme forces at very close distances
        force = GRAVITY_STRENGTH * first.mass * second.mass / (distance * distance + DISTANCE_DAMPING)
        angle = first.angle_to(second)
        
        # Apply acceleration to both bodies in opposite directions
        # First body
        acc1 = force / first.mass
        # Limit maximum acceleration for numerical stability
        acc1 = min(acc1, 0.5)  # Reduced from 2.0
        # Apply time scale to acceleration
        acc1 *= TIME_SCALE
        acc1_x = acc1 * math.cos(angle)
        acc1_y = acc1 * math.sin(angle)
        vx1, vy1 = first.velocity
        first.velocity = (vx1 + acc1_x, vy1 + acc1_y)
        
        # Second body (opposite direction)
        acc2 = force / second.mass
        # Limit maximum acceleration for numerical stability
        acc2 = min(acc2, 0.5)  # Reduced from 2.0
        # Apply time scale to acceleration
        acc2 *= TIME_SCALE
        acc2_x = acc2 * math.cos(angle + math.pi)  # Opposite direction
        acc2_y = acc2 * math.sin(angle + math.pi)  # Opposite direction
        vx2, vy2 = second.velocity
        second.velocity = (vx2 + acc2_x, vy2 + acc2_y)
    
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
                print(f"⚡ Collision detected: {first_name} destroyed {second_name}!")
                self.remove_body(second)
            elif isinstance(second, Sun) and (isinstance(first, Planet) or isinstance(first, Asteroid)):
                print(f"⚡ Collision detected: {second_name} destroyed {first_name}!")
                self.remove_body(first)
            # Handle planet-asteroid collisions (asteroid gets absorbed)
            elif isinstance(first, Planet) and isinstance(second, Asteroid):
                print(f"💥 Collision detected: Planet {first_name} absorbed asteroid {second_name}!")
                self.remove_body(second)
            elif isinstance(first, Asteroid) and isinstance(second, Planet):
                print(f"💥 Collision detected: Planet {second_name} absorbed asteroid {first_name}!")
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
    
    # Generate and assign a random name to the planet
    planet_name = generate_random_planet_name()
    print(f"Added new planet: {planet_name}")
    
    solar_system.add_body(planet, planet_name)

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
    print(f"Added asteroid: {asteroid_name}, eccentricity: {eccentricity:.2f}")
    
    solar_system.add_body(asteroid, asteroid_name)
    return asteroid

def main():
    # Create solar system
    solar_system = SolarSystem()
    
    # Add sun at the center - make the sun smaller
    sun = Sun(10000)
    sun.display_size = 50  # Fixed size for sun
    solar_system.add_body(sun, "Sun")
    
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
    
    # Add asteroid belt between Mars and Jupiter
    num_asteroids = 15  # Number of asteroids to add
    for _ in range(num_asteroids):
        # Asteroid belt is roughly between Mars and Jupiter
        add_elliptical_asteroid(solar_system, 220, 260, None)
    
    # Add some outlier asteroids with more extreme elliptical orbits
    add_elliptical_asteroid(solar_system, 180, 300, 0.6)  # Highly elliptical
    add_elliptical_asteroid(solar_system, 150, 350, 0.7)  # Very elliptical
    
    # Add font for instructions
    font = pygame.font.SysFont('Arial', 18)
    instruction_text = font.render('Click to add planets | ESC to quit | O to toggle orbits | +/- to change speed | A to add asteroid', True, WHITE)
    
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
                elif event.key == pygame.K_PLUS or event.key == pygame.K_KP_PLUS or event.key == pygame.K_EQUALS:
                    # Increase speed
                    TIME_SCALE = min(TIME_SCALE * 1.25, 2.0)
                    print(f"Speed: {TIME_SCALE:.2f}x")
                elif event.key == pygame.K_MINUS or event.key == pygame.K_KP_MINUS:
                    # Decrease speed
                    TIME_SCALE = max(TIME_SCALE * 0.8, 0.01)
                    print(f"Speed: {TIME_SCALE:.2f}x")
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
        
        # Draw instructions
        screen.blit(instruction_text, (10, 10))
        
        # Display current speed
        speed_text = font.render(f"Speed: {TIME_SCALE:.2f}x", True, WHITE)
        screen.blit(speed_text, (10, 40))
        
        # Update display
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main() 