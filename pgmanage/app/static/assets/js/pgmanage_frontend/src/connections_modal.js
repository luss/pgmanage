import { createApp } from 'vue'
import { connectionsStore } from './stores/connections.js'
import { tabsStore } from './stores/stores_initializer.js'
import ConnectionsModal from './components/ConnectionsModal.vue'
import moment from 'moment'
import { emitter } from './emitter.js'

const conn_app = createApp({
    components: {
        'connections-modal': ConnectionsModal
    },
  })

// this is a temporary supporting code to glue the new vue app and old app code
// connection manager just emits the event with a selected connection as a payload
// the glue code does the necessary stuff in the old app

function connectionsModalInit() {
    document.addEventListener('connection:selected', function(event){
        let connection = event.detail
        if(connection) {
            // patch the connection last used date when connecting
            // to refresh last-used labels on the welcome screen
            connectionsStore.connections.find((c) => c.id == connection.id).last_access_date = moment.now()
        }
        $('#connections-modal').modal('hide')
        if (connection.technology === 'terminal') {
            let details = `${connection.tunnel.user}@${connection.tunnel.server}:${connection.tunnel.port}`
            emitter.emit(`${tabsStore.id}_create_terminal_tab`, {index: connection.id, alias: connection.alias, details: details})
        }
        else {
            emitter.emit(`${tabsStore.id}_create_conn_tab`, ({index: connection.id}))
        }
    })
}

export { connectionsModalInit, conn_app }