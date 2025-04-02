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
        
        self.game_over = False
        self.reset_timer = 0
        
        # Set up display
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Pongularity")
        self.clock = pygame.time.Clock()
        
        # Font setup
        self.score_font = pygame.font.SysFont('Arial', 32)
        self.game_over_font = pygame.font.SysFont('Arial', 60)
        self.winner_font = pygame.font.SysFont('Arial', 30)
    
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
    
    def update(self):
        """Update game state for one frame."""
        if not self.game_over:
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
                    self.game_over = True
            
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
    
    def render(self):
        """Draw the game state to the screen."""
        # Clear screen
        self.screen.fill(self.BLACK)
        
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
        
        # Draw center line
        for i in range(self.GRID, self.HEIGHT - self.GRID, self.GRID * 2):
            pygame.draw.rect(self.screen, self.LIGHT_GREY, (
                self.WIDTH // 2 - self.GRID // 2, 
                i, 
                self.GRID, 
                self.GRID
            ))
        
        # Draw scores
        left_score_text = self.score_font.render(str(self.score["left"]), True, self.WHITE)
        right_score_text = self.score_font.render(str(self.score["right"]), True, self.WHITE)
        
        self.screen.blit(left_score_text, (self.WIDTH // 4, self.GRID * 4))
        self.screen.blit(right_score_text, (3 * self.WIDTH // 4, self.GRID * 4))
        
        # Draw game over message
        if self.game_over:
            game_over_text = self.game_over_font.render("GAME OVER", True, self.WHITE)
            
            winner = "LEFT" if self.score["left"] >= self.MAX_SCORE else "RIGHT"
            winner_text = self.winner_font.render(f"{winner} PLAYER WINS!", True, self.WHITE)
            
            self.screen.blit(game_over_text, (self.WIDTH // 2 - game_over_text.get_width() // 2, 
                                             self.HEIGHT // 2 - game_over_text.get_height() // 2))
            self.screen.blit(winner_text, (self.WIDTH // 2 - winner_text.get_width() // 2, 
                                          self.HEIGHT // 2 + 50))
        
        # Update display
        pygame.display.flip()
    
    def handle_input(self):
        """Process user input."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
        
        if not self.game_over:
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