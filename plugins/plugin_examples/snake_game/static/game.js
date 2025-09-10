// 🐍 Snake Game Logic
class SnakeGame {
    constructor() {
        this.canvas = document.getElementById('gameCanvas');
        this.ctx = this.canvas.getContext('2d');
        this.gridSize = 20;
        this.tileCount = this.canvas.width / this.gridSize;
        
        // Game state
        this.gameRunning = false;
        this.gamePaused = false;
        this.gameLoop = null;
        this.borderMode = true; // true = borders kill, false = wrap around
        
        // Snake
        this.snake = [{ x: 10, y: 10 }];
        this.direction = { x: 0, y: 0 };
        this.nextDirection = { x: 0, y: 0 };
        
        // Apple
        this.apple = { x: 15, y: 15 };
        
        // Score
        this.score = 0;
        this.highScore = this.loadHighScore();
        
        // Game speed (lower = faster)
        this.gameSpeed = 150;
        
        this.initializeControls();
        this.updateDisplay();
        this.draw();
    }
    
    initializeControls() {
        document.addEventListener('keydown', (e) => {
            if (!this.gameRunning) return;
            
            const key = e.key.toLowerCase();
            
            // Prevent default for arrow keys to stop page scrolling
            if (['arrowup', 'arrowdown', 'arrowleft', 'arrowright'].includes(e.key.toLowerCase())) {
                e.preventDefault();
            }
            
            // Handle direction changes
            switch (key) {
                case 'arrowup':
                case 'w':
                    if (this.direction.y === 0) {
                        this.nextDirection = { x: 0, y: -1 };
                    }
                    break;
                case 'arrowdown':
                case 's':
                    if (this.direction.y === 0) {
                        this.nextDirection = { x: 0, y: 1 };
                    }
                    break;
                case 'arrowleft':
                case 'a':
                    if (this.direction.x === 0) {
                        this.nextDirection = { x: -1, y: 0 };
                    }
                    break;
                case 'arrowright':
                case 'd':
                    if (this.direction.x === 0) {
                        this.nextDirection = { x: 1, y: 0 };
                    }
                    break;
                case ' ':
                case 'p':
                    e.preventDefault();
                    this.togglePause();
                    break;
                case 'r':
                    e.preventDefault();
                    this.restartGame();
                    break;
            }
        });
    }
    
    startGame() {
        this.gameRunning = true;
        this.gamePaused = false;
        this.snake = [{ x: 10, y: 10 }];
        this.direction = { x: 1, y: 0 };
        this.nextDirection = { x: 1, y: 0 };
        this.score = 0;
        this.gameSpeed = 150;
        
        this.placeApple();
        this.updateDisplay();
        this.hideOverlay();
        this.enableControls();
        
        this.gameLoop = setInterval(() => {
            if (!this.gamePaused) {
                this.update();
                this.draw();
            }
        }, this.gameSpeed);
    }
    
    update() {
        // Update direction
        this.direction = { ...this.nextDirection };
        
        // Move snake head
        const head = { ...this.snake[0] };
        head.x += this.direction.x;
        head.y += this.direction.y;
        
        // Handle walls based on border mode
        if (this.borderMode) {
            // Border mode: Check wall collision
            if (head.x < 0 || head.x >= this.tileCount || 
                head.y < 0 || head.y >= this.tileCount) {
                this.gameOver();
                return;
            }
        } else {
            // Borderless mode: Wrap around walls
            if (head.x < 0) head.x = this.tileCount - 1;
            if (head.x >= this.tileCount) head.x = 0;
            if (head.y < 0) head.y = this.tileCount - 1;
            if (head.y >= this.tileCount) head.y = 0;
        }
        
        // Check self collision
        if (this.snake.some(segment => segment.x === head.x && segment.y === head.y)) {
            this.gameOver();
            return;
        }
        
        this.snake.unshift(head);
        
        // Check apple collision
        if (head.x === this.apple.x && head.y === this.apple.y) {
            this.eatApple();
        } else {
            this.snake.pop();
        }
    }
    
    eatApple() {
        this.score += 10;
        this.updateScore();
        this.placeApple();
        
        // Increase speed slightly
        if (this.gameSpeed > 80) {
            this.gameSpeed -= 2;
            clearInterval(this.gameLoop);
            this.gameLoop = setInterval(() => {
                if (!this.gamePaused) {
                    this.update();
                    this.draw();
                }
            }, this.gameSpeed);
        }
    }
    
    placeApple() {
        do {
            this.apple = {
                x: Math.floor(Math.random() * this.tileCount),
                y: Math.floor(Math.random() * this.tileCount)
            };
        } while (this.snake.some(segment => 
            segment.x === this.apple.x && segment.y === this.apple.y
        ));
    }
    
