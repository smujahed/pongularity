"""
Pongularity game implemented with Pygame.
"""
import pygame
import sys
import random
import math

class PongularityGame:
    def __init__(self):
        pygame.init()
        
        # Constants
        self.WIDTH = 750
        self.HEIGHT = 585
        self.GRID = 15
        self.PADDLE_HEIGHT = self.GRID * 5
        self.MAX_PADDLE_Y = self.HEIGHT - self.GRID - self.PADDLE_HEIGHT
        self.PADDLE_SPEED = 6
        self.BALL_SPEED = 5
        self.BALL_ACCELERATION = 0.25
        self.MAX_BALL_SPEED = 15
        self.MAX_SCORE = 10
        self.POWERUP_SIZE = self.GRID * 2
        self.POWERUP_SPAWN_INTERVAL = 5000  # ms
        self.POWERUP_DURATION = 7000  # ms
        
        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.LIGHT_GREY = (211, 211, 211)
        self.RED = (255, 0, 0)
        self.GREEN = (0, 255, 0)
        self.BLUE = (0, 0, 255)
        self.YELLOW = (255, 255, 0)
        self.CYAN = (0, 255, 255)
        self.PURPLE = (128, 0, 128)
        
        # Game state
        self.game_state = "start_screen"  # Can be "start_screen", "playing", or "game_over"
        
        # Game objects
        self.left_paddle = {
            "x": self.GRID * 2,
            "y": self.HEIGHT / 2 - self.PADDLE_HEIGHT / 2,
            "width": self.GRID,
            "height": self.PADDLE_HEIGHT,
            "dy": 0
        }
        
        self.right_paddle = {
            "x": self.WIDTH - self.GRID * 3,
            "y": self.HEIGHT / 2 - self.PADDLE_HEIGHT / 2,
            "width": self.GRID,
            "height": self.PADDLE_HEIGHT,
            "dy": 0
        }
        
        # Instead of a single ball, we'll have a list of balls
        self.balls = []
        self.add_ball()  # Add the initial ball
        
        self.score = {
            "left": 0,
            "right": 0
        }
        
        self.reset_timer = 0
        
        # Power-up system
        self.powerups = []
        self.active_powerups = []
        self.last_powerup_spawn = 0
        
        # Set up display
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Pongularity")
        self.clock = pygame.time.Clock()
        
        # Font setup
        self.score_font = pygame.font.SysFont('Arial', 32)
        self.game_over_font = pygame.font.SysFont('Arial', 60)
        self.winner_font = pygame.font.SysFont('Arial', 30)
        self.title_font = pygame.font.SysFont('Arial', 72)
        self.instruction_font = pygame.font.SysFont('Arial', 20)
        self.powerup_font = pygame.font.SysFont('Arial', 16)
    
    def add_ball(self, speed_multiplier=1.0):
        """Add a new ball to the game."""
        ball = {
            "x": self.WIDTH / 2,
            "y": self.HEIGHT / 2,
            "width": self.GRID,
            "height": self.GRID,
            "resetting": False,
            "dx": self.BALL_SPEED * speed_multiplier * random.choice([-1, 1]),
            "dy": self.BALL_SPEED * speed_multiplier * random.choice([-1, 1])
        }
        self.balls.append(ball)
        return ball
    
    def collides(self, obj1, obj2):
        """Check collision between two rectangular objects."""
        return (obj1["x"] < obj2["x"] + obj2["width"] and
                obj1["x"] + obj1["width"] > obj2["x"] and
                obj1["y"] < obj2["y"] + obj2["height"] and
                obj1["y"] + obj1["height"] > obj2["y"])
    
    def reset_ball(self, ball):
        """Reset a ball to the center after scoring."""
        ball["resetting"] = False
        ball["x"] = self.WIDTH / 2
        ball["y"] = self.HEIGHT / 2
        # Reset ball speed to initial value
        speed_sign_x = 1 if ball["dx"] > 0 else -1
        speed_sign_y = 1 if ball["dy"] > 0 else -1
        ball["dx"] = self.BALL_SPEED * speed_sign_x
        ball["dy"] = self.BALL_SPEED * speed_sign_y
    
    def reset_game(self):
        """Reset the entire game state."""
        self.score["left"] = 0
        self.score["right"] = 0
        self.left_paddle["y"] = self.HEIGHT / 2 - self.PADDLE_HEIGHT / 2
        self.right_paddle["y"] = self.HEIGHT / 2 - self.PADDLE_HEIGHT / 2
        
        # Clear all balls and add a new one
        self.balls = []
        self.add_ball()
        
        # Clear all power-ups
        self.powerups = []
        self.active_powerups = []
        self.last_powerup_spawn = pygame.time.get_ticks()
        
        self.game_state = "playing"
    
    def spawn_powerup(self):
        """Spawn a random power-up on the field."""
        powerup_types = [
            {"type": "multi_ball", "color": self.YELLOW},
            {"type": "giant_ball", "color": self.RED},
            {"type": "micro_ball", "color": self.BLUE},
            {"type": "slow_motion", "color": self.CYAN},
            {"type": "speed_ball", "color": self.PURPLE}
        ]
        
        powerup_type = random.choice(powerup_types)
        
        # Don't spawn in corners or too close to paddles
        margin = self.GRID * 5
        x = random.randint(margin, self.WIDTH - margin - self.POWERUP_SIZE)
        y = random.randint(margin, self.HEIGHT - margin - self.POWERUP_SIZE)
        
        powerup = {
            "x": x,
            "y": y,
            "width": self.POWERUP_SIZE,
            "height": self.POWERUP_SIZE,
            "type": powerup_type["type"],
            "color": powerup_type["color"]
        }
        
        self.powerups.append(powerup)
    
    def activate_powerup(self, powerup_type):
        """Activate a power-up effect."""
        now = pygame.time.get_ticks()
        
        # Add this power-up to active power-ups with an end time
        active_powerup = {
            "type": powerup_type,
            "end_time": now + self.POWERUP_DURATION
        }
        
        # Apply immediate effects
        if powerup_type == "multi_ball":
            # Add a new ball
            speed_multiplier = 1.0
            for _ in range(2):  # Add 2 balls
                self.add_ball(speed_multiplier)
        
        self.active_powerups.append(active_powerup)
    
    def update_powerup_effects(self):
        """Update and apply active power-up effects."""
        now = pygame.time.get_ticks()
        
        # Check for expired power-ups
        i = 0
        while i < len(self.active_powerups):
            if now >= self.active_powerups[i]["end_time"]:
                # Remove the power-up effect
                powerup_type = self.active_powerups[i]["type"]
                
                # Apply clean-up for ended power-ups
                if powerup_type == "giant_ball" or powerup_type == "micro_ball":
                    # Reset ball sizes to normal
                    for ball in self.balls:
                        ball["width"] = self.GRID
                        ball["height"] = self.GRID
                
                self.active_powerups.pop(i)
            else:
                i += 1
        
        # Apply continuous effects for active power-ups
        for powerup in self.active_powerups:
            if powerup["type"] == "giant_ball":
                # Make all balls larger
                for ball in self.balls:
                    ball["width"] = self.GRID * 2
                    ball["height"] = self.GRID * 2
            
            elif powerup["type"] == "micro_ball":
                # Make all balls smaller
                for ball in self.balls:
                    ball["width"] = self.GRID // 2
                    ball["height"] = self.GRID // 2
            
            elif powerup["type"] == "slow_motion":
                # Slow down all balls
                for ball in self.balls:
                    speed_x = abs(ball["dx"])
                    speed_y = abs(ball["dy"])
                    if speed_x > self.BALL_SPEED / 2:
                        ball["dx"] = (self.BALL_SPEED / 2) * (1 if ball["dx"] > 0 else -1)
                    if speed_y > self.BALL_SPEED / 2:
                        ball["dy"] = (self.BALL_SPEED / 2) * (1 if ball["dy"] > 0 else -1)
            
            elif powerup["type"] == "speed_ball":
                # Speed up all balls
                for ball in self.balls:
                    speed_x = abs(ball["dx"])
                    speed_y = abs(ball["dy"])
                    if speed_x < self.MAX_BALL_SPEED * 0.8:
                        ball["dx"] = (self.MAX_BALL_SPEED * 0.8) * (1 if ball["dx"] > 0 else -1)
                    if speed_y < self.MAX_BALL_SPEED * 0.8:
                        ball["dy"] = (self.MAX_BALL_SPEED * 0.8) * (1 if ball["dy"] > 0 else -1)
    
    def update(self):
        """Update game state for one frame."""
        if self.game_state == "playing":
            now = pygame.time.get_ticks()
            
            # Update paddle positions
            self.left_paddle["y"] += self.left_paddle["dy"]
            self.right_paddle["y"] += self.right_paddle["dy"]
            
            # Keep paddles within bounds
            if self.left_paddle["y"] < self.GRID:
                self.left_paddle["y"] = self.GRID
            elif self.left_paddle["y"] > self.MAX_PADDLE_Y:
                self.left_paddle["y"] = self.MAX_PADDLE_Y
                
            if self.right_paddle["y"] < self.GRID:
                self.right_paddle["y"] = self.GRID
            elif self.right_paddle["y"] > self.MAX_PADDLE_Y:
                self.right_paddle["y"] = self.MAX_PADDLE_Y
            
            # Check if it's time to spawn a power-up
            if now - self.last_powerup_spawn >= self.POWERUP_SPAWN_INTERVAL:
                self.spawn_powerup()
                self.last_powerup_spawn = now
            
            # Update power-up effects
            self.update_powerup_effects()
            
            # Check for ball collision with power-ups
            for ball in self.balls:
                i = 0
                while i < len(self.powerups):
                    if self.collides(ball, self.powerups[i]):
                        # Activate the power-up
                        self.activate_powerup(self.powerups[i]["type"])
                        # Remove it from the field
                        self.powerups.pop(i)
                    else:
                        i += 1
            
            # Update ball positions and check for collisions
            balls_to_remove = []
            for i, ball in enumerate(self.balls):
                if not ball["resetting"]:
                    ball["x"] += ball["dx"]
                    ball["y"] += ball["dy"]
                
                # Ball collision with top and bottom
                if ball["y"] < self.GRID:
                    ball["y"] = self.GRID
                    ball["dy"] *= -1
                elif ball["y"] + ball["height"] > self.HEIGHT - self.GRID:
                    ball["y"] = self.HEIGHT - self.GRID - ball["height"]
                    ball["dy"] *= -1
                
                # Ball out of bounds (scoring)
                if (ball["x"] < 0 or ball["x"] > self.WIDTH) and not ball["resetting"]:
                    if len(self.balls) <= 1:
                        # This is the last or only ball, reset it
                        ball["resetting"] = True
                        self.reset_timer = now
                        
                        if ball["x"] < 0:
                            self.score["right"] += 1
                        else:
                            self.score["left"] += 1
                        
                        if self.score["left"] >= self.MAX_SCORE or self.score["right"] >= self.MAX_SCORE:
                            self.game_state = "game_over"
                    else:
                        # Multiple balls exist, we can remove this one
                        balls_to_remove.append(i)
                        
                        if ball["x"] < 0:
                            self.score["right"] += 1
                        else:
                            self.score["left"] += 1
                        
                        if self.score["left"] >= self.MAX_SCORE or self.score["right"] >= self.MAX_SCORE:
                            self.game_state = "game_over"
                
                # Reset ball after delay
                if ball["resetting"] and now - self.reset_timer >= 400:
                    self.reset_ball(ball)
                
                # Ball collision with paddles
                if self.collides(ball, self.left_paddle):
                    ball["dx"] *= -1
                    ball["x"] = self.left_paddle["x"] + self.left_paddle["width"]
                    # Speed up ball after paddle hit
                    self.accelerate_ball(ball)
                elif self.collides(ball, self.right_paddle):
                    ball["dx"] *= -1
                    ball["x"] = self.right_paddle["x"] - ball["width"]
                    # Speed up ball after paddle hit
                    self.accelerate_ball(ball)
            
            # Remove balls that went out of bounds
            for i in sorted(balls_to_remove, reverse=True):
                self.balls.pop(i)
            
            # Ensure there's always at least one ball
            if len(self.balls) == 0:
                self.add_ball()
    
    def accelerate_ball(self, ball):
        """Increase ball speed after paddle hit."""
        # Increase speed while preserving direction
        dx_sign = 1 if ball["dx"] > 0 else -1
        dy_sign = 1 if ball["dy"] > 0 else -1
        
        dx_abs = abs(ball["dx"]) + self.BALL_ACCELERATION
        dy_abs = abs(ball["dy"]) + self.BALL_ACCELERATION
        
        # Cap maximum speed
        dx_abs = min(dx_abs, self.MAX_BALL_SPEED)
        dy_abs = min(dy_abs, self.MAX_BALL_SPEED)
        
        ball["dx"] = dx_abs * dx_sign
        ball["dy"] = dy_abs * dy_sign
    
    def render_start_screen(self):
        """Render the start screen."""
        # Title
        title_text = self.title_font.render("PONGULARITY", True, self.WHITE)
        self.screen.blit(title_text, (self.WIDTH // 2 - title_text.get_width() // 2, self.HEIGHT // 4))
        
        # Centered instructions
        centered_instructions = [
            "Press SPACE to start",
            "First to 10 points wins!"
        ]
        
        y_offset = self.HEIGHT // 2
        for instruction in centered_instructions:
            instruction_text = self.instruction_font.render(instruction, True, self.LIGHT_GREY)
            self.screen.blit(instruction_text, (self.WIDTH // 2 - instruction_text.get_width() // 2, y_offset))
            y_offset += 35
        
        # Left paddle controls (left side)
        left_header = self.instruction_font.render("Left Controls", True, self.WHITE)
        self.screen.blit(left_header, (self.WIDTH // 4 - left_header.get_width() // 2, y_offset))
        
        left_up = self.instruction_font.render("W (up)", True, self.LIGHT_GREY)
        self.screen.blit(left_up, (self.WIDTH // 4 - left_up.get_width() // 2, y_offset + 35))
        
        left_down = self.instruction_font.render("S (down)", True, self.LIGHT_GREY)
        self.screen.blit(left_down, (self.WIDTH // 4 - left_down.get_width() // 2, y_offset + 70))
        
        # Right paddle controls (right side)
        right_header = self.instruction_font.render("Right Controls", True, self.WHITE)
        self.screen.blit(right_header, (3 * self.WIDTH // 4 - right_header.get_width() // 2, y_offset))
        
        right_up = self.instruction_font.render("Up Arrow (up)", True, self.LIGHT_GREY)
        self.screen.blit(right_up, (3 * self.WIDTH // 4 - right_up.get_width() // 2, y_offset + 35))
        
        right_down = self.instruction_font.render("Down Arrow (down)", True, self.LIGHT_GREY)
        self.screen.blit(right_down, (3 * self.WIDTH // 4 - right_down.get_width() // 2, y_offset + 70))
    
    def render_game_over(self):
        """Render the game over screen."""
        game_over_text = self.game_over_font.render("GAME OVER", True, self.WHITE)
        
        winner = "LEFT" if self.score["left"] >= self.MAX_SCORE else "RIGHT"
        winner_text = self.winner_font.render(f"{winner} PLAYER WINS!", True, self.WHITE)
        
        restart_text = self.instruction_font.render("Press SPACE to play again", True, self.WHITE)
        
        self.screen.blit(game_over_text, (self.WIDTH // 2 - game_over_text.get_width() // 2, 
                                         self.HEIGHT // 2 - game_over_text.get_height() // 2 - 50))
        self.screen.blit(winner_text, (self.WIDTH // 2 - winner_text.get_width() // 2, 
                                      self.HEIGHT // 2))
        self.screen.blit(restart_text, (self.WIDTH // 2 - restart_text.get_width() // 2, 
                                      self.HEIGHT // 2 + 80))
    
    def render_active_powerups(self):
        """Render the list of active power-ups on screen."""
        if not self.active_powerups:
            return
        
        y_offset = self.GRID * 2
        for i, powerup in enumerate(self.active_powerups):
            # Format power-up name nicely
            name = powerup["type"].replace("_", " ").title()
            
            # Calculate remaining time
            now = pygame.time.get_ticks()
            remaining = max(0, powerup["end_time"] - now)
            remaining_sec = math.ceil(remaining / 1000)
            
            # Format text with time remaining
            text = f"{name}: {remaining_sec}s"
            
            # Get color based on power-up type
            color = self.WHITE
            for p in self.powerups:
                if p["type"] == powerup["type"]:
                    color = p["color"]
                    break
            
            # Render text
            powerup_text = self.powerup_font.render(text, True, color)
            self.screen.blit(powerup_text, (self.WIDTH - powerup_text.get_width() - self.GRID * 2, y_offset))
            y_offset += 25
    
    def render(self):
        """Draw the game state to the screen."""
        # Clear screen
        self.screen.fill(self.BLACK)
        
        if self.game_state == "start_screen":
            self.render_start_screen()
        elif self.game_state == "playing":
            # Draw paddles
            pygame.draw.rect(self.screen, self.WHITE, (
                self.left_paddle["x"], 
                self.left_paddle["y"], 
                self.left_paddle["width"], 
                self.left_paddle["height"]
            ))
            
            pygame.draw.rect(self.screen, self.WHITE, (
                self.right_paddle["x"], 
                self.right_paddle["y"], 
                self.right_paddle["width"], 
                self.right_paddle["height"]
            ))
            
            # Draw balls
            for ball in self.balls:
                pygame.draw.rect(self.screen, self.WHITE, (
                    ball["x"], 
                    ball["y"], 
                    ball["width"], 
                    ball["height"]
                ))
            
            # Draw power-ups
            for powerup in self.powerups:
                pygame.draw.rect(self.screen, powerup["color"], (
                    powerup["x"],
                    powerup["y"],
                    powerup["width"],
                    powerup["height"]
                ))
            
            # Draw top and bottom borders
            pygame.draw.rect(self.screen, self.LIGHT_GREY, (0, 0, self.WIDTH, self.GRID))
            pygame.draw.rect(self.screen, self.LIGHT_GREY, (0, self.HEIGHT - self.GRID, self.WIDTH, self.GRID))
            
            # Draw scores
            left_score_text = self.score_font.render(str(self.score["left"]), True, self.WHITE)
            right_score_text = self.score_font.render(str(self.score["right"]), True, self.WHITE)
            
            self.screen.blit(left_score_text, (self.WIDTH // 4, self.GRID * 4))
            self.screen.blit(right_score_text, (3 * self.WIDTH // 4, self.GRID * 4))
            
            # Draw active power-ups list
            self.render_active_powerups()
            
        elif self.game_state == "game_over":
            self.render_game_over()
        
        # Update display
        pygame.display.flip()
    
    def handle_input(self):
        """Process user input."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            # Check for space bar press on start screen or game over screen
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if self.game_state == "start_screen" or self.game_state == "game_over":
                    self.reset_game()
        
        if self.game_state == "playing":
            # Get the current state of all keys
            keys = pygame.key.get_pressed()
            
            # Update paddle movement based on current key states
            self.right_paddle["dy"] = 0
            self.left_paddle["dy"] = 0
            
            if keys[pygame.K_UP]:
                self.right_paddle["dy"] = -self.PADDLE_SPEED
            elif keys[pygame.K_DOWN]:
                self.right_paddle["dy"] = self.PADDLE_SPEED
                
            if keys[pygame.K_w]:
                self.left_paddle["dy"] = -self.PADDLE_SPEED
            elif keys[pygame.K_s]:
                self.left_paddle["dy"] = self.PADDLE_SPEED
        
        return True
    
    def run(self):
        """Main game loop."""
        running = True
        
        while running:
            running = self.handle_input()
            self.update()
            self.render()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit() 