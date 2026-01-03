<script>
  import { api } from '../lib/services/api';
  import { setUser } from '../lib/stores/userStore';
  
  function goto(path) {
    window.location.href = path;
  }
  
  let isLogin = $state(true);
  let username = $state('');
  let password = $state('');
  let passwordConfirm = $state('');
  let error = $state('');
  let loading = $state(false);
  
  async function handleSubmit() {
    error = '';
    loading = true;
    
    try {
      if (isLogin) {
        const response = await api.login({ username, password });
        setUser({ username }, response.access_token);
        goto('/lobby');
      } else {
        if (password !== passwordConfirm) {
          error = 'Пароли не совпадают';
          loading = false;
          return;
        }
        await api.register({ username, password, password_confirm: passwordConfirm });
        // После регистрации автоматически входим
        const response = await api.login({ username, password });
        setUser({ username }, response.access_token);
        goto('/lobby');
      }
    } catch (err) {
      error = err.message || 'Произошла ошибка';
    } finally {
      loading = false;
    }
  }
</script>

<div class="login-container">
  <div class="login-card">
    <h1>{isLogin ? 'Вход' : 'Регистрация'}</h1>
    
    {#if error}
      <div class="error">{error}</div>
    {/if}
    
    <form onsubmit={(e) => { e.preventDefault(); handleSubmit(); }}>
      <div class="form-group">
        <label for="username">Логин</label>
        <input
          id="username"
          type="text"
          bind:value={username}
          required
          minlength="3"
          maxlength="20"
          pattern="[a-zA-Z0-9_]+"
          placeholder="Введите логин"
        />
      </div>
      
      <div class="form-group">
        <label for="password">Пароль</label>
        <input
          id="password"
          type="password"
          bind:value={password}
          required
          minlength="6"
          placeholder="Введите пароль"
        />
      </div>
      
      {#if !isLogin}
        <div class="form-group">
          <label for="passwordConfirm">Подтверждение пароля</label>
          <input
            id="passwordConfirm"
            type="password"
            bind:value={passwordConfirm}
            required
            minlength="6"
            placeholder="Подтвердите пароль"
          />
        </div>
      {/if}
      
      <button type="submit" disabled={loading}>
        {loading ? 'Загрузка...' : (isLogin ? 'Войти' : 'Зарегистрироваться')}
      </button>
    </form>
    
    <div class="switch">
      <button class="link-button" onclick={() => isLogin = !isLogin}>
        {isLogin ? 'Нет аккаунта? Зарегистрироваться' : 'Уже есть аккаунт? Войти'}
      </button>
    </div>
  </div>
</div>

<style>
  .login-container {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    background: var(--bg-dark);
    padding: 20px;
  }
  
  .login-card {
    background: var(--card-bg);
    border-radius: 12px;
    padding: 40px;
    width: 100%;
    max-width: 400px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
  }
  
  h1 {
    text-align: center;
    margin-bottom: 30px;
    color: var(--text-primary);
  }
  
  .form-group {
    margin-bottom: 20px;
  }
  
  label {
    display: block;
    margin-bottom: 8px;
    color: var(--text-secondary);
    font-size: 14px;
  }
  
  input {
    width: 100%;
    padding: 12px;
    background: var(--bg-dark);
    border: 1px solid var(--border);
    border-radius: 8px;
    color: var(--text-primary);
    font-size: 16px;
  }
  
  input:focus {
    border-color: var(--accent);
  }
  
  button[type="submit"] {
    width: 100%;
    padding: 12px;
    background: var(--accent);
    color: white;
    border-radius: 8px;
    font-size: 16px;
    font-weight: 600;
    margin-top: 10px;
    transition: background 0.2s;
  }
  
  button[type="submit"]:hover:not(:disabled) {
    background: var(--accent-hover);
  }
  
  button[type="submit"]:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
  
  .error {
    background: rgba(239, 68, 68, 0.1);
    border: 1px solid var(--error);
    color: var(--error);
    padding: 12px;
    border-radius: 8px;
    margin-bottom: 20px;
    text-align: center;
  }
  
  .switch {
    text-align: center;
    margin-top: 20px;
  }
  
  .link-button {
    background: none;
    color: var(--accent);
    text-decoration: underline;
    font-size: 14px;
    padding: 0;
  }
  
  .link-button:hover {
    color: var(--accent-hover);
  }
</style>

