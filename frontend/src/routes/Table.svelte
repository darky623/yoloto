<script>
  import { onMount, onDestroy } from 'svelte';
  import { api } from '../lib/services/api';
  
  function goto(path) {
    window.location.href = path;
  }
  import { userStore } from '../lib/stores/userStore';
  import { currentTableStore, setTableData, updateTableData } from '../lib/stores/currentTableStore';
  import { wsService } from '../lib/services/websocket';
  import Timer from '../lib/components/Game/Timer.svelte';
  import GameBoard from '../lib/components/Game/GameBoard.svelte';
  import ActionButtons from '../lib/components/Game/ActionButtons.svelte';
  
  let tableId = $derived.by(() => {
    const match = window.location.pathname.match(/\/table\/(\d+)/);
    return match ? parseInt(match[1]) : null;
  });
  
  let loading = $state(true);
  let error = $state('');
  let user = $derived($userStore.user);
  let token = $derived($userStore.token);
  let tableData = $derived($currentTableStore);
  let balance = $state(0);
  let isJoined = $state(false);
  
  onMount(async () => {
    if (!tableId || !token) {
      goto('/lobby');
      return;
    }
    
    await loadTable();
    connectWebSocket();
    
    return () => {
      wsService.disconnect();
    };
  });
  
  onDestroy(() => {
    wsService.disconnect();
  });
  
  async function loadTable() {
    try {
      loading = true;
      const data = await api.getTable(tableId);
      setTableData({
        table: data,
        players: data.players || [],
        countdown: data.countdown_seconds,
        status: data.status,
        prizePool: parseFloat(data.prize_pool),
        roundId: data.current_round_id
      });
      
      // Проверить, участвует ли пользователь
      isJoined = data.players.some(p => p.user_id === user?.id);
      balance = parseFloat(user?.balance || 0);
    } catch (err) {
      error = err.message || 'Ошибка загрузки стола';
      if (err.message.includes('401') || err.message.includes('Unauthorized')) {
        goto('/login');
      }
    } finally {
      loading = false;
    }
  }
  
  function connectWebSocket() {
    if (!token || !tableId) return;
    
    wsService.connect(tableId, token);
    
    // Обработчики событий
    wsService.on('table_state', (data) => {
      updateTableData({
        status: data.status,
        players: data.players || [],
        countdown: data.countdown_seconds,
        prizePool: data.prize_pool
      });
    });
    
    wsService.on('player_joined', (data) => {
      updateTableData({
        players: [...tableData.players, {
          user_id: data.player_id,
          username: data.username,
          dice: null,
          is_winner: false
        }],
        prizePool: data.prize_pool
      });
      if (data.player_id === user?.id) {
        isJoined = true;
      }
    });
    
    wsService.on('player_left', (data) => {
      updateTableData({
        players: tableData.players.filter(p => p.user_id !== data.player_id),
        prizePool: data.prize_pool
      });
      if (data.player_id === user?.id) {
        isJoined = false;
      }
    });
    
    wsService.on('countdown_started', (data) => {
      updateTableData({ countdown: data.seconds, status: 'countdown' });
    });
    
    wsService.on('countdown_update', (data) => {
      updateTableData({ countdown: data.seconds_left });
    });
    
    wsService.on('game_rolling', () => {
      updateTableData({ status: 'rolling' });
    });
    
    wsService.on('game_result', async (data) => {
      updateTableData({
        players: data.results.map(r => ({
          user_id: r.player_id,
          username: r.username,
          dice: r.dice,
          is_winner: r.is_winner
        })),
        status: 'finished'
      });
      
      // Обновить баланс
      try {
        const balanceData = await api.getBalance();
        balance = parseFloat(balanceData.balance);
        // Обновить пользователя в store
        userStore.update(state => ({
          ...state,
          user: { ...state.user, balance: balanceData.balance }
        }));
      } catch (err) {
        console.error('Error updating balance:', err);
      }
    });
    
    wsService.on('error', (data) => {
      error = data.message || 'Произошла ошибка';
    });
  }
  
  async function handleJoin() {
    try {
      await api.joinTable(tableId);
      wsService.send('join_table', { table_id: tableId });
      isJoined = true;
      await loadTable();
    } catch (err) {
      error = err.message || 'Не удалось присоединиться';
    }
  }
  
  async function handleLeave() {
    try {
      await api.leaveTable(tableId);
      wsService.send('leave_table', { table_id: tableId });
      isJoined = false;
      await loadTable();
    } catch (err) {
      error = err.message || 'Не удалось покинуть стол';
    }
  }
</script>

<div class="table-page">
  {#if loading}
    <div class="loading">Загрузка...</div>
  {:else if error}
    <div class="error">{error}</div>
  {:else}
    <header class="table-header">
      <button class="back-btn" onclick={() => goto('/lobby')}>← Назад</button>
      <div class="table-info">
        <h1>{tableData.table?.name || 'Стол'}</h1>
        <div class="info-row">
          <span>Призовой фонд: <strong>{tableData.prizePool.toFixed(2)} руб.</strong></span>
          <span>Ставка: <strong>{tableData.table?.bet_amount} руб.</strong></span>
          <span>Баланс: <strong>{balance.toFixed(2)} руб.</strong></span>
        </div>
      </div>
    </header>
    
    <main class="table-main">
      {#if tableData.countdown !== null && tableData.status === 'countdown'}
        <div class="countdown-info">
          <p>Результат через:</p>
          <Timer seconds={tableData.countdown} />
        </div>
      {:else if tableData.status === 'waiting'}
        <div class="waiting-info">
          <p>Для старта необходимо минимум {tableData.table?.min_players || 2} ставки</p>
        </div>
      {/if}
      
      <GameBoard players={tableData.players} status={tableData.status} />
      
      <ActionButtons
        isJoined={isJoined}
        canJoin={balance >= parseFloat(tableData.table?.bet_amount || 0)}
        onJoin={handleJoin}
        onLeave={handleLeave}
        betAmount={tableData.table?.bet_amount}
      />
    </main>
  {/if}
</div>

<style>
  .table-page {
    min-height: 100vh;
    background: var(--bg-dark);
    padding: 20px;
  }
  
  .table-header {
    background: var(--card-bg);
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    gap: 20px;
  }
  
  .back-btn {
    padding: 10px 20px;
    background: var(--border);
    color: var(--text-primary);
    border-radius: 8px;
    font-size: 16px;
  }
  
  .back-btn:hover {
    background: var(--accent);
  }
  
  .table-info {
    flex: 1;
  }
  
  .table-info h1 {
    margin: 0 0 10px 0;
    color: var(--accent);
  }
  
  .info-row {
    display: flex;
    gap: 20px;
    flex-wrap: wrap;
    color: var(--text-secondary);
  }
  
  .info-row strong {
    color: var(--text-primary);
  }
  
  .table-main {
    max-width: 1200px;
    margin: 0 auto;
  }
  
  .countdown-info, .waiting-info {
    text-align: center;
    margin-bottom: 30px;
    padding: 20px;
    background: var(--card-bg);
    border-radius: 12px;
  }
  
  .countdown-info p, .waiting-info p {
    font-size: 18px;
    margin-bottom: 10px;
    color: var(--text-secondary);
  }
  
  .loading, .error {
    text-align: center;
    padding: 40px;
    font-size: 18px;
  }
  
  .error {
    color: var(--error);
  }
</style>

