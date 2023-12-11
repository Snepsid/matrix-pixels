import pygame
import random
import math

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 27, 27
PIXEL_SIZE = 10
SCREEN_WIDTH = WIDTH * PIXEL_SIZE
SCREEN_HEIGHT = HEIGHT * PIXEL_SIZE
MIN_COLUMN_HEIGHT = 3  # Minimum number of "pixels" in a column
MAX_COLUMN_HEIGHT = 27  # Maximum number of "pixels" in a column

# Colors
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 5, 0)

# Initialize screen and clock
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Selective Bottom Pixel Pulsing")
clock = pygame.time.Clock()

def get_gradient_color(start_color, end_color, ratio, pulse_phase=None):
    """Return a color that's a blend between start_color and end_color based on the ratio, with some random variation."""
    base_color = tuple([
        int(start_color[i] + ratio * (end_color[i] - start_color[i]))
        for i in range(3)
    ])
    
    # Apply pulsing effect using pulse_phase for independent pulsing if provided
    if pulse_phase:
        pulse_intensity = (math.sin(pygame.time.get_ticks() * 0.1 + pulse_phase) ** 8)  # Sharp sinusoidal pulse
        base_color = (int(base_color[0] + pulse_intensity * 200), int(base_color[1] + pulse_intensity * 200), int(base_color[2] + pulse_intensity * 200))
    
    # Apply random variation within a ±20% range, but ensure it remains within [0, 255]
    return tuple([
        min(255, max(0, base_color[i] + random.randint(-int(0.2 * base_color[i]), int(0.2 * base_color[i]))))
        for i in range(3)
    ])

class StuckPixel:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.stuck_duration = random.randint(5, 15)
        self.fade_timer = random.randint(1, 11)  # Reduced duration for fading out
        self.fade_amount = random.randint(6, 12)  # Faster fade-out

    def update(self):
        if self.stuck_duration > 0:
            self.stuck_duration -= 1
            return False
        if self.fade_timer > 0:
            self.fade_timer -= 1
        else:
            self.color = tuple([max(0, c - self.fade_amount) for c in self.color])
            if self.color == (0, 0, 0):
                return True
        return False

    def draw(self):
        pygame.draw.rect(screen, self.color, (self.x, self.y, PIXEL_SIZE, PIXEL_SIZE))

class GridPixelColumn:
    def __init__(self, x):
        self.x = x
        self.y = random.randint(-MAX_COLUMN_HEIGHT, 0) * PIXEL_SIZE
        self.speed = random.choice([PIXEL_SIZE, 2*PIXEL_SIZE])  # Randomize fall speed between 1 and 2 "pixels"
        self.height = random.randint(MIN_COLUMN_HEIGHT, MAX_COLUMN_HEIGHT) * PIXEL_SIZE
        self.trigger_point = random.randint(SCREEN_HEIGHT // 4, 3 * SCREEN_HEIGHT // 4)  # Random trigger point between 1/4 and 3/4 of screen height
        self.new_column_generated = False
        self.remove = False  # Mark column for removal
        
        # 20% chance for the column's bottom pixel to have the pulsing effect
        self.pulse_phase = random.uniform(0, 2*math.pi) if random.random() < 0.20 else None

    def move(self):
        self.y += self.speed
        
        # Trigger the generation of a new column when reaching the trigger point
        if self.y > self.trigger_point and not self.new_column_generated:
            columns.append(GridPixelColumn(self.x))  # Reset the x-coordinate for the new column
            self.new_column_generated = True
        
        if self.y - self.height > SCREEN_HEIGHT:
            self.remove = True

    def draw(self):
        start_y = self.y
        for i in range(self.height // PIXEL_SIZE):
            ratio = i / (self.height // PIXEL_SIZE)
            pulse = self.pulse_phase if i == 0 else None  # Apply pulse only if pulse_phase is set for the bottom pixel
            color = get_gradient_color(GREEN, DARK_GREEN, ratio, pulse)
            pygame.draw.rect(screen, color, (self.x, start_y - i*PIXEL_SIZE, PIXEL_SIZE, PIXEL_SIZE))
            
            # Reduced chance to turn the pixel into a stuck pixel if it's bright green
            if 200 <= color[1] <= 255 and random.random() < 0.005:
                # Ensure that super bright pixels start fading immediately
                if color[1] > 250:
                    stuck_pixel = StuckPixel(self.x, start_y - i*PIXEL_SIZE, color)
                    stuck_pixel.stuck_duration = 0
                    stuck_pixels.append(stuck_pixel)
                else:
                    stuck_pixels.append(StuckPixel(self.x, start_y - i*PIXEL_SIZE, color))

# Create initial pixel columns without gaps
columns = []
stuck_pixels = []
x = 0
while x < SCREEN_WIDTH:
    columns.append(GridPixelColumn(x))
    x += PIXEL_SIZE  # No gaps

# Main loop
running = True
paused = False  # Added pause state
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:  # Check for mouse click
            paused = not paused  # Toggle pause state

    if not paused:  # Wrap existing animation code in this block
        screen.fill(BLACK)

        for column in columns:
            column.move()
            column.draw()

        for pixel in stuck_pixels:
            if pixel.update():
                stuck_pixels.remove(pixel)
            pixel.draw()

        # Remove columns marked for removal after the loop
        columns = [col for col in columns if not col.remove]

    pygame.display.flip()
    clock.tick(5)  # Adjusted frame rate for more deliberate movement

pygame.quit()
