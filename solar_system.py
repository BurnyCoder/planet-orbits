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

# Clock for controlling frame rate
clock = pygame.time.Clock()
FPS = 60

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
        if body in self.bodies:
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
        if first.distance_to(second) < first.display_size/2 + second.display_size/2:
            # Only remove planets, not suns
            if isinstance(first, Planet) and not isinstance(second, Planet):
                self.remove_body(first)
            elif isinstance(second, Planet) and not isinstance(first, Planet):
                self.remove_body(second)
    
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
    """Add a planet at the given position with appropriate velocity."""
    x, y = pos
    # Convert to coordinates relative to center
    x -= WIDTH // 2
    y -= HEIGHT // 2
    
    # Calculate distance from center
    distance = math.sqrt(x*x + y*y)
    
    # Enforce minimum distance from sun
    if distance < 100:  # Increased from 50
        # Too close to center - place it at minimum distance in same direction
        angle = math.atan2(y, x)
        distance = 100
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
    solar_system.add_body(planet)

def main():
    # Create solar system
    solar_system = SolarSystem()
    
    # Add sun at the center - make the sun smaller
    sun = Sun(10000)
    sun.display_size = 50  # Fixed size for sun
    solar_system.add_body(sun, "Sun")
    
    # Define planet data for our solar system with improved spacing
    # Format: name, distance from sun, mass, color, size_scale, has_rings
    # Distances are increased to provide more space between planets
    # Using a more logarithmic scale for distances to better represent the solar system
    planets_data = [
        # Name       Distance  Mass    Color           Size Scale  Rings
        ("Mercury",  120,      0.055,  MERCURY_COLOR,  0.38,       False),
        ("Venus",    180,      0.815,  VENUS_COLOR,    0.95,       False),
        ("Earth",    250,      1.0,    EARTH_COLOR,    1.0,        False),
        ("Mars",     320,      0.107,  MARS_COLOR,     0.53,       False),
        ("Jupiter",  450,      317.8,  JUPITER_COLOR,  11.2,       False),
        ("Saturn",   550,      95.2,   SATURN_COLOR,   9.45,       True),
        ("Uranus",   650,      14.6,   URANUS_COLOR,   4.0,        False),
        ("Neptune",  750,      17.2,   NEPTUNE_COLOR,  3.88,       False)
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
    
    # Add font for instructions
    font = pygame.font.SysFont('Arial', 18)
    instruction_text = font.render('Click to add planets | ESC to quit | O to toggle orbits | +/- to change speed', True, WHITE)
    
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