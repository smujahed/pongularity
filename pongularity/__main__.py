"""
Main entry point for the Pongularity game.
"""
from .game import PongularityGame

def main():
    """Main entry point function for the game."""
    game = PongularityGame()
    game.run()

if __name__ == "__main__":
    main() 