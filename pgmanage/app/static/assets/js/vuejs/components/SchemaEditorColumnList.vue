<template>
<span>
  <div class="card mb-2">
    <div class="card-body p-0">
      <ul class="list-group list-group-flush form-group rounded-0">
        <li class="list-group-item d-flex row no-gutters font-weight-bold">
          <div class="col-3">Name</div>
          <div class="col-2">Type</div>
          <div class="col-3">Default</div>
          <div class="col-1">Nullable</div>
          <div class="col-1">Primary Key</div>
          <div v-if="commentable" class="col">Comment</div>
          <div class="col">Actions</div>
        </li>
        <li v-for="(column, index) in columns" :key="column.index"
        :class="['list-group-item d-flex row no-gutters', { 'row-deleted': column.deleted }, { 'row-new': column.new }]">
              <div class="col-3">
                  <input v-model="column.name" class="form-control mb-0" placeholder="column name..." />
              </div>

              <div class="col-2">
                <SearchableDropdown
                  placeholder="type to search"
                  :options="dataTypes"
                  :default="{ name: 'integer' }"
                  :maxItem=20
                  v-model="column.dataType"
                />
              </div>

              <div class="col-3">
                <input v-model="column.defaultValue" class="form-control mb-0" placeholder="NULL" />
              </div>

              <div class="col-1">
                <input type='checkbox' v-model="column.nullable" class="form-control mb-0" />
              </div>

              <div class="col-1">
                <input type='checkbox' v-model="column.isPK" class="form-control mb-0" />
              </div>
              <div v-if="commentable" class="col">
                <input v-model="column.comment" class="form-control mb-0" placeholder="column comment.." />
              </div>
              <div class="col">
                <button v-if="!column.deleted" @click='removeColumn(index)' class="float-right btn btn-outline-danger">
                  <i class="fas fa-circle-xmark"></i>
                </button>

                <button v-if="column.deleted && !column.new" @click='column.deleted = false' class="float-right btn btn-outline-success">
                  <i class="fas fa-rotate-left"></i>
                </button>

                <button v-if="this.movable(column)" @click='moveColumnUp(index)' class="float-right btn btn-outline-secondary">
                  <i class="fas fa-circle-up"></i>
                </button>

                <button v-if="this.movable(column)" @click='moveColumnDown(index)' class="float-right btn btn-outline-secondary">
                  <i class="fas fa-circle-down"></i>
                </button>
              </div>
        </li>
        <li class="list-group-item d-flex row no-gutters font-weight-bold">
          <div class="col">
            <button @click='addColumn' class="float-right btn btn-sm btn-outline-success">
              Add Column
            </button>
          </div>
        </li>
      </ul>

    </div>
  </div>
  </span>
</template>

<script>
  export default {
    name: 'SchemaEditorColumnList',
    data() {
      return {
        columns: [],
        value:'',
        options: ['Select option', 'options', 'selected', 'multiple', 'label', 'searchable', 'clearOnSelect', 'hideSelected', 'maxHeight', 'allowEmpty', 'showLabels', 'onChange', 'touched']
      }
    },
    components: {
      'SearchableDropdown': Vue.defineAsyncComponent(() => loadModule('/static/assets/js/vuejs/components/SearchableDropdown.vue', options)),
    },
    props: {
      initialColumns: Array,
      commentable: Boolean,
      mode: String,
      dataTypes: Array,
    },
    emits: ["columns:changed"],
    methods: {
      addColumn() {
        let colName = `column-${this.columns.length}`
        const defaultCol = {
          dataType: 'integer',
          name: colName,
          defaultValue: 0,
          nullable: false,
          isPK: false,
          comment:null,
          new: this.mode === 'alter'
        }
        this.columns.push(defaultCol)
      },
      movable(column) {
        //all columns are movable when creating a new table
        if(this.mode !== 'alter') return true;
        if(column.new) return true;
      },
      removeColumn(index) {
        if(this.mode === 'alter' && !this.columns[index].new) {
          this.columns[index].deleted = true;
        } else {
          this.columns.splice(index, 1)
        }
      },
      moveColumnUp(index) {
        // prevent moving newly added column above existing ones in "alter" mode
        if(index == 0) return;
        if(this.mode === 'alter') {
          let colAbove = this.columns[index-1]
          if(!colAbove.new) return;
        }
        let col = this.columns.splice(index, 1)[0]
        this.columns.splice(index-1, 0, col)
      },
      moveColumnDown(index) {
        if(index == this.columns.length-1) return;
        let col = this.columns.splice(index, 1)[0]
        this.columns.splice(index+1, 0, col)
      },
      // setDataType(selected) {
      //   this.
      // }
    },
    watch: {
      initialColumns: {
        handler(newVal, oldVal) {
          this.columns = newVal
        },
        immediate: true
      },
      columns: {
        handler(newVal, oldVal) {
          this.$emit('columns:changed', newVal)
        },
        deep: true
      }
    }
  }
</script>