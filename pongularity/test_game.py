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

    def test_game_colors(self):
        """Test that game colors are set correctly"""
        self.assertEqual(self.game.BLACK, (0, 0, 0))
        self.assertEqual(self.game.WHITE, (255, 255, 255))
        self.assertEqual(self.game.LIGHT_GREY, (211, 211, 211))

    def test_initial_score(self):
        """Test that game starts with correct score"""
        self.assertEqual(self.game.score["left"], 0)
        self.assertEqual(self.game.score["right"], 0)
        self.assertFalse(self.game.game_over)

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

    def test_initial_ball_position(self):
        """Test that ball starts in correct position"""
        self.assertEqual(self.game.ball["x"], self.game.WIDTH / 2)
        self.assertEqual(self.game.ball["y"], self.game.HEIGHT / 2)
        self.assertEqual(self.game.ball["width"], self.game.GRID)
        self.assertEqual(self.game.ball["height"], self.game.GRID)
        self.assertFalse(self.game.ball["resetting"])
        self.assertEqual(self.game.ball["dx"], self.game.BALL_SPEED)
        self.assertEqual(self.game.ball["dy"], -self.game.BALL_SPEED)

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
        # Set ball to non-center position
        self.game.ball["x"] = 100
        self.game.ball["y"] = 100
        self.game.ball["resetting"] = True
        self.game.ball["dx"] = 10
        self.game.ball["dy"] = 10
        
        self.game.reset_ball()
        
        # Check position reset
        self.assertEqual(self.game.ball["x"], self.game.WIDTH / 2)
        self.assertEqual(self.game.ball["y"], self.game.HEIGHT / 2)
        self.assertFalse(self.game.ball["resetting"])
        
        # Check speed reset
        self.assertEqual(abs(self.game.ball["dx"]), self.game.BALL_SPEED)
        self.assertEqual(abs(self.game.ball["dy"]), self.game.BALL_SPEED)

    def test_ball_acceleration(self):
        """Test ball acceleration after paddle hit"""
        # Test normal acceleration
        initial_dx = self.game.BALL_SPEED
        initial_dy = -self.game.BALL_SPEED
        self.game.ball["dx"] = initial_dx
        self.game.ball["dy"] = initial_dy
        
        self.game.accelerate_ball()
        
        self.assertEqual(self.game.ball["dx"], initial_dx + self.game.BALL_ACCELERATION)
        self.assertEqual(self.game.ball["dy"], initial_dy - self.game.BALL_ACCELERATION)
        
        # Test max speed cap
        self.game.ball["dx"] = self.game.MAX_BALL_SPEED
        self.game.ball["dy"] = -self.game.MAX_BALL_SPEED
        self.game.accelerate_ball()
        
        self.assertEqual(self.game.ball["dx"], self.game.MAX_BALL_SPEED)
        self.assertEqual(self.game.ball["dy"], -self.game.MAX_BALL_SPEED)

    def test_left_paddle_collision(self):
        """Test ball collision with left paddle"""
        # Position ball to collide with left paddle
        self.game.ball["x"] = self.game.left_paddle["x"] + self.game.left_paddle["width"] - 1
        self.game.ball["y"] = self.game.left_paddle["y"]
        self.game.ball["dx"] = -self.game.BALL_SPEED
        
        initial_speed = abs(self.game.ball["dx"])
        self.game.update()
        
        self.assertTrue(self.game.ball["dx"] > 0)  # Direction should reverse
        self.assertTrue(abs(self.game.ball["dx"]) > initial_speed)  # Speed should increase

    def test_right_paddle_collision(self):
        """Test ball collision with right paddle"""
        # Position ball to collide with right paddle
        self.game.ball["x"] = self.game.right_paddle["x"] - self.game.ball["width"] + 1
        self.game.ball["y"] = self.game.right_paddle["y"]
        self.game.ball["dx"] = self.game.BALL_SPEED
        
        initial_speed = abs(self.game.ball["dx"])
        self.game.update()
        
        self.assertTrue(self.game.ball["dx"] < 0)  # Direction should reverse
        self.assertTrue(abs(self.game.ball["dx"]) > initial_speed)  # Speed should increase

    def test_ball_wall_collision(self):
        """Test ball collision with top and bottom walls"""
        # Test top wall collision
        self.game.ball["y"] = self.game.GRID - 1
        self.game.ball["dy"] = -self.game.BALL_SPEED
        self.game.update()
        self.assertTrue(self.game.ball["dy"] > 0)
        
        # Test bottom wall collision
        self.game.ball["y"] = self.game.HEIGHT - self.game.GRID - self.game.ball["height"] + 1
        self.game.ball["dy"] = self.game.BALL_SPEED
        self.game.update()
        self.assertTrue(self.game.ball["dy"] < 0)

    def test_left_player_scoring(self):
        """Test scoring when ball goes past right edge"""
        self.game.ball["x"] = self.game.WIDTH + 10
        self.game.ball["resetting"] = False
        
        with patch('pygame.time.get_ticks', return_value=0):
            self.game.update()
            
        self.assertEqual(self.game.score["left"], 1)
        self.assertEqual(self.game.score["right"], 0)
        self.assertTrue(self.game.ball["resetting"])

    def test_right_player_scoring(self):
        """Test scoring when ball goes past left edge"""
        self.game.ball["x"] = -10
        self.game.ball["resetting"] = False
        
        with patch('pygame.time.get_ticks', return_value=0):
            self.game.update()
            
        self.assertEqual(self.game.score["left"], 0)
        self.assertEqual(self.game.score["right"], 1)
        self.assertTrue(self.game.ball["resetting"])

    def test_left_player_win(self):
        """Test game over when left player reaches max score"""
        self.game.score["left"] = self.game.MAX_SCORE - 1
        self.game.ball["x"] = self.game.WIDTH + 10
        self.game.ball["resetting"] = False
        
        with patch('pygame.time.get_ticks', return_value=0):
            self.game.update()
        
        self.assertTrue(self.game.game_over)

    def test_right_player_win(self):
        """Test game over when right player reaches max score"""
        self.game.score["right"] = self.game.MAX_SCORE - 1
        self.game.ball["x"] = -10
        self.game.ball["resetting"] = False
        
        with patch('pygame.time.get_ticks', return_value=0):
            self.game.update()
        
        self.assertTrue(self.game.game_over)

if __name__ == '__main__':
    unittest.main()