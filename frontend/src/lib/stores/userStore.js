import { writable } from 'svelte/store';

export const userStore = writable({
  user: null,
  token: null,
  isAuthenticated: false
});

export function setUser(user, token) {
  userStore.set({
    user,
    token,
    isAuthenticated: true
  });
  if (token) {
    localStorage.setItem('token', token);
  }
}

export function clearUser() {
  userStore.set({
    user: null,
    token: null,
    isAuthenticated: false
  });
  localStorage.removeItem('token');
}

// Загрузить токен из localStorage при загрузке
if (typeof window !== 'undefined') {
  const savedToken = localStorage.getItem('token');
  if (savedToken) {
    userStore.update(state => ({
      ...state,
      token: savedToken,
      isAuthenticated: true
    }));
  }
}

