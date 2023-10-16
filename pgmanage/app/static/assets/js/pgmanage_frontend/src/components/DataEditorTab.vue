<template>
<div class="data-editor">
  <div class="form-row">
    <div class="form-group col-9">
      <form class="form" @submit.prevent>
        <label class="mb-2" for="selectServer">
          <span class="font-weight-bold">Filter</span> <span class='text-info'> select</span> * <span class='text-info'>from</span> {{this.schema}}.{{this.table}} t
        </label>
        <input v-model.trim="query_filter" class="form-control" name="filter"
           placeholder="extra filter criteria" />
      </form>
    </div>
    <div class="form-group col-2">
      <form class="form" @submit.prevent>
        <label class="font-weight-bold mb-2" for="selectServer">Limit</label>
        <select v-model="row_limit" class="form-control">
            <option v-for="(option, index) in [10, 100, 1000]"
              :key=index
              :value="option">
                {{option}} rows
            </option>
        </select>
      </form>
    </div>
    <div class="form-group col-1 d-flex align-items-end pl-0">
      <button class="btn btn-primary mr-2" title="Load Data" @click="getTableData()">
        <i class="fa-solid fa-filter"></i>
      </button>
    </div>
  </div>

  <div class="grid-scrollable">
    <div class="row">
      <div class="col-12">
        <hot-table ref="hotTableComponent" class='data-grid' :settings="hotSettings"></hot-table>
      </div>
    </div>
  </div>

  <div class="data-editor__footer d-flex justify-content-end align-items-center p-2">
    <button type="submit" class="btn btn-success btn-sm mr-5" :disabled="!hasChanges"
      @click.prevent="applyChanges">
      {{this.applyBtnTitle()}}
    </button>
  </div>
</div>
</template>

<script>
import axios from 'axios'
import Knex from 'knex'
import { isEqual, zipObject } from 'lodash';
import { showToast } from "../notification_control";
import { v_queryRequestCodes } from '../query'
import { createRequest } from '../long_polling'
import { HotTable } from '@handsontable/vue3';
import { TextEditor } from 'handsontable/editors/textEditor';
import { registerAllModules } from 'handsontable/registry';

// register Handsontable's modules, needed for column auto-sizing
registerAllModules();


class CustomEditor extends TextEditor {
  constructor(props) {
    super(props);
  }

  createElements() {
    super.createElements();

    this.TEXTAREA = document.createElement('input');
    this.TEXTAREA.setAttribute('placeholder', 'Custom placeholder');
    this.TEXTAREA.setAttribute('data-hot-input', true);
    this.textareaStyle = this.TEXTAREA.style;
    this.TEXTAREA_PARENT.innerText = '';
    this.TEXTAREA_PARENT.appendChild(this.TEXTAREA);
  }
}

