<template>
<div v-if="visible" class="col-9 d-flex ml-auto">
  <div class="modal-connections__forms position-absolute w-100">
    <div  class="modal-connections__forms_connection connection-form position-absolute">
        <div class="connection-form__header d-flex justify-content-between align-items-center pb-3">
        <!-- TODO: integrate with active connection list -->
        <h3 class="connection-form__header_title mb-0">{{initialConnection.alias}} {{connectionLocal.locked ? "(Active/Read Only)": ""}}</h3>
        <!-- TODO: add test connecttion -->
        <button @click="$emit('connection:test', this.connectionLocal)" class="btn btn-success">Test</button>
        <!-- FIXME: conditionally disable if form is dirty -->
        <button @click="dispatchConnectionSelected(this.connectionLocal)" class="btn btn-success">Connect</button>
        </div>

        <form>
          <!-- TODO: add validations -->
        <div class="form-row mt-3">
            <div class="form-group col-6">
            <label for="connectionName" class="font-weight-bold mb-3">Name</label>
            <input v-model="connectionLocal.alias" type="text" class="form-control" id="connectionName" placeholder="Connection name">
            </div>
            <div class="form-group col-3">
            <label for="connectionType" class="font-weight-bold mb-3">Type</label>
            <select v-model="connectionLocal.technology" @change="handleTypeChange" id="connectionType" class="form-control" placeholder="Connection type">
                <option disabled>Choose...</option>
                <option v-for="(technology, index) in technologies"
                  :key=index
                  :value="technology">
                    {{technology}}
                </option>
            </select>
            </div>
            <div class="form-group col-3">
            <label for="connectionGroup" class="font-weight-bold mb-3">Group</label>
            <select v-model="connectionLocal.group" id="connectionGroup" class="form-control" placeholder="Connection group">
                <option value=""></option>
                <option v-for="(group, index) in groups"
                  :key=index
                  :value="group.id">
                    {{group.name}}
                </option>
            </select>
            </div>
        </div>

        <div class="form-row">
            <div class="form-group col-6">
            <label for="connectionName" class="font-weight-bold mb-3">Server</label>
            <input v-model="connectionLocal.server" type="text" class="form-control" id="connectionServer"
              :placeholder="placeholder.server"
              :disabled="dbFormDisabled">
            </div>

            <div class="form-group col-3">
            <label for="connectionPort" class="font-weight-bold mb-3">Port</label>
            <input v-model="connectionLocal.port" type="text" class="form-control" id="connectionPort"
              :placeholder="placeholder.port"
              :disabled="dbFormDisabled">
            </div>

            <div class="form-group col-3">
            <label for="connectionSSL" class="font-weight-bold mb-3">SSL</label>
            <select id="connectionSSL" class="form-control" placeholder="SSL" disabled="true">
                <option selected>Choose...</option>
                <option>Option 1</option>
                <option>Option 2</option>
            </select>
            </div>
        </div>

        <div class="form-row">
            <div class="form-group col-6">
            <label for="connectionDatabase" class="font-weight-bold mb-3">Database</label>
            <input v-model="connectionLocal.service" type="text" class="form-control" id="connectionDatabase"
              :placeholder="placeholder.service"
              :disabled="connectionLocal.technology==='terminal' || !!connectionLocal.conn_string.length">
            </div>

            <div class="form-group col-3">
            <label for="connectionUsername" class="font-weight-bold mb-3">Username</label>
            <input v-model="connectionLocal.user" type="text" class="form-control" id="connectionUsername"
              :placeholder="placeholder.user"
              :disabled="dbFormDisabled">
            </div>

            <div class="form-group col-3">
            <label for="connectionPassword" class="font-weight-bold mb-3">Password</label>
            <input v-model="connectionLocal.password" type="password" class="form-control" id="connectionPassword"
              :disabled="dbFormDisabled">
            </div>
        </div>

        <div class="connection-form__divider d-flex align-items-center my-3">
            <span class="connection-form__divider_text">OR</span>
        </div>

        <div class="form-group">
            <label for="connectionSring" class="font-weight-bold mb-3">Use a connection string</label>
            <input v-model="connectionLocal.conn_string" type="text" class="form-control" id="connectionSring"
              :placeholder="placeholder.conn_string"
              :disabled="connStringDisabled">
        </div>

        <div class="custom-control custom-switch mb-3">
            <input v-model="connectionLocal.tunnel.enabled" @change="scrollToTunnel" type="checkbox" class="custom-control-input" id="sshTunel" data-toggle="collapse" data-target="#sshSettings">
            <label class="custom-control-label font-weight-bold" for="sshTunel">Use SSH tunnel</label>
        </div>

        <div id="sshSettings" :class="(connectionLocal.tunnel.enabled) ? 'collapse show':'collapse'">
            <div class="form-row">
            <div class="form-group col-6">
                <label for="sshServer" class="font-weight-bold mb-3">SSH Server</label>
                <input v-model="connectionLocal.tunnel.server" type="text" class="form-control" id="sshServer" placeholder="SSH Server">
            </div>

            <div class="form-group col-3">
                <label for="sshPort" class="font-weight-bold mb-3">SSH Port</label>
                <input v-model="connectionLocal.tunnel.port" type="text" class="form-control" id="sshPort" placeholder="SSH Port">
            </div>

            <div class="form-group col-3">
                <label for="sshUsername" class="font-weight-bold mb-3">SSH Username</label>
                <input v-model="connectionLocal.tunnel.user" type="text" class="form-control" id="sshUsername" placeholder="SSH Username">
            </div>
            </div>

            <div class="form-row">
            <div class="form-group col-6">
                <label for="sshPassphrase" class="font-weight-bold mb-3">SSH Passphrase</label>
                <input v-model="connectionLocal.tunnel.password" type="password" class="form-control" id="sshPassphrase" placeholder="SSH Passphrase">
            </div>

            <div class="form-group col-6">
                <p class="font-weight-bold mb-3">Select file</p>
                <label class="btn btn-secondary">
                {{connectionLocal.tunnel.key ? 'Key File Loaded' : 'Select Key' }} <input type="file" @change="updateConnectionKey" hidden>
                </label>
            </div>
            </div>
        </div>
        </form>
    </div>
  </div>
  <div class="modal-footer mt-auto justify-content-between w-100">
    <button v-if="connectionLocal.id" type="button" @click="$emit('connection:delete', this.connectionLocal)" class="btn btn-danger">Delete</button>
    <button type="button"
      @click="$emit('connection:save', this.connectionLocal)"
      :disabled="connectionLocal.locked"
      class="btn btn-primary ml-auto">Save changes</button>
  </div>
