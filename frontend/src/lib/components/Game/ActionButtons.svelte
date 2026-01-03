<script>
  let { isJoined, canJoin, onJoin, onLeave, betAmount } = $props();
</script>

<div class="action-buttons">
  {#if isJoined}
    <button class="action-btn joined" disabled>
      Ставка сделана
    </button>
    <p class="bet-info">Стоимость {betAmount} руб.</p>
  {:else}
    <button
      class="action-btn join"
      onclick={onJoin}
      disabled={!canJoin}
    >
      Ставка
    </button>
    <p class="bet-info">Стоимость {betAmount} руб.</p>
  {/if}
</div>

<style>
  .action-buttons {
    text-align: center;
    margin-top: 30px;
  }
  
  .action-btn {
    padding: 16px 48px;
    font-size: 18px;
    font-weight: 700;
    border-radius: 12px;
    min-width: 200px;
    transition: all 0.2s;
  }
  
  .action-btn.join {
    background: var(--accent);
    color: white;
  }
  
  .action-btn.join:hover:not(:disabled) {
    background: var(--accent-hover);
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(139, 92, 246, 0.4);
  }
  
  .action-btn.joined {
    background: var(--border);
    color: var(--text-secondary);
    cursor: not-allowed;
  }
  
  .action-btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
  
  .bet-info {
    margin-top: 12px;
    color: var(--text-secondary);
    font-size: 14px;
  }
</style>

