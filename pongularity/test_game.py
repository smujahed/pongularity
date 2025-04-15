import unittest
from unittest.mock import patch, MagicMock
import pygame
import sys
from .game import PongularityGame

class TestPongularityGame(unittest.TestCase):
    
    def setUp(self):
        # Mock pygame.init() and other pygame functions
        self.pygame_mock = MagicMock()
        self.pygame_display_mock = MagicMock()
        self.pygame_time_mock = MagicMock()
        self.pygame_font_mock = MagicMock()
        
        with patch('pygame.init'), \
             patch('pygame.display.set_mode', return_value=MagicMock()), \
             patch('pygame.display.set_caption'), \
             patch('pygame.time.Clock', return_value=MagicMock()), \
             patch('pygame.font.SysFont', return_value=MagicMock()):
            self.game = PongularityGame()

    def test_game_constants(self):
        """Test that game constants are set correctly"""
        self.assertEqual(self.game.WIDTH, 750)
        self.assertEqual(self.game.HEIGHT, 585)
        self.assertEqual(self.game.GRID, 15)
        self.assertEqual(self.game.PADDLE_HEIGHT, self.game.GRID * 5)
        self.assertEqual(self.game.MAX_PADDLE_Y, self.game.HEIGHT - self.game.GRID - self.game.PADDLE_HEIGHT)
        self.assertEqual(self.game.PADDLE_SPEED, 6)
        self.assertEqual(self.game.BALL_SPEED, 5)
        self.assertEqual(self.game.BALL_ACCELERATION, 0.25)
        self.assertEqual(self.game.MAX_BALL_SPEED, 15)
        self.assertEqual(self.game.MAX_SCORE, 10)
        self.assertEqual(self.game.POWERUP_SIZE, self.game.GRID * 2)
        self.assertEqual(self.game.POWERUP_SPAWN_INTERVAL, 5000)
        self.assertEqual(self.game.POWERUP_DURATION, 7000)

    def test_game_colors(self):
        """Test that game colors are set correctly"""
        self.assertEqual(self.game.BLACK, (0, 0, 0))
        self.assertEqual(self.game.WHITE, (255, 255, 255))
        self.assertEqual(self.game.LIGHT_GREY, (211, 211, 211))
        self.assertEqual(self.game.RED, (255, 0, 0))
        self.assertEqual(self.game.GREEN, (0, 255, 0))
        self.assertEqual(self.game.BLUE, (0, 0, 255))
        self.assertEqual(self.game.YELLOW, (255, 255, 0))
        self.assertEqual(self.game.CYAN, (0, 255, 255))
        self.assertEqual(self.game.PURPLE, (128, 0, 128))

    def test_initial_score(self):
        """Test that game starts with correct score"""
        self.assertEqual(self.game.score["left"], 0)
        self.assertEqual(self.game.score["right"], 0)
        self.assertEqual(self.game.game_state, "start_screen")

    def test_initial_paddle_positions(self):
        """Test that paddles start in correct positions"""
        # Left paddle
        self.assertEqual(self.game.left_paddle["x"], self.game.GRID * 2)
        self.assertEqual(self.game.left_paddle["y"], self.game.HEIGHT / 2 - self.game.PADDLE_HEIGHT / 2)
        self.assertEqual(self.game.left_paddle["width"], self.game.GRID)
        self.assertEqual(self.game.left_paddle["height"], self.game.PADDLE_HEIGHT)
        self.assertEqual(self.game.left_paddle["dy"], 0)

        # Right paddle
        self.assertEqual(self.game.right_paddle["x"], self.game.WIDTH - self.game.GRID * 3)
        self.assertEqual(self.game.right_paddle["y"], self.game.HEIGHT / 2 - self.game.PADDLE_HEIGHT / 2)
        self.assertEqual(self.game.right_paddle["width"], self.game.GRID)
        self.assertEqual(self.game.right_paddle["height"], self.game.PADDLE_HEIGHT)
        self.assertEqual(self.game.right_paddle["dy"], 0)

    def test_initial_ball_state(self):
        """Test that balls list is initialized correctly"""
        self.assertEqual(len(self.game.balls), 1)
        ball = self.game.balls[0]
        self.assertEqual(ball["x"], self.game.WIDTH / 2)
        self.assertEqual(ball["y"], self.game.HEIGHT / 2)
        self.assertEqual(ball["width"], self.game.GRID)
        self.assertEqual(ball["height"], self.game.GRID)
        self.assertFalse(ball["resetting"])
        self.assertIn(abs(ball["dx"]), [self.game.BALL_SPEED, -self.game.BALL_SPEED])
        self.assertIn(abs(ball["dy"]), [self.game.BALL_SPEED, -self.game.BALL_SPEED])

    def test_collision_detection(self):
        """Test collision detection between objects"""
        # Test overlapping objects
        obj1 = {"x": 10, "y": 10, "width": 10, "height": 10}
        obj2 = {"x": 15, "y": 15, "width": 10, "height": 10}
        self.assertTrue(self.game.collides(obj1, obj2))
        
        # Test non-overlapping objects (separated vertically)
        obj2["x"] = 15
        obj2["y"] = 30
        self.assertFalse(self.game.collides(obj1, obj2))
        
        # Test one object completely inside another
        obj1 = {"x": 10, "y": 10, "width": 20, "height": 20}
        obj2 = {"x": 15, "y": 15, "width": 5, "height": 5}
        self.assertTrue(self.game.collides(obj1, obj2))
        
        # Test objects at negative coordinates
        obj1 = {"x": -5, "y": -5, "width": 10, "height": 10}
        obj2 = {"x": 0, "y": 0, "width": 10, "height": 10}
        self.assertTrue(self.game.collides(obj1, obj2))
        
        # Test objects with zero width/height
        obj1 = {"x": 10, "y": 10, "width": 0, "height": 10}
        obj2 = {"x": 15, "y": 15, "width": 10, "height": 10}
        self.assertFalse(self.game.collides(obj1, obj2))

    def test_left_paddle_boundaries(self):
        """Test that left paddle stays within game boundaries"""
        # Set game state to "playing"
        self.game.game_state = "playing"
        
        # Test upper boundary
        self.game.left_paddle["y"] = 0
        self.game.left_paddle["dy"] = -10
        self.game.update()
        self.assertEqual(self.game.left_paddle["y"], self.game.GRID)
        
        # Test lower boundary
        self.game.left_paddle["y"] = self.game.HEIGHT
        self.game.left_paddle["dy"] = 10
        self.game.update()
        self.assertEqual(self.game.left_paddle["y"], self.game.MAX_PADDLE_Y)

    def test_right_paddle_boundaries(self):
        """Test that right paddle stays within game boundaries"""
        # Set game state to "playing"
        self.game.game_state = "playing"
        
        # Test upper boundary
        self.game.right_paddle["y"] = 0
        self.game.right_paddle["dy"] = -10
        self.game.update()
        self.assertEqual(self.game.right_paddle["y"], self.game.GRID)
        
        # Test lower boundary
        self.game.right_paddle["y"] = self.game.HEIGHT
        self.game.right_paddle["dy"] = 10
        self.game.update()
        self.assertEqual(self.game.right_paddle["y"], self.game.MAX_PADDLE_Y)

    def test_ball_reset(self):
        """Test ball reset functionality"""
        # Get the first ball
        ball = self.game.balls[0]
        
        # Set ball to non-center position
        ball["x"] = 100
        ball["y"] = 100
        ball["resetting"] = True
        ball["dx"] = 10
        ball["dy"] = 10
        
        self.game.reset_ball(ball)
        
        # Check position reset
        self.assertEqual(ball["x"], self.game.WIDTH / 2)
        self.assertEqual(ball["y"], self.game.HEIGHT / 2)
        self.assertFalse(ball["resetting"])
        
        # Check speed reset
        self.assertEqual(abs(ball["dx"]), self.game.BALL_SPEED)
        self.assertEqual(abs(ball["dy"]), self.game.BALL_SPEED)

    def test_ball_acceleration(self):
        """Test ball acceleration after paddle hit"""
        # Get the first ball
        ball = self.game.balls[0]
        
        # Test normal acceleration
        initial_dx = self.game.BALL_SPEED
        initial_dy = -self.game.BALL_SPEED
        ball["dx"] = initial_dx
        ball["dy"] = initial_dy
        
        self.game.accelerate_ball(ball)
        
        self.assertEqual(ball["dx"], initial_dx + self.game.BALL_ACCELERATION)
        self.assertEqual(ball["dy"], initial_dy - self.game.BALL_ACCELERATION)
        
        # Test max speed cap
        ball["dx"] = self.game.MAX_BALL_SPEED
        ball["dy"] = -self.game.MAX_BALL_SPEED
        self.game.accelerate_ball(ball)
        
        self.assertEqual(ball["dx"], self.game.MAX_BALL_SPEED)
        self.assertEqual(ball["dy"], -self.game.MAX_BALL_SPEED)

    def test_powerup_spawn(self):
        """Test power-up spawning functionality"""
        self.assertEqual(len(self.game.powerups), 0)
        
        self.game.spawn_powerup()
        
        self.assertEqual(len(self.game.powerups), 1)
        powerup = self.game.powerups[0]
        
        # Check powerup properties
        self.assertIn("x", powerup)
        self.assertIn("y", powerup)
        self.assertIn("width", powerup)
        self.assertIn("height", powerup)
        self.assertIn("type", powerup)
        self.assertIn("color", powerup)
        
        # Check valid type
        self.assertIn(powerup["type"], ["multi_ball", "giant_ball", "micro_ball", "slow_motion", "speed_ball"])
        
        # Check valid position
        margin = self.game.GRID * 5
        self.assertTrue(margin <= powerup["x"] <= self.game.WIDTH - margin - self.game.POWERUP_SIZE)
        self.assertTrue(margin <= powerup["y"] <= self.game.HEIGHT - margin - self.game.POWERUP_SIZE)

    def test_multi_ball_activation(self):
        """Test that multi_ball powerup adds two new balls"""
        self.assertEqual(len(self.game.balls), 1)
        
        self.game.activate_powerup("multi_ball")
        
        self.assertEqual(len(self.game.balls), 3)
        self.assertEqual(len(self.game.active_powerups), 1)
        self.assertEqual(self.game.active_powerups[0]["type"], "multi_ball")

    def test_powerup_update_giant_ball(self):
        """Test giant_ball powerup effect"""
        ball = self.game.balls[0]
        original_width = ball["width"]
        original_height = ball["height"]
        
        # Add giant_ball to active powerups
        now = 1000  # Mock time
        with patch('pygame.time.get_ticks', return_value=now):
            self.game.activate_powerup("giant_ball")
            
            # Run the update function that applies effects
            self.game.update_powerup_effects()
        
        # Check that ball size increased
        self.assertEqual(ball["width"], self.game.GRID * 2)
        self.assertEqual(ball["height"], self.game.GRID * 2)
        
        # Test cleanup after expiration
        with patch('pygame.time.get_ticks', return_value=now + self.game.POWERUP_DURATION + 100):
            self.game.update_powerup_effects()
        
        # Check that ball size is back to normal
        self.assertEqual(ball["width"], self.game.GRID)
        self.assertEqual(ball["height"], self.game.GRID)
        self.assertEqual(len(self.game.active_powerups), 0)

    def test_game_reset(self):
        """Test full game reset functionality"""
        # Add additional balls and powerups
        self.game.add_ball()
        self.game.spawn_powerup()
        self.game.activate_powerup("multi_ball")
        
        # Set scores
        self.game.score["left"] = 5
        self.game.score["right"] = 3
        
        # Reset the game
        with patch('pygame.time.get_ticks', return_value=0):
            self.game.reset_game()
        
        # Check that everything is reset
        self.assertEqual(self.game.score["left"], 0)
        self.assertEqual(self.game.score["right"], 0)
        self.assertEqual(len(self.game.balls), 1)
        self.assertEqual(len(self.game.powerups), 0)
        self.assertEqual(len(self.game.active_powerups), 0)
        self.assertEqual(self.game.game_state, "playing")

if __name__ == '__main__':
    unittest.main()