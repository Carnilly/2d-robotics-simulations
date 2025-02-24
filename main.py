import pygame
import sys
import math

# Initialize Pygame
pygame.init()

# Set up display
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Autonomous Robot with Obstacle Recovery")

# Set up clock for FPS
clock = pygame.time.Clock()

# Robot settings
robot_pos = [WIDTH // 2, HEIGHT // 2]
robot_angle = 0  # Angle in degrees
robot_speed = 2
rotation_speed = 2
recovery_mode = False  # Flag to indicate recovery behavior
recovery_steps = 0     # Counter for recovery steps

# Robot dimensions
ROBOT_WIDTH, ROBOT_HEIGHT = 50, 30
robot_surface = pygame.Surface((ROBOT_WIDTH, ROBOT_HEIGHT), pygame.SRCALPHA)
robot_surface.fill((0, 128, 255))  # Blue robot

# Obstacles
obstacles = [
    pygame.Rect(200, 150, 100, 300),
    pygame.Rect(500, 100, 150, 150),
    pygame.Rect(350, 400, 200, 50)
]

def draw_robot(pos, angle):
    """Draws the robot and a direction indicator line."""
    rotated_robot = pygame.transform.rotate(robot_surface, angle)
    rect = rotated_robot.get_rect(center=pos)
    screen.blit(rotated_robot, rect.topleft)

    # Direction line
    line_length = 40
    end_x = pos[0] + line_length * math.cos(math.radians(-angle))
    end_y = pos[1] + line_length * math.sin(math.radians(-angle))
    pygame.draw.line(screen, (255, 0, 0), pos, (end_x, end_y), 3)  # Red direction line

    return rect

def draw_obstacles():
    """Draws static obstacles."""
    for obstacle in obstacles:
        pygame.draw.rect(screen, (128, 128, 128), obstacle)

def detect_collision(robot_rect):
    """Detect collision between robot and any obstacle."""
    return any(robot_rect.colliderect(obstacle) for obstacle in obstacles)

def cast_sensor(pos, angle, length=100):
    """Simulates a distance sensor using raycasting."""
    end_x = pos[0] + length * math.cos(math.radians(-angle))
    end_y = pos[1] + length * math.sin(math.radians(-angle))
    pygame.draw.line(screen, (0, 255, 0), pos, (end_x, end_y), 2)

    # Check for collision along the line
    sensor_line = pygame.Rect(min(pos[0], end_x), min(pos[1], end_y), abs(end_x - pos[0]), abs(end_y - pos[1]))
    for obstacle in obstacles:
        if sensor_line.colliderect(obstacle):
            return True  # Obstacle detected
    return False

def check_boundary(robot_rect):
    """Check if the robot is going out of bounds and correct it."""
    if robot_rect.left < 0 or robot_rect.right > WIDTH or robot_rect.top < 0 or robot_rect.bottom > HEIGHT:
        return True
    return False

def autonomous_navigation(front_sensor, left_sensor, right_sensor, boundary_detected):
    """Decision-making for obstacle and boundary avoidance."""
    global robot_angle, recovery_mode, recovery_steps

    if recovery_mode:
        # Recovery behavior: back up and turn
        if recovery_steps < 30:
            # Reverse
            robot_pos[0] -= robot_speed * math.cos(math.radians(-robot_angle))
            robot_pos[1] -= robot_speed * math.sin(math.radians(-robot_angle))
        else:
            # Turn in place after reversing
            robot_angle += rotation_speed
        recovery_steps += 1

        # End recovery after enough steps
        if recovery_steps > 60:
            recovery_mode = False
            recovery_steps = 0

    else:
        # Normal obstacle avoidance behavior
        if boundary_detected or front_sensor:
            recovery_mode = True  # Trigger recovery mode
        else:
            # Adjust course if side sensors detect obstacles
            if left_sensor:
                robot_angle -= rotation_speed / 2  # Turn right slightly
            elif right_sensor:
                robot_angle += rotation_speed / 2  # Turn left slightly

# Game loop
running = True
while running:
    clock.tick(60)  # 60 FPS
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Autonomous movement
    prev_pos = robot_pos.copy()
    prev_angle = robot_angle

    # Sensors (front, left, right)
    front_sensor = cast_sensor(robot_pos, robot_angle, length=80)
    left_sensor = cast_sensor(robot_pos, robot_angle + 45, length=60)
    right_sensor = cast_sensor(robot_pos, robot_angle - 45, length=60)

    # Move robot forward continuously (unless in recovery mode)
    if not recovery_mode:
        robot_pos[0] += robot_speed * math.cos(math.radians(-robot_angle))
        robot_pos[1] += robot_speed * math.sin(math.radians(-robot_angle))

    # Redraw screen
    screen.fill((30, 30, 30))
    draw_obstacles()
    robot_rect = draw_robot(robot_pos, robot_angle)

    # Check boundaries and collisions
    boundary_detected = check_boundary(robot_rect)
    if detect_collision(robot_rect) or boundary_detected:
        robot_pos = prev_pos
        robot_angle = prev_angle
        recovery_mode = True  # Enter recovery mode after collision

    # Decision-making
    autonomous_navigation(front_sensor, left_sensor, right_sensor, boundary_detected)

    pygame.display.flip()

pygame.quit()
sys.exit()
