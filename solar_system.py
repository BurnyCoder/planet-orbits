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

# Colors
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)

# Planet colors
PLANET_COLORS = [RED, GREEN, BLUE]

# Clock for controlling frame rate
clock = pygame.time.Clock()
FPS = 60

class Body:
    """Base class for all celestial bodies."""
    min_display_size = 10
    display_log_base = 1.1
    
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
        """Update position based on velocity."""
        x, y = self.position
        vx, vy = self.velocity
        self.position = (x + vx, y + vy)
    
    def draw(self, surface):
        """Draw the body on the given surface."""
        x, y = self.position
        pygame.draw.circle(surface, self.color, 
                          (int(x + WIDTH // 2), int(y + HEIGHT // 2)), 
                          self.display_size)
    
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
    def __init__(self, mass, position=(0, 0), velocity=(0, 0)):
        color = random.choice(PLANET_COLORS)
        super().__init__(mass, position, velocity, color)

class SolarSystem:
    """Manages all the bodies in the solar system and their interactions."""
    def __init__(self):
        self.bodies = []
    
    def add_body(self, body):
        """Add a body to the solar system."""
        self.bodies.append(body)
    
    def remove_body(self, body):
        """Remove a body from the solar system."""
        if body in self.bodies:
            self.bodies.remove(body)
    
    def update_all(self, surface):
        """Update and draw all bodies."""
        for body in self.bodies:
            body.move()
            body.draw(surface)
    
    def calculate_gravity(self, first, second):
        """Calculate gravitational effect between two bodies."""
        # Skip if the bodies are too close to avoid division by zero
        distance = first.distance_to(second)
        if distance < 1:
            return
        
        # Calculate force based on masses and distance
        force = first.mass * second.mass / (distance * distance)
        angle = first.angle_to(second)
        
        # Apply acceleration to both bodies in opposite directions
        # First body
        acc1 = force / first.mass
        acc1_x = acc1 * math.cos(angle)
        acc1_y = acc1 * math.sin(angle)
        vx1, vy1 = first.velocity
        first.velocity = (vx1 + acc1_x, vy1 + acc1_y)
        
        # Second body (opposite direction)
        acc2 = force / second.mass
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
        for i, first in enumerate(bodies):
            for second in bodies[i+1:]:
                self.calculate_gravity(first, second)
                self.check_collision(first, second)

def add_random_planet(solar_system, pos):
    """Add a planet at the given position with appropriate velocity."""
    x, y = pos
    # Convert to coordinates relative to center
    x -= WIDTH // 2
    y -= HEIGHT // 2
    
    # Calculate distance from center
    distance = math.sqrt(x*x + y*y)
    if distance < 50:  # Too close to center
        return
    
    # Calculate velocity perpendicular to radius for stable orbit
    speed = 6  # Adjust for different orbital behavior
    vx = y / distance * speed
    vy = -x / distance * speed
    
    # Random mass between 1 and 3
    mass = random.uniform(1, 3)
    
    # Create and add the planet
    planet = Planet(mass, (x, y), (vx, vy))
    solar_system.add_body(planet)

def main():
    # Create solar system
    solar_system = SolarSystem()
    
    # Add sun at the center
    sun = Sun(10000)
    solar_system.add_body(sun)
    
    # Add some initial planets
    for _ in range(4):
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(200, 400)
        x = math.cos(angle) * distance
        y = math.sin(angle) * distance
        
        # Calculate orbit velocity (perpendicular to radius)
        speed = math.sqrt(sun.mass / distance) * 0.7  # Adjusted for stability
        vx = math.sin(angle) * speed
        vy = -math.cos(angle) * speed
        
        planet = Planet(random.uniform(1, 5), (x, y), (vx, vy))
        solar_system.add_body(planet)
    
    # Add font for instructions
    font = pygame.font.SysFont('Arial', 18)
    instruction_text = font.render('Click to add planets | ESC to quit', True, WHITE)
    
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
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    add_random_planet(solar_system, event.pos)
        
        # Calculate physics
        solar_system.handle_all_interactions()
        
        # Update and draw
        solar_system.update_all(screen)
        
        # Draw instructions
        screen.blit(instruction_text, (10, 10))
        
        # Update display
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main() 