</div>
</template>


<script>
// TODO: validations
// TODO: reset form on selected connection change
// TODO: handle boolean values in password fields
  export default {
    name: 'ConnectionsModalConnectionForm',
    data() {
      return {
        connectionLocal: {},
      }
    },
    props: {
      visible: Boolean,
      groups: Object,
      initialConnection: {
        type: Object,
        required: true,
        default: {
          id: null,
          alias: 'New Connection',
          locked: false,
          public: false,
          is_mine: true,
          technology: null,
          group: null,
          conn_string: "",
          server: null,
          port: null,
          service: null,
          user: null,
          password: "",
          password_set: false,
          tunnel: {
            enabled: false,
            server: "",
            port: "",
            user: "",
            password: "",
            password_set: false,
            key: "",
            key_set: false
          }
        }
      },
      technologies: Array,
      groups: Array
    },
    computed: {
      placeholder() {
        const placeholderMap = {
          'postgresql': {
            'server': 'ex: 127.0.0.1',
            'port': 'ex: 5432',
            'service': 'ex: postgres',
            'user': 'ex: postgres',
            'conn_string': 'ex: postgresql://postgres@localhost:5432/postgres'
          },
          'mysql': {
            'server': 'ex: 127.0.0.1',
            'port': 'ex: 3306',
            'service': 'ex: db',
            'user': 'ex: root',
            'conn_string': 'ex: mysql://root@localhost:3306/db'
          },
          'mariadb': {
            'server': 'ex: 127.0.0.1',
            'port': 'ex: 3306',
            'service': 'ex: db',
            'user': 'ex: root',
            'conn_string': 'ex: mysql://root@localhost:3306/db'
          },
          'oracle': {
            'server': 'ex: 127.0.0.1',
            'port': 'ex: 1521',
            'service': 'ex: xe',
            'user': 'ex: system',
            'conn_string': 'ex: oracle://system@localhost:1521/xe'
          },
          'sqlite': {
            'server': '',
            'port': '',
            'service': 'ex: /home/user/sqlite_file.db',
            'user': '',
            'conn_string': ''
          },
          'terminal': {
            'server': '',
            'port': '',
            'service': '',
            'user': '',
            'conn_string': ''
          },
        }
        let current_db = this.connectionLocal.technology || 'postgresql'
        return placeholderMap[current_db]
      },
      dbFormDisabled() {
        return ['sqlite', 'terminal'].includes(this.connectionLocal.technology) || !!this.connectionLocal.conn_string.length
      },
      connStringDisabled() {
        return (!!this.connectionLocal.server ||
        !!this.connectionLocal.port ||
        !!this.connectionLocal.user ||
        !!this.connectionLocal.password ||
        !!this.connectionLocal.service ||
        ['terminal', 'sqlite'].includes(this.connectionLocal.technology))
      }
    },
    methods: {
      dispatchConnectionSelected(connection) {
        let event = new CustomEvent('connection:selected', { detail: connection })
        document.dispatchEvent(event)
      },
      updateConnectionKey(event) {
        let file = (event.target.files) ? event.target.files[0] : false;
        let reader = new FileReader();
        reader.onload = (e) => { this.connectionLocal.tunnel.key = e.target.result; };
        reader.readAsText(file);
      },
      handleTypeChange(event) {
        let technology = event.target.value
        if(technology === 'terminal') {
          // erase db fields
          this.connectionLocal.server = ''
          this.connectionLocal.port = ''
          this.connectionLocal.service = ''
          this.connectionLocal.user = ''
          this.connectionLocal.password = ''
          // open ssh subform
          this.connectionLocal.tunnel.enabled = true
          setTimeout(this.scrollToTunnel,10)
        } else {
          this.connectionLocal.tunnel.enabled = false
        }

        if(technology === 'sqlite') {
          this.connectionLocal.server = ''
          this.connectionLocal.port = ''
          this.connectionLocal.user = ''
          this.connectionLocal.password = ''
        }
      },
      scrollToTunnel(){
        // scroll the tunnel form into viewport if tunnel was enabled
        if(this.connectionLocal.tunnel.enabled) {
          document.getElementById('sshSettings').scrollIntoView()
        }
      }
    },
    watch: {
      initialConnection(newVal, oldVal) {
        this.connectionLocal = {...newVal}
        this.connectionLocal.tunnel = {...newVal.tunnel}
      },
    }
  }
</script>