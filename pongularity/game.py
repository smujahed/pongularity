"""
Pongularity game implemented with Pygame.
"""
import pygame
import sys

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
        
        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.LIGHT_GREY = (211, 211, 211)
        
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
        
        self.ball = {
            "x": self.WIDTH / 2,
            "y": self.HEIGHT / 2,
            "width": self.GRID,
            "height": self.GRID,
            "resetting": False,
            "dx": self.BALL_SPEED,
            "dy": -self.BALL_SPEED
        }
        
        self.score = {
            "left": 0,
            "right": 0
        }
        
        self.reset_timer = 0
        
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
    
    def collides(self, obj1, obj2):
        """Check collision between two rectangular objects."""
        return (obj1["x"] < obj2["x"] + obj2["width"] and
                obj1["x"] + obj1["width"] > obj2["x"] and
                obj1["y"] < obj2["y"] + obj2["height"] and
                obj1["y"] + obj1["height"] > obj2["y"])
    
    def reset_ball(self):
        """Reset the ball to the center after scoring."""
        self.ball["resetting"] = False
        self.ball["x"] = self.WIDTH / 2
        self.ball["y"] = self.HEIGHT / 2
        # Reset ball speed to initial value
        speed_sign_x = 1 if self.ball["dx"] > 0 else -1
        speed_sign_y = 1 if self.ball["dy"] > 0 else -1
        self.ball["dx"] = self.BALL_SPEED * speed_sign_x
        self.ball["dy"] = self.BALL_SPEED * speed_sign_y
    
    def reset_game(self):
        """Reset the entire game state."""
        self.score["left"] = 0
        self.score["right"] = 0
        self.left_paddle["y"] = self.HEIGHT / 2 - self.PADDLE_HEIGHT / 2
        self.right_paddle["y"] = self.HEIGHT / 2 - self.PADDLE_HEIGHT / 2
        self.reset_ball()
        self.game_state = "playing"
    
    def update(self):
        """Update game state for one frame."""
        if self.game_state == "playing":
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
            
            # Update ball position
            if not self.ball["resetting"]:
                self.ball["x"] += self.ball["dx"]
                self.ball["y"] += self.ball["dy"]
            
            # Ball collision with top and bottom
            if self.ball["y"] < self.GRID:
                self.ball["y"] = self.GRID
                self.ball["dy"] *= -1
            elif self.ball["y"] + self.GRID > self.HEIGHT - self.GRID:
                self.ball["y"] = self.HEIGHT - self.GRID * 2
                self.ball["dy"] *= -1
            
            # Ball out of bounds (scoring)
            if (self.ball["x"] < 0 or self.ball["x"] > self.WIDTH) and not self.ball["resetting"]:
                self.ball["resetting"] = True
                self.reset_timer = pygame.time.get_ticks()
                
                if self.ball["x"] < 0:
                    self.score["right"] += 1
                else:
                    self.score["left"] += 1
                
                if self.score["left"] >= self.MAX_SCORE or self.score["right"] >= self.MAX_SCORE:
                    self.game_state = "game_over"
            
            # Reset ball after delay
            if self.ball["resetting"] and pygame.time.get_ticks() - self.reset_timer >= 400:
                self.reset_ball()
            
            # Ball collision with paddles
            if self.collides(self.ball, self.left_paddle):
                self.ball["dx"] *= -1
                self.ball["x"] = self.left_paddle["x"] + self.left_paddle["width"]
                # Speed up ball after paddle hit
                self.accelerate_ball()
            elif self.collides(self.ball, self.right_paddle):
                self.ball["dx"] *= -1
                self.ball["x"] = self.right_paddle["x"] - self.ball["width"]
                # Speed up ball after paddle hit
                self.accelerate_ball()
    
    def accelerate_ball(self):
        """Increase ball speed after paddle hit."""
        # Increase speed while preserving direction
        dx_sign = 1 if self.ball["dx"] > 0 else -1
        dy_sign = 1 if self.ball["dy"] > 0 else -1
        
        dx_abs = abs(self.ball["dx"]) + self.BALL_ACCELERATION
        dy_abs = abs(self.ball["dy"]) + self.BALL_ACCELERATION
        
        # Cap maximum speed
        dx_abs = min(dx_abs, self.MAX_BALL_SPEED)
        dy_abs = min(dy_abs, self.MAX_BALL_SPEED)
        
        self.ball["dx"] = dx_abs * dx_sign
        self.ball["dy"] = dy_abs * dy_sign
    
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
            
            # Draw ball
            pygame.draw.rect(self.screen, self.WHITE, (
                self.ball["x"], 
                self.ball["y"], 
                self.ball["width"], 
                self.ball["height"]
            ))
            
            # Draw top and bottom borders
            pygame.draw.rect(self.screen, self.LIGHT_GREY, (0, 0, self.WIDTH, self.GRID))
            pygame.draw.rect(self.screen, self.LIGHT_GREY, (0, self.HEIGHT - self.GRID, self.WIDTH, self.GRID))
            
            # Draw scores
            left_score_text = self.score_font.render(str(self.score["left"]), True, self.WHITE)
            right_score_text = self.score_font.render(str(self.score["right"]), True, self.WHITE)
            
            self.screen.blit(left_score_text, (self.WIDTH // 4, self.GRID * 4))
            self.screen.blit(right_score_text, (3 * self.WIDTH // 4, self.GRID * 4))
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