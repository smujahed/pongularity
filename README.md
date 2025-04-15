# Pongularity

A simple implementation of the classic Pong game using Pygame.

## Installation

1. Clone this repository:
```
git clone <repository-url>
cd <repository-directory>
```

2. Create a virtual environment and activate it:
```
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the required dependencies:
```
pip install -r requirements.txt
```

## Running the Game

You can run the game in one of two ways:

1. Install the package and run using the entry point:
```
pip install -e .
pongularity
```

2. Or run directly using the module:
```
python -m pongularity
```

## Controls

- **Left Paddle**: W (up), S (down)
- **Right Paddle**: Up Arrow (up), Down Arrow (down)
- **Exit**: Close the window

## Game Rules

- First player to score 10 points wins
- A point is scored when the opponent fails to return the ball
- The ball speeds up slightly after each successful return

Enjoy the game! 