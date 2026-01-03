<script>
  import { onMount } from 'svelte';
  import { api } from '../lib/services/api';
  
  function goto(path) {
    window.location.href = path;
  }
  import { userStore, clearUser } from '../lib/stores/userStore';
  import { tablesStore, setTables } from '../lib/stores/tablesStore';
  
  let loading = $state(true);
  let error = $state('');
  let user = $derived($userStore.user);
  let balance = $state(0);
  let tables = $derived($tablesStore);
  
  onMount(async () => {
    await loadData();
    // Обновлять список столов каждые 2 секунды
    const interval = setInterval(loadTables, 2000);
    return () => clearInterval(interval);
  });
  
  async function loadData() {
    try {
      loading = true;
      await Promise.all([loadUser(), loadTables()]);
    } catch (err) {
      error = err.message || 'Ошибка загрузки данных';
      if (err.message.includes('401') || err.message.includes('Unauthorized')) {
        clearUser();
        goto('/login');
      }
    } finally {
      loading = false;
    }
  }
  
  async function loadUser() {
    try {
      const userData = await api.getMe();
      userStore.update(state => ({ ...state, user: userData }));
      balance = parseFloat(userData.balance);
    } catch (err) {
      const balanceData = await api.getBalance();
      balance = parseFloat(balanceData.balance);
    }
  }
  
  async function loadTables() {
    try {
      const tablesData = await api.getTables();
      setTables(tablesData);
    } catch (err) {
      console.error('Error loading tables:', err);
    }
  }
  
  function handleLogout() {
    clearUser();
    goto('/login');
  }
  
  function canJoinTable(table) {
    return table.status === 'waiting' || table.status === 'countdown';
  }
</script>

<div class="lobby">
  <header class="header">
    <div class="user-info">
      <span class="username">{user?.username || 'Пользователь'}</span>
      <span class="balance">Баланс: {balance.toFixed(2)} руб.</span>
    </div>
    <button class="logout-btn" on:click={handleLogout}>Выход</button>
  </header>
  
  <main class="main">
    {#if loading}
      <div class="loading">Загрузка...</div>
    {:else if error}
      <div class="error">{error}</div>
    {:else}
      <h1>Выберите стол</h1>
      <div class="tables-grid">
        {#each tables as table}
          <div class="table-card">
            <h2>{table.name}</h2>
            <div class="table-info">
              <div class="info-item">
                <span class="label">Ставка:</span>
                <span class="value">{table.bet_amount} руб.</span>
              </div>
              <div class="info-item">
                <span class="label">Игроки:</span>
                <span class="value">{table.current_players}/{table.max_players}</span>
              </div>
              <div class="info-item">
                <span class="label">Призовой фонд:</span>
                <span class="value">{parseFloat(table.prize_pool).toFixed(2)} руб.</span>
              </div>
              <div class="info-item">
                <span class="label">Статус:</span>
                <span class="value status-{table.status}">
                  {table.status === 'waiting' ? 'Ожидание' : 
                   table.status === 'countdown' ? 'Обратный отсчет' :
                   table.status === 'rolling' ? 'Игра идет' :
                   table.status === 'finished' ? 'Завершено' : table.status}
                </span>
              </div>
            </div>
            <button
              class="join-btn"
              on:click={() => goto(`/table/${table.id}`)}
              disabled={!canJoinTable(table) || balance < parseFloat(table.bet_amount)}
            >
              {canJoinTable(table) ? 'Присоединиться' : 'Наблюдать'}
            </button>
          </div>
        {/each}
      </div>
    {/if}
  </main>
</div>

<style>
  .lobby {
    min-height: 100vh;
    background: var(--bg-dark);
  }
  
  .header {
    background: var(--card-bg);
    padding: 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid var(--border);
  }
  
  .user-info {
    display: flex;
    gap: 20px;
    align-items: center;
  }
  
  .username {
    font-weight: 600;
    font-size: 18px;
  }
  
  .balance {
    color: var(--accent);
    font-weight: 600;
  }
  
  .logout-btn {
    padding: 10px 20px;
    background: var(--error);
    color: white;
    border-radius: 8px;
    font-weight: 600;
  }
  
  .logout-btn:hover {
    opacity: 0.9;
  }
  
  .main {
    max-width: 1200px;
    margin: 0 auto;
    padding: 40px 20px;
  }
  
  h1 {
    margin-bottom: 30px;
    text-align: center;
  }
  
  .tables-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 20px;
  }
  
  .table-card {
    background: var(--card-bg);
    border-radius: 12px;
    padding: 24px;
    border: 1px solid var(--border);
    transition: transform 0.2s, box-shadow 0.2s;
  }
  
  .table-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  }
  
  .table-card h2 {
    margin-bottom: 20px;
    color: var(--accent);
  }
  
  .table-info {
    display: flex;
    flex-direction: column;
    gap: 12px;
    margin-bottom: 20px;
  }
  
  .info-item {
    display: flex;
    justify-content: space-between;
    padding: 8px 0;
    border-bottom: 1px solid var(--border);
  }
  
  .label {
    color: var(--text-secondary);
  }
  
  .value {
    font-weight: 600;
  }
  
  .status-waiting {
    color: var(--text-secondary);
  }
  
  .status-countdown {
    color: #fbbf24;
  }
  
  .status-rolling {
    color: var(--accent);
  }
  
  .status-finished {
    color: var(--success);
  }
  
  .join-btn {
    width: 100%;
    padding: 12px;
    background: var(--accent);
    color: white;
    border-radius: 8px;
    font-weight: 600;
    font-size: 16px;
  }
  
  .join-btn:hover:not(:disabled) {
    background: var(--accent-hover);
  }
  
  .join-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
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