export default {
  name: "DataEditorTab",
  components: {
    HotTable,
  },
  props: {
    dialect: String,
    schema: String,
    table: String,
    tab_id: String,
    database_index: Number,
    database_name: String,
    initial_filter: {
      type: String,
    default: ''
    }
  },
  setup() {

  },
  data() {
    return {
      knex: null,
      tableColumns: [],
      tableData: [],
      tableDataLocal: [],
      query_filter: '',
      row_limit: 10
    };
  },
  computed: {
    hotSettings(){
      return {
        licenseKey: 'non-commercial-and-evaluation',
        manualColumnResize: true,
        fixedColumnsLeft: 2,
        minSpareRows: 0,
        width: '100%',
        height: 'calc(100vh - 210px)',
        editor: CustomEditor,
        renderer: function(instance, td, row, col, prop, value, cellProperties) {
          let newValue = value
          if(value) {
            // truncate displayed cell data to reduce column width
            if(value.length > 100)
              newValue = `${value.substring(0,120)}...`
          }

          arguments[5] = newValue
          Handsontable.renderers.TextRenderer.apply(this, arguments);

          let rowMeta = instance.getDataAtCell(row, 0)
          if(rowMeta) {
            if(rowMeta.is_dirty)
              td.classList.add('row-dirty')
            if(rowMeta.is_deleted)
              td.classList.add('row-deleted')
            if(rowMeta.is_new)
              td.classList.add('row-new')
          }
        }
      }
    },
    hasChanges() {
      return this.pendingChanges.length > 0
    },
    pendingChanges() {
      return this.tableDataLocal.filter((row) => row[0].is_dirty || row[0].is_new || row[0].is_deleted)
    },
  },
  mounted() {
    this.knex = Knex({ client: this.dialect || 'postgres'})
    this.getTableColumns().then(this.getTableData)
  },
  methods: {
    actionsRenderer(hotInstance, td, row, column, prop, value, cellProperties) {
      const div = document.createElement('div');
      div.className = 'btn p-0';

      let cellData = value
      if(!cellData)
        return
      if(cellData.is_deleted || cellData.is_dirty) {
        const revertIcon = document.createElement('i')
        revertIcon.className = 'fas fa-rotate-left text-info'
        revertIcon.title = 'Revert'
        revertIcon.dataset.action = 'revert'
        div.appendChild(revertIcon);

      } else {
        const deleteIcon = document.createElement('i')
        deleteIcon.className = 'fas fa-circle-xmark text-danger'
        deleteIcon.title = 'Remove'
        deleteIcon.dataset.action = 'delete'
        div.appendChild(deleteIcon)
      }

      td.innerText = '' //don't show the actual contents of the cell

      let cellClass = ''
      if(cellData.is_dirty)
        cellClass = 'row-dirty'
      if(cellData.is_deleted)
        cellClass = 'row-deleted'
      if(cellData.is_new)
        cellClass = 'row-new'
      td.className = `'cellReadOnly' ${cellClass}`
      td.appendChild(div);
    },
    colHeaders(colIndex) {
      // TODO: can we render this with vue somehow?
      if(colIndex === 0)
        return `<div data-action="add" class="btn p-0" title="Add column">
        <i data-action="add" class="fa-solid fa-circle-plus text-success"></i>
        </div>`

      let col = this.tableColumns[colIndex-1]
      if(col) {
        let prepend = col.is_primary ? '<i class="fas fa-key action-key text-secondary mr-1"></i>' : ''
        return `${prepend}<span>${col.name}</span><div class='font-weight-light'>${col.data_type}</div>`
      }
      return ''
    },
    getTableColumns() {
      return axios
        .post("/get_table_columns/", {
          database_index: this.database_index,
          tab_id: this.tab_id,
          schema: this.schema,
          table: this.table
        })
        .then((response) => {
          this.tableColumns = response.data.columns
          this.query_filter = `${this.$props.initial_filter} ${response.data.initial_orderby}`.trim()
        })
        .catch((error) => {
          showToast("error", error.response.data)
        });
    },
    getTableData() {
      var message_data = {
        v_table: this.table,
        v_schema: this.schema,
        v_db_index: this.database_index,
        v_filter : this.query_filter,
        v_count: this.row_limit,
        v_conn_tab_id: v_connTabControl.selectedTab.id,
        v_tab_id: this.tab_id
      }

      var context = {
        tab_tag: null,
        callback: this.handleResponse.bind(this),
        start_time: new Date().getTime(),
        database_index: this.database_index
      }

      createRequest(40, message_data, context)//TODO: add proper name for the request code
      let actionsCol = {
        readOnly: true,
        renderer: this.actionsRenderer
      }
      let columns = this.tableColumns.map((c) => { editor: CustomEditor })
      columns.unshift(actionsCol)

      this.$refs.hotTableComponent.hotInstance.updateSettings({
        colHeaders: this.colHeaders,
        autoColumnSize: {syncLimit: 300, useHeaders: true},
        columns: columns,
      })

      this.$refs.hotTableComponent.hotInstance.addHook('afterOnCellMouseDown', (function(event, coords, TD){
        let action_type = event.target.dataset.action
        let hotInstance = this.$refs.hotTableComponent.hotInstance

        if(action_type) {
          let rowMeta = hotInstance.getDataAtCell(coords.row,coords.col)
          if(action_type === 'delete')
            this.deleteRow(rowMeta, coords.row)
          if(action_type === 'revert')
            this.revertRow(rowMeta, coords.row)
          if(action_type === 'add')
            this.addRow()
          }
        }).bind(this))

      this.$refs.hotTableComponent.hotInstance.addHook('afterChange', (function(changes, source) {
        if(source === 'edit') {
          let hotInstance = this.$refs.hotTableComponent.hotInstance
          //changes are [[row prop old new]]
          changes.forEach((change) => {
            let rowNum = change[0]
            let rowData = hotInstance.getDataAtRow(rowNum)
            let rowMeta = hotInstance.getDataAtCell(rowNum,0)
            let originalRow = this.tableData.find((row) => row[0].initial_id == rowMeta.initial_id)
            rowMeta.is_dirty = false //set to false for proper comparison with the original
            rowMeta.is_dirty = !isEqual(rowData, originalRow) && !rowMeta.is_new
          })
        }
      }).bind(this))

      // FIXME: move hooks to some plase where they are attached once, otherwise multiple invocations happen
      this.$refs.hotTableComponent.hotInstance.addHook('afterOnCellMouseDown', (function(event, coords, TD){
        let hotInstance = this.$refs.hotTableComponent.hotInstance
        // disables highlight of actions column
        if (coords.col == 0){
          hotInstance.deselectCell(coords.row, coords.col);
        }
      }).bind(this))
    },
    handleResponse(response) {
      if(response.v_error == true) {
        showToast("error", response.v_data.message)
      } else {
        //store table data into original var, clone it to the working copy
        let pkIndex = this.tableColumns.findIndex((col) => col.is_primary) || 0
        this.tableData = response.v_data.rows.map((row) => {
          let rowMeta = {
            is_dirty: false,
            is_new: false,
            is_deleted: false,
            initial_id: row[pkIndex]
          }

          return [rowMeta].concat(row)
        })
        this.tableDataLocal = JSON.parse(JSON.stringify(this.tableData))
        this.$refs.hotTableComponent.hotInstance.updateData(this.tableDataLocal);
      }
    },
    handleSaveResponse(response) {
      if(response.v_error == true) {
        showToast("error", response.v_data.message)
      } else {
        // let msg = response.v_data.v_status === "CREATE TABLE" ? `Table "${this.localTable.tableName}" created` : `Table "${this.localTable.tableName}" updated`
        showToast("success", 'data updated')
        this.getTableData()
      }
    },
    addRow() {
      let newRow = Array(this.tableColumns.length + 1).fill(null) //+1 adds an extra actions column
      let rowMeta = {
        is_dirty: false,
        is_new: true,
        is_deleted: false,
        initial_id: -1
      }

      newRow[0] = rowMeta
      this.tableDataLocal.unshift(newRow)
      this.$refs.hotTableComponent.hotInstance.selectCell(0, 2)
      // this.$refs.hotTableComponent.hotInstance.deselectCell(0, 1)
    },
    revertRow(rowMeta,rowNum) {
      let sourceRow = this.tableData.find((row) => row[0].initial_id == rowMeta.initial_id)
      this.tableDataLocal[rowNum] = JSON.parse(JSON.stringify(sourceRow))
    },
    deleteRow(rowMeta,rowNum) {
      if(rowMeta.is_new) {
        this.tableDataLocal.splice(rowNum, 1)
      } else {
        this.tableDataLocal[rowNum][0].is_deleted = true
      }
    },
    generateSQL() {
      let colNames = this.tableColumns.map(c => c.name)
      let deletes = []
      let inserts = []
      let updates = []
      let changes = this.pendingChanges
      let pkColName = this.tableColumns.find((col) => col.is_primary).name || 'id'

      changes.forEach(function(change) {
        let rowMeta = change[0]
        if(rowMeta.is_new) {
          inserts.push(zipObject(colNames, change.slice(1)))
        }
        if(rowMeta.is_dirty){
          let originalRow = this.tableData.find((row) => row[0].initial_id == rowMeta.initial_id).slice(1)
          let updateArgs = {}

          change.slice(1).forEach((changedCol, idx) => {
            if(changedCol!==originalRow[idx]) {
              updateArgs[colNames[idx]] = changedCol
            }
          })

          updates.push(this.knex(this.table).where(pkColName, rowMeta.initial_id).update(updateArgs))
        }
      }, this)

      let deletableIds = changes.filter((c) => c[0].is_deleted).map((c) => {return c[0].initial_id})
      if(deletableIds.length > 0)
        deletes.push(this.knex(this.table).whereIn(pkColName, deletableIds).del())

      let insQ = []
      if(inserts.length)
        insQ = this.knex(this.table).insert(inserts)

      return [].concat(updates, insQ, deletes, '').join(';\n')
    },
    applyChanges() {
      let query = this.generateSQL()

      let message_data = {
        v_sql_cmd : query,
        v_sql_save : false,
        v_db_index: this.database_index,
        v_conn_tab_id: v_connTabControl.selectedTab.id,
        v_tab_id: this.tab_id,
        v_tab_db_id: this.database_index,
        // v_mode: 0,
        // v_all_data: false,
        // v_log_query: false,
        // v_tab_title: 'schema editor',
        // v_autocommit: true,
        // database_name: this.database_name
      }

      let context = {
        callback: this.handleSaveResponse.bind(this),
      }

      createRequest(v_queryRequestCodes.SaveEditDataNew, message_data, context)
    },
    applyBtnTitle() {
      let count = this.pendingChanges.length

      if(count === 0)
        return 'No Changes'
      return `Apply ${count} ${(count > 1 || count == 0) ? 'changes' : 'change'}`
    }
  },
  watch: {
    tableDataLocal: {
      handler(newVal, oldVal) {
        this.$refs.hotTableComponent.hotInstance.updateData(this.tableDataLocal);
      },
      deep: true
    },
  }
};
</script>

<style scoped>
  .grid-scrollable {
    width: 100%;
  }
</style>
