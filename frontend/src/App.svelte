<script>
  import { userStore } from './lib/stores/userStore';
  import Login from './routes/Login.svelte';
  import Lobby from './routes/Lobby.svelte';
  import Table from './routes/Table.svelte';
  
  let currentPath = $state(typeof window !== 'undefined' ? window.location.pathname : '/');
  
  // Обновлять путь при изменении URL
  if (typeof window !== 'undefined') {
    window.addEventListener('popstate', () => {
      currentPath = window.location.pathname;
    });
  }
  
  function getComponent() {
    if (currentPath === '/login' || currentPath === '/') {
      return Login;
    } else if (currentPath === '/lobby') {
      return Lobby;
    } else if (currentPath.startsWith('/table/')) {
      return Table;
    }
    return Login;
  }
  
  let Component = $derived(getComponent());
</script>

{#if Component === Login}
  <Login />
{:else if Component === Lobby}
  <Lobby />
{:else if Component === Table}
  <Table />
{:else}
  <Login />
{/if}

<style>
  :global(body) {
    margin: 0;
    padding: 0;
  }
</style>

