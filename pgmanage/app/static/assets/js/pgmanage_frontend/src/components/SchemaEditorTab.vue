<template>
  <div class="schema-editor-scrollable p-1 pr-2">
    <div class="form-row">
      <div class="form-group col-2">
          <label class="font-weight-bold mb-2" for="tableNameInput">Table Name</label>
          <input v-model.trim="localTable.tableName" class="form-control" id="tableNameInput" name="tableName" placeholder="table name..." />
      </div>

      <div v-if="showSchema" class="form-group col-3">
        <label class="font-weight-bold mb-2" for="selectSchema">Schema</label>
        <select class="form-control text-truncate pr-4" id="selectSchema" v-model="initialTable.schema">
          <option v-for="(schema, index) in schemas" :value="schema" :key="index">
            {{ schema }}
          </option>
        </select>
      </div>
      <div class="form-group col d-flex align-items-end">
        <button :disabled="!hasChanges || queryIsRunning" @click='applyChanges' type="button"
          class="btn btn-success mt-4 ml-auto">
          Apply Changes
        </button>
      </div>
    </div>

    <div class="form-row">
      <div class="col">
        <label class="font-weight-bold mb-2 mr-2">Columns</label>

      <!-- TODO -->
      <!-- <button @click='addColumn' class="btn btn-icon btn-icon-success" title="Add column">
        <i class="fa-solid fa-circle-plus fa-xl"></i>
      </button> -->
      </div>
    </div>

    <ColumnList
      :initialColumns="localTable.columns"
      :dataTypes="dataTypes"
      :commentable="commentable"
      :mode="getMode"
      @columns:changed="changeColumns" />

    <div class="form-group mb-2">
        <p class="font-weight-bold mb-2">Generated SQL</p>
        <div ref="editor" style="height: 30vh"></div>
    </div>
  </div>
</template>