    draw() {
        // Clear canvas
        this.ctx.fillStyle = '#EBE9F8';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Draw snake
        this.ctx.fillStyle = '#4CAF50';
        this.snake.forEach((segment, index) => {
            // Head is slightly different color
            if (index === 0) {
                this.ctx.fillStyle = '#2E7D32';
            } else {
                this.ctx.fillStyle = '#4CAF50';
            }
            
            this.ctx.fillRect(
                segment.x * this.gridSize + 1,
                segment.y * this.gridSize + 1,
                this.gridSize - 2,
                this.gridSize - 2
            );
        });
        
        // Draw apple
        this.ctx.fillStyle = '#FF6B6B';
        this.ctx.fillRect(
            this.apple.x * this.gridSize + 1,
            this.apple.y * this.gridSize + 1,
            this.gridSize - 2,
            this.gridSize - 2
        );
        
        // Add some styling to apple
        this.ctx.fillStyle = '#E53E3E';
        this.ctx.fillRect(
            this.apple.x * this.gridSize + 3,
            this.apple.y * this.gridSize + 3,
            this.gridSize - 6,
            this.gridSize - 6
        );
    }
    
    gameOver() {
        this.gameRunning = false;
        clearInterval(this.gameLoop);
        
        // Update high score
        if (this.score > this.highScore) {
            this.highScore = this.score;
            this.saveHighScore();
            this.updateDisplay();
        }
        
        this.showGameOverOverlay();
        this.disableControls();
    }
    
    togglePause() {
        if (!this.gameRunning) return;
        
        this.gamePaused = !this.gamePaused;
        const pauseButton = document.getElementById('pauseButton');
        
        if (this.gamePaused) {
            pauseButton.textContent = '▶️ Resume';
            pauseButton.classList.add('pause-active');
            this.showPauseOverlay();
        } else {
            pauseButton.textContent = '⏸️ Pause';
            pauseButton.classList.remove('pause-active');
            this.hideOverlay();
        }
    }
    
    restartGame() {
        clearInterval(this.gameLoop);
        this.startGame();
    }
    
    updateScore() {
        const scoreElement = document.getElementById('currentScore');
        scoreElement.textContent = this.score;
        scoreElement.classList.add('animate');
        setTimeout(() => scoreElement.classList.remove('animate'), 300);
    }
    
    updateDisplay() {
        document.getElementById('currentScore').textContent = this.score;
        document.getElementById('highScore').textContent = this.highScore;
    }
    
    showGameOverOverlay() {
        const overlay = document.getElementById('gameOverlay');
        const title = document.getElementById('overlayTitle');
        const message = document.getElementById('overlayMessage');
        const button = document.getElementById('playButton');
        
        title.textContent = '🎮 Game Over!';
        message.textContent = `Final Score: ${this.score}${this.score === this.highScore ? ' 🏆 New High Score!' : ''}`;
        button.textContent = 'Play Again';
        button.onclick = () => this.startGame();
        
        overlay.classList.remove('hidden');
    }
    
    showPauseOverlay() {
        const overlay = document.getElementById('gameOverlay');
        const title = document.getElementById('overlayTitle');
        const message = document.getElementById('overlayMessage');
        const button = document.getElementById('playButton');
        
        title.textContent = '⏸️ Paused';
        message.textContent = 'Press Resume or P to continue';
        button.textContent = 'Resume';
        button.onclick = () => this.togglePause();
        
        overlay.classList.remove('hidden');
    }
    
    hideOverlay() {
        document.getElementById('gameOverlay').classList.add('hidden');
    }
    
    enableControls() {
        document.getElementById('pauseButton').disabled = false;
        document.getElementById('restartButton').disabled = false;
    }
    
    disableControls() {
        const pauseButton = document.getElementById('pauseButton');
        pauseButton.disabled = true;
        pauseButton.textContent = '⏸️ Pause';
        pauseButton.classList.remove('pause-active');
        document.getElementById('restartButton').disabled = false;
    }
    
    loadHighScore() {
        return parseInt(localStorage.getItem('airflow-snake-high-score') || '0');
    }
    
    saveHighScore() {
        localStorage.setItem('airflow-snake-high-score', this.highScore.toString());
    }
    
    toggleBorderMode() {
        this.borderMode = !this.borderMode;
        this.updateModeDescription();
        
        // If game is running, restart with new mode
        if (this.gameRunning) {
            this.restartGame();
        }
    }
    
    updateModeDescription() {
        const description = document.getElementById('modeDescription');
        const toggle = document.getElementById('borderToggle');
        
        if (this.borderMode) {
            description.textContent = 'Classic mode: Hit walls = Game Over';
            toggle.checked = true;
        } else {
            description.textContent = 'Arcade mode: Walls wrap around';
            toggle.checked = false;
        }
    }
}

// Global functions for button handlers
let game;

function startGame() {
    if (game) {
        game.startGame();
    }
}

function togglePause() {
    if (game) {
        game.togglePause();
    }
}

function restartGame() {
    if (game) {
        game.restartGame();
    }
}

function toggleBorderMode() {
    if (game) {
        game.toggleBorderMode();
    }
}

// Initialize game when page loads
document.addEventListener('DOMContentLoaded', () => {
    game = new SnakeGame();
    // Set initial border toggle state
    const toggle = document.getElementById('borderToggle');
    toggle.checked = game.borderMode;
    game.updateModeDescription();
});
