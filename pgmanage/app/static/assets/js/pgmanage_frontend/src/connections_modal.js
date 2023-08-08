import { createApp } from 'vue'
import ConnectionsModal from './components/ConnectionsModal.vue'

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
        $('#connections-modal').modal('hide');
        if (connection.technology === 'terminal') {
            v_connTabControl.tag.createOuterTerminalTab(connection.id, connection.alias, connection.tunnel.user + '@' + connection.tunnel.server + ':' + connection.tunnel.port);
        }
        else {
            v_connTabControl.tag.createConnTab(connection.id);
        }
    })
}

export { connectionsModalInit, conn_app }