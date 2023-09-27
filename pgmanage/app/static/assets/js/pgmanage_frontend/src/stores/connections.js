// const pinia = Pinia.createPinia();
// Pinia.setActivePinia(pinia);
import { createPinia, defineStore, setActivePinia } from 'pinia'

const pinia = createPinia()
setActivePinia(pinia)

const useConnectionsStore = defineStore({
  id: "connections",
  state: () => ({
    connections: [],
    groups: [],
  }),
  getters: {
    remote_terminals: (state) =>
      state.connections.filter((conn) => conn.technology === "terminal"),
  },
});

const connectionsStore = useConnectionsStore();

export { connectionsStore }