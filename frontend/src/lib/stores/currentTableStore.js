import { writable } from 'svelte/store';

export const currentTableStore = writable({
  table: null,
  players: [],
  countdown: null,
  status: 'waiting',
  prizePool: 0,
  roundId: null
});

export function setTableData(data) {
  currentTableStore.set(data);
}

export function updateTableData(updates) {
  currentTableStore.update(state => ({
    ...state,
    ...updates
  }));
}

