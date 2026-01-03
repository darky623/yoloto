<script>
  let { seconds } = $props();
  
  function formatTime(sec) {
    const mins = Math.floor(sec / 60);
    const secs = sec % 60;
    return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
  }
</script>

<div class="timer">
  <div class="timer-display">{formatTime(seconds)}</div>
</div>

<style>
  .timer {
    display: flex;
    justify-content: center;
    align-items: center;
  }
  
  .timer-display {
    font-size: 48px;
    font-weight: 700;
    color: var(--accent);
    font-variant-numeric: tabular-nums;
    letter-spacing: 4px;
  }
</style>

