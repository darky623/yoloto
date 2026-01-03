<script>
  let { players = [], status = 'waiting' } = $props();
  
  // Позиции для 6 игроков по кругу
  const positions = [
    { top: '10%', left: '50%', transform: 'translateX(-50%)' }, // Верх
    { top: '30%', right: '10%' }, // Справа верх
    { top: '70%', right: '10%' }, // Справа низ
    { bottom: '10%', left: '50%', transform: 'translateX(-50%)' }, // Низ
    { top: '70%', left: '10%' }, // Слева низ
    { top: '30%', left: '10%' }, // Слева верх
  ];
  
  function getPlayerPosition(index) {
    return positions[index] || {};
  }
</script>

<div class="game-board">
  <div class="board-circle">
    {#each Array(6) as _, i}
      {@const player = players[i]}
      <div
        class="player-slot"
        class:filled={player}
        class:winner={player?.is_winner}
        style={getPlayerPosition(i)}
      >
        {#if player}
          <div class="player-info">
            <div class="player-avatar">{player.username[0].toUpperCase()}</div>
            <div class="player-name">{player.username}</div>
            {#if player.dice !== null}
              <div class="player-dice" class:winner={player.is_winner}>
                {player.dice}
              </div>
            {/if}
          </div>
        {/if}
      </div>
    {/each}
    
    <div class="center-area">
      {#if status === 'rolling'}
        <div class="dice-animation">🎲</div>
      {:else if status === 'finished'}
        <div class="result-text">Результат</div>
      {/if}
    </div>
  </div>
</div>

<style>
  .game-board {
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 40px 20px;
    min-height: 500px;
  }
  
  .board-circle {
    position: relative;
    width: 600px;
    height: 600px;
    border: 3px solid var(--border);
    border-radius: 50%;
    background: var(--card-bg);
  }
  
  .player-slot {
    position: absolute;
    width: 120px;
    height: 120px;
    border: 2px solid var(--border);
    border-radius: 12px;
    background: var(--bg-dark);
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.3s;
  }
  
  .player-slot.filled {
    background: var(--accent);
    border-color: var(--accent);
  }
  
  .player-slot.winner {
    background: var(--success);
    border-color: var(--success);
    box-shadow: 0 0 20px rgba(16, 185, 129, 0.5);
    transform: scale(1.1);
  }
  
  .player-info {
    text-align: center;
    width: 100%;
    padding: 8px;
  }
  
  .player-avatar {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.2);
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 4px;
    font-weight: 700;
    font-size: 18px;
  }
  
  .player-name {
    font-size: 12px;
    font-weight: 600;
    margin-bottom: 4px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  
  .player-dice {
    font-size: 24px;
    font-weight: 700;
    color: white;
  }
  
  .player-dice.winner {
    font-size: 32px;
    animation: pulse 1s infinite;
  }
  
  @keyframes pulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.2); }
  }
  
  .center-area {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 150px;
    height: 150px;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  .dice-animation {
    font-size: 80px;
    animation: spin 0.5s linear infinite;
  }
  
  @keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }
  
  .result-text {
    font-size: 24px;
    font-weight: 700;
    color: var(--accent);
  }
  
  @media (max-width: 768px) {
    .board-circle {
      width: 400px;
      height: 400px;
    }
    
    .player-slot {
      width: 80px;
      height: 80px;
    }
    
    .player-avatar {
      width: 30px;
      height: 30px;
      font-size: 14px;
    }
    
    .player-name {
      font-size: 10px;
    }
    
    .player-dice {
      font-size: 18px;
    }
  }
</style>

