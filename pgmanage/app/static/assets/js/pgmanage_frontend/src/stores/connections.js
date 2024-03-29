import { defineStore } from "pinia";
import axios from "axios";

import { dbMetadataStore } from "../stores/stores_initializer";

const useConnectionsStore = defineStore({
  id: "connections",
  state: () => ({
    connections: [],
    groups: [],
    changeActiveDatabaseCallList: [],
    changeActiveDatabaseCallRunning: false,
  }),
  getters: {
    remote_terminals: (state) =>
      state.connections.filter((conn) => conn.technology === "terminal"),
  },
  actions: {
    getConnection(conn_id) {
      return this.connections.find((conn) => conn.id === conn_id);
    },
    queueChangeActiveDatabaseThreadSafe(data) {
      this.changeActiveDatabaseCallList.push(data);
      if (!this.changeActiveDatabaseCallRunning) {
        this.changeActiveDatabaseThreadSafe(
          this.changeActiveDatabaseCallList.pop()
        );
      }
    },
    changeActiveDatabaseThreadSafe(data) {
      console.log(data)
      this.changeActiveDatabaseCallRunning = true;
      axios
        .post("/change_active_database/", data)
        .then(async (resp) => {
          // debugger
          await dbMetadataStore.fetchDbMeta(data.database_index, data.tab_id, data.database)
          this.changeActiveDatabaseCallRunning = false;
          if (this.changeActiveDatabaseCallList.length > 0)
            this.changeActiveDatabaseThreadSafe(
              this.changeActiveDatabaseCallList.pop()
            );
        })
        .catch((error) => {
          console.log(error);
        });
    },
  },
});

export { useConnectionsStore };
