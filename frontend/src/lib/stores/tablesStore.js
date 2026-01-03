import { writable } from 'svelte/store';

export const tablesStore = writable([]);

export function setTables(tables) {
  tablesStore.set(tables);
}

export function updateTable(tableId, updates) {
  tablesStore.update(tables => 
    tables.map(table => 
      table.id === tableId ? { ...table, ...updates } : table
    )
  );
}