<script>
import dialects from "./dialect-data.mjs";
export default {
  name: "SchemaEditor",
  props: {
    // pass dbrefs here so that we can make api calls
    mode: String,
    dialect: String,
    schema: String,
    table: String,
    tab_id: String,
    database_index: String, //really?
    database_name: String,
    tree_node: Object
  },
  components: {
    'ColumnList': Vue.defineAsyncComponent(() => loadModule('/static/assets/js/vuejs/components/SchemaEditorColumnList.vue', options)),
  },
  setup(props) {
    // FIXME: do we really need validations here?
    return {
      v$: Vuelidate.useVuelidate()
    }
  },
  data() {
    return {
        // TODO: improve this
        // 2 - for postgres - store type and its alias as a single item to reduce dropdown length
        dialectData: {},
        knex: null,
        schemas: [],
        customTypes: [],
        localTable: {},
        initialTable: {
          tableName: 'newTable',
          schema: '',
          columns: [{
            dataType: 'autoincrement',
            name: 'id',
            defaultValue: 0,
            nullable: false,
            isPK: true,
            comment: null
          }]
        },
        generatedSQL: '',
        hasChanges: false,
        queryIsRunning: false
    };
  },
  mounted() {
    // the "client" parameter is a bit misleading here,
    // we do not connect to any db from Knex, just setting
    // the correct SQL dialect with this option
    this.knex = window.require('knex')({ client: this.dialect })
    this.loadDialectData(this.dialect)
    this.setupEditor()
    if(this.$props.mode==='alter') {
      this.loadTableDefinition()
      // localTable for ALTER case is being set via watcher
    } else {
      this.localTable = {...this.initialTable}
    }
  },
  methods: {
    loadDialectData(dialect) {
      this.dialectData = dialects[dialect]

      if(dialect === 'postgres') {
        axios.post('/get_schemas_postgresql/', {
          database_index: this.database_index,
          tab_id: this.tab_id
        })
        .then((response) => {
          this.schemas = response.data.data.map((schema) => {return schema.name})
        })
        .catch((error) => {
          console.log(error)
        })

        axios.post('/get_types_postgresql/', {
          p_database_index: this.database_index, //ARRGH!!! change to normal param name
          p_tab_id: this.tab_id,
          p_schema: this.schema
        })
        .then((response) => {
          this.customTypes = response.data.v_data.map((type) => {return type.v_type_name})
        })
        .catch((error) => {
          console.log(error)
        })
      }
    },
    loadTableDefinition() {
        // FIXME: this should be database-agnostic
        axios.post('/get_table_definition_postgresql/', {
          database_index: this.database_index,
          tab_id: this.tab_id,
          table: this.table,
          schema: this.schema
        })
        .then((response) => {
          let coldefs = response.data.data.map((col) => {
            return {
              dataType: col.data_type,
              name: col.name,
              defaultValue: 0,
              nullable: col.nullable,
              isPK: col.is_primary,
              comment: null, //TBD
            }
          })
          this.initialTable.columns = coldefs
          this.initialTable.tableName = this.$props.table
          this.initialTable.schema = this.$props.schema
        })
        .catch((error) => {
          console.log(error)
        })
    },
    setupEditor() {
      this.editor = ace.edit(this.$refs.editor);
      this.editor.setTheme("ace/theme/" + window.v_editor_theme);
      this.editor.session.setMode("ace/mode/sql");
      this.editor.setFontSize(Number(window.v_font_size));
      this.editor.$blockScrolling = Infinity;
      this.editor.clearSelection();
      this.editor.setReadOnly(true);
    },
    generateSQL() {
      //add knex error handing with notification to the user
      let tabledef = this.localTable
      let k = this.knex.schema.withSchema(tabledef.schema)
      this.hasChanges = false
      if(this.mode === 'alter') {
        let changes = {
          'adds': [],
          'drops': [],
          'typeChanges': [],
          'nullableChanges': [],
          'dropNulls': [],
          'defaults': [],
          'renames': [],
        }

        let originalColumns = this.initialTable.columns
        this.localTable.columns.forEach((column, idx) => {
          if(column.deleted) changes.drops.push(column.name)
          if(column.new) changes.adds.push(column)
          if(column.deleted || column.new) return //no need to do further steps for new or deleted cols
          if(column.dataType !== originalColumns[idx].dataType) changes.typeChanges.push(column)
          if(column.nullable !== originalColumns[idx].nullable) changes.nullableChanges.push(column)
          if(column.defaultValue !== originalColumns[idx].defaultValue) changes.defaults.push(column)
          if(column.name !== originalColumns[idx].name) changes.renames.push({'oldName': originalColumns[idx].name, 'newName': column.name})
        })

        // we use initial table name here since localTable.tableName may be changed
        // which results in broken SQL
        let knexOperations = k.alterTable(this.initialTable.tableName, function(table) {
          changes.adds.forEach((coldef) => {
            // use Knex's magic to create a proper auto-incrementing column in database-agnostic way
            let col = coldef.dataType === 'autoincrement' ?
              table.increments(coldef.name) :
              table.specificType(coldef.name, coldef.dataType)

            coldef.nullable ? col.nullable() : col.notNullable()

            if(coldef.defaultValue) col.defaultTo(coldef.defaultValue)
            if(coldef.comment) col.comment(coldef.comment)
          })

          if(changes.drops.length) table.dropColumns(changes.drops)
          changes.typeChanges.forEach((coldef) => {
            if(coldef.dataType === 'autoincrement') {
              table.increments(coldef.name).alter()
            }else {
              table.specificType(coldef.name, coldef.dataType).defaultTo(coldef.defaultValue).alter({alterNullable : false})
            }
          })
          changes.dropNulls.forEach((coldef) => {
            coldef.nullable ? col.setNullable() : col.dropNullable()
          })
          changes.renames.forEach((rename) => {
            table.renameColumn(rename.oldName, rename.newName)
          })
        })

        // handle table rename last
        if(this.initialTable.tableName !== this.localTable.tableName) {
          knexOperations.renameTable(this.initialTable.tableName, this.localTable.tableName)
        }
        this.generatedSQL = knexOperations.toQuery()

      } else {
        this.generatedSQL = k.createTable(tabledef.tableName, function (table) {
          tabledef.columns.forEach((coldef) => {
            // use Knex's magic to create a proper auto-incrementing column in database-agnostic way
            let col = coldef.dataType === 'autoincrement' ?
              table.increments(coldef.name) :
              table.specificType(coldef.name, coldef.dataType)

            coldef.nullable ? col.nullable() : col.notNullable()

            if(coldef.defaultValue) col.defaultTo(coldef.defaultValue)
            if(coldef.comment) col.comment(coldef.comment)
          })

          // generate PKs
          let pkCols = tabledef.columns.filter((col) => col.isPK)
          if(pkCols.length > 0) {
            table.primary(pkCols.map((col) => col.name))
          }
        }).toQuery()
      }
      this.hasChanges = this.generatedSQL.length > 0
    },
    changeColumns(columns) {
      this.localTable.columns = columns
    },
    applyChanges() {
      let message_data = {
				v_sql_cmd : this.generatedSQL,
				v_sql_save : false,
				v_cmd_type: null,
				v_db_index: this.database_index,
				v_conn_tab_id: v_connTabControl.selectedTab.id,
				v_tab_id: this.tab_id,
				v_tab_db_id: this.database_index,
				v_mode: 0,
				v_all_data: false,
				v_log_query: false,
				v_tab_title: 'schema editor',
				v_autocommit: true,
				database_name: this.database_name
			}

      let context = {
				tab_tag: v_connTabControl.selectedTab.tag.tabControl.selectedTab.tag,
				cmd_type: null,
				database_index: this.database_index,
				mode: 0,
				callback: this.handleResponse,
				acked: false,
				query: this.generatedSQL,
				log_query: false,
				save_query: null,
        simple: true //a hacky way to prevent long polling handler from running legacy rentering routines
			}
      this.queryIsRunning = true
      createRequest(v_queryRequestCodes.Query, message_data, context)
    },
    handleResponse(response) {
      if(response.v_error == true) {
        this.$toast.error(this.createNotifyMessage('Failed', response.v_data.message), {
        })
      } else {
        let msg = response.v_data.v_status === "CREATE TABLE" ? `Table "${this.localTable.tableName}" created` : `Table "${this.localTable.tableName}" updated`
        this.$toast.success(this.createNotifyMessage('Done', msg), {
          duration:3000
        })
        refreshTreePostgresql(this.tree_node)
      }
      this.queryIsRunning = false
    },
    createNotifyMessage(title, desc) {
      return `<div class="v-toast__body p-0">
                  <h3 class="font-weight-bold">${title}</h3>
                  <p>${desc}</p>
              </div>`
    },
  },
  computed: {
    dataTypes() {
      // our magic datatype to generate db-specific autoincrementing column
      let rawTypes = ['autoincrement']
        .concat(this.dialectData.dataTypes)
        .concat(this.customTypes)
      return rawTypes.map((t, idx) => {return {id: idx, name: t}})
    },
    showSchema() {
      return this.mode !== 'alter' && this.dialectData.hasSchema
    },
    commentable() {
      return this.mode !== 'alter' && this.dialectData.hasComments
    },
    getMode() {
      return this.mode
    }
  },
  watch: {
    generatedSQL() {
      let format = window.sqlFormatter.format;
      this.editor.setValue(
        format(
          this.generatedSQL,
          {
            tabWidth: 2,
            keywordCase: 'upper',
            language: this.dialectData.formatterDialect,
            linesBetweenQueries: 1,
          }
      ))
      this.editor.clearSelection();
    },
    // watch initialTable for changes for cases when it is changed by requesting tabledef from the back-end
    initialTable: {
      handler(newVal, oldVal) {
        this.localTable = JSON.parse(JSON.stringify(newVal))
      },
      deep: true
    },
    // watch our local working copy for changes, generate new SQL when the change occcurs
    localTable: {
      handler(newVal, oldVal) {
        this.generateSQL()
      },
      deep: true
    }
  }
};
</script>

<style scoped>
  .schema-editor-scrollable {
    height: calc(100vh - 60px);
    overflow: hidden auto;
  }
</style>