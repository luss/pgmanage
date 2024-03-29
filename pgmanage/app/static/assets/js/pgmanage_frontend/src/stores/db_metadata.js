import { defineStore } from "pinia";
import { connectionsStore } from "../stores/stores_initializer";
import axios from "axios";

const useDbMetadataStore = defineStore("dbMetadata", {
  state: () => ({
    initialized: 'false',
    dbMeta: {}
    // connection_id: { //not a tab id so that we can reuse the same db meta entry for multiple tabs of the same database
    //     technology: 'postgresql' | sqlite....
    //     connection_meta: 'connection properties',
    //     databases: [ //for sqlite - a single entry with a stub dbname
    //         'dname': {
    //             schemas: ['',...]
    //             tables: [{name: 'smth', schema: (optional)}, }, ...]
    //         }
    //     ]
    // }
  }),
  actions: {
    getDbMeta(conn_id, db_name) {
      console.log(conn_id, db_name)
      return this.dbMeta[conn_id][db_name]
    },
    async fetchDbMeta(conn_id, tab_id, db_name) {
      const meta_response = await axios.post('/get_database_meta/', {
        database_index: conn_id,
        tab_id: tab_id
      })

      if(!this.dbMeta[conn_id])
        this.dbMeta[conn_id] = {}
      this.dbMeta[conn_id][db_name] = meta_response.data.schemas
      console.log(this.dbMeta)
    }
  },
});

export { useDbMetadataStore };