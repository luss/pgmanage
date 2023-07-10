<template>
  <PowerTree ref="tree" v-model="nodes" @nodedblclick="doubleClickNode" @toggle="onToggle"
    @nodecontextmenu="onContextMenu" :allow-multiselect="false">
    <template v-slot:toggle="{ node }">
      <i v-if="node.isExpanded" class="exp_col fas fa-chevron-down"></i>
      <i v-if="!node.isExpanded" class="exp_col fas fa-chevron-right"></i>
    </template>

    <template v-slot:title="{ node }">
      <span class="item-icon">
        <i :class="['icon_tree', node.data.icon]"></i>
      </span>
      <span v-if="node.data.raw_html" v-html="node.title"> </span>
      <span v-else>
        {{ node.title }}
      </span>
    </template>
  </PowerTree>
</template>

<script>
const { PowerTree } = window["VuePowerTree"];

export default {
  name: "SqliteTree",
  components: {
    PowerTree,
  },
  props: {
    databaseIndex: {
      type: Number,
      required: true,
    },
    tabId: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      nodes: [
        {
          title: "Sqlite",
          isExpanded: false,
          isDraggable: false,
          data: {
            icon: "node-sqlite",
            type: "server",
            contextMenu: "cm_server",
          },
        },
      ],
    };
  },
  computed: {
    cmRefreshObject() {
      return {
        label: "Refresh",
        icon: "fas cm-all fa-sync-alt",
        onClick: this.refreshNode,
      };
    },
    contextMenu() {
      return {
        cm_server: [this.cmRefreshObject],
        cm_tables: [
          this.cmRefreshObject,
          {
            label: "Create Table",
            icon: "fas cm-all fa-edit",
            onClick: () => {
              tabSQLTemplate("Create Table", this.templates.create_table);
            },
          },
        ],
        cm_table: [
          this.cmRefreshObject,
          {
            label: "Data Actions",
            icon: "fas cm-all fa-list",
            children: [
              {
                label: "Query Data",
                icon: "fas cm-all fa-search",
                onClick: () => {
                  const node = this.getSelectedNode();
                  TemplateSelectSqlite(node.title, "t");
                },
              },
              {
                label: "Edit Data",
                icon: "fas cm-all fa-table",
                onClick: () => {
                  const node = this.getSelectedNode();
                  v_startEditData(node.title);
                },
              },
              {
                label: "Insert Record",
                icon: "fas cm-all fa-edit",
                onClick: () => {
                  const node = this.getSelectedNode();
                  TemplateInsertSqlite(node.title);
                },
              },
              {
                label: "Update Records",
                icon: "fas cm-all fa-edit",
                onClick: () => {
                  const node = this.getSelectedNode();
                  TemplateUpdateSqlite(node.title);
                },
              },
              {
                label: "Delete Records",
                icon: "fas cm-all fa-times",
                onClick: () => {
                  const node = this.getSelectedNode();
                  tabSQLTemplate(
                    "Delete Records",
                    this.templates.delete.replace("#table_name#", node.title)
                  );
                },
              },
            ],
          },
          {
            label: "Table Actions",
            icon: "fas cm-all fa-list",
            children: [
              {
                label: "Alter Table",
                icon: "fas cm-all fa-edit",
                onClick: () => {
                  const node = this.getSelectedNode();
                  tabSQLTemplate(
                    "Alter Table",
                    this.templates.alter_table.replace(
                      "#table_name#",
                      node.title
                    )
                  );
                },
              },
              {
                label: "Drop Table",
                icon: "fas cm-all fa-times",
                onClick: () => {
                  const node = this.getSelectedNode();
                  tabSQLTemplate(
                    "Drop Table",
                    this.templates.drop_table.replace(
                      "#table_name#",
                      node.title
                    )
                  );
                },
              },
            ],
          },
        ],
        cm_columns: [
          this.cmRefreshObject,
          {
            label: "Create Column",
            icon: "fas cm-all fa-edit",
            onClick: () => {
              const node = this.getSelectedNode();
              tabSQLTemplate(
                "Create Column",
                this.templates.create_column.replace(
                  "#table_name#",
                  this.getParentNode(node).title
                )
              );
            },
          },
        ],
        cm_column: [],
        cm_pks: [this.cmRefreshObject],
        cm_pk: [this.cmRefreshObject],
        cm_fks: [this.cmRefreshObject],
        cm_fk: [this.cmRefreshObject],
        cm_uniques: [this.cmRefreshObject],
        cm_unique: [this.cmRefreshObject],
        cm_indexes: [
          this.cmRefreshObject,
          {
            label: "Create Index",
            icon: "fas cm-all fa-edit",
            onClick: () => {
              const node = this.getSelectedNode();
              tabSQLTemplate(
                "Create Index",
                this.templates.create_index.replace(
                  "#table_name#",
                  this.getParentNode(node).title
                )
              );
            },
          },
        ],
        cm_index: [
          this.cmRefreshObject,
          {
            label: "Reindex",
            icon: "fas cm-all fa-edit",
            onClick: () => {
              // Fix THIS
              const node = this.getSelectedNode();
              tabSQLTemplate(
                "Reindex",
                this.templates.reindex.replace(
                  "#index_name#",
                  node.title
                    .replace(" (Unique)", "")
                    .replace(" (Non Unique)", "")
                )
              );
            },
          },
          {
            label: "Drop Index",
            icon: "fas cm-all fa-times",
            onClick: () => {
              const node = this.getSelectedNode();
              // Fix THIS
              tabSQLTemplate(
                "Drop Index",
                this.templates.drop_index.replace(
                  "#index_name#",
                  node.title
                    .replace(" (Unique)", "")
                    .replace(" (Non Unique)", "")
                )
              );
            },
          },
        ],
        cm_triggers: [
          this.cmRefreshObject,
          {
            label: "Create Trigger",
            icon: "fas cm-all fa-edit",
            onClick: () => {
              const node = this.getSelectedNode();
              tabSQLTemplate(
                "Create Trigger",
                this.templates.create_trigger.replace(
                  "#table_name#",
                  this.getParentNode(node).title
                )
              );
            },
          },
        ],
        cm_trigger: [
          {
            label: "Drop Trigger",
            icon: "fas cm-all fa-times",
            onClick: () => {
              const node = this.getSelectedNode();
              tabSQLTemplate(
                "Drop Trigger",
                this.templates.drop_trigger
                  .replace(
                    "#table_name#",
                    this.getParentNode(this.getParentNode(node)).title
                  )
                  .replace("#trigger_name#", node.title)
              );
            },
          },
        ],
        cm_views: [
          this.cmRefreshObject,
          {
            label: "Create View",
            icon: "fas cm-all fa-edit",
            onClick: () => {
              tabSQLTemplate("Create View", this.templates.create_view);
            },
          },
        ],
        cm_view: [
          this.cmRefreshObject,
          {
            label: "Query Data",
            icon: "fas cm-all fa-search",
            onClick: () => {
              const node = this.getSelectedNode();

              TemplateSelectSqlite(node.title, "v");
            },
          },
          {
            label: "Drop View",
            icon: "fas cm-all fa-times",
            onClick: () => {
              const node = this.getSelectedNode();
              tabSQLTemplate(
                "Drop View",
                this.templates.drop_view.replace("#view_name#", node.title)
              );
            },
          },
        ],
      };
    },
  },
  methods: {
    onToggle(node, e) {
      this.$refs.tree.select(node.path);
      if (node.isExpanded) return;
      this.refreshTreeSqlite(node);
    },
    doubleClickNode(node, e) {
      if (node.isLeaf) return;
      this.onToggle(node);
      this.toggleNode(node);
    },
    onContextMenu(node, e) {
      this.$refs.tree.select(node.path);
      e.preventDefault();
      window["vue3-context-menu"].default.showContextMenu({
        theme: "pgmanage",
        x: e.x,
        y: e.y,
        zIndex: 1000,
        minWidth: 230,
        items: this.contextMenu[node.data.contextMenu],
      });
    },
    refreshTreeSqlite(node) {
      if (node.children.length == 0) this.insertSpinnerNode(node);
      if (node.data.type == "server") {
        this.getTreeDetailsSqlite(node);
      } else if (node.data.type == "table_list") {
        this.getTablesSqlite(node);
      } else if (node.data.type == "table") {
        this.getColumnsSqlite(node);
      } else if (node.data.type == "primary_key") {
        this.getPKSqlite(node);
      } else if (node.data.type == "pk") {
        this.getPKColumnsSqlite(node);
      } else if (node.data.type == "foreign_keys") {
        this.getFKsSqlite(node);
      } else if (node.data.type == "foreign_key") {
        this.getFKsColumnsSqlite(node);
      } else if (node.data.type == "uniques") {
        this.getUniquesSqlite(node);
      } else if (node.data.type == "unique") {
        this.getUniquesColumnsSqlite(node);
      } else if (node.data.type == "indexes") {
        this.getIndexesSqlite(node);
      } else if (node.data.type == "index") {
        this.getIndexesColumnsSqlite(node);
      } else if (node.data.type == "trigger_list") {
        this.getTriggersSqlite(node);
      } else if (node.data.type == "view_list") {
        this.getViewsSqlite(node);
      } else if (node.data.type == "view") {
        this.getViewsColumnsSqlite(node);
      }
    },
    getTreeDetailsSqlite(node) {
      axios
        .post("/get_tree_info_sqlite/", {
          database_index: this.databaseIndex,
          tab_id: this.tabId,
        })
        .then((resp) => {
          this.removeChildNodes(node);
          this.$refs.tree.updateNode(node.path, {
            title: resp.data.version,
          });
          this.templates = resp.data;

          this.insertNode(node, "Views", {
            icon: "fas node-all fa-eye node-view-list",
            type: "view_list",
            contextMenu: "cm_views",
          });
          this.insertNode(node, "Tables", {
            icon: "fas node-all fa-th node-table-list",
            type: "table_list",
            contextMenu: "cm_tables",
          });
        })
        .catch((error) => {
          showError(error.response.data.data);
        });
    },
    getTablesSqlite(node) {
      axios
        .post("/get_tables_sqlite/", {
          database_index: this.databaseIndex,
          tab_id: this.tabId,
        })
        .then((resp) => {
          this.removeChildNodes(node);
          this.$refs.tree.updateNode(node.path, {
            title: `Tables (${resp.data.length})`,
          });

          resp.data.forEach((el) => {
            this.insertNode(node, el, {
              icon: "fas node-all fa-table node-table",
              type: "table",
              contextMenu: "cm_table",
            });
          });
        })
        .catch((error) => {
          showError(error.response.data.data);
        });
    },
    getColumnsSqlite(node) {
      axios
        .post("/get_columns_sqlite/", {
          database_index: this.databaseIndex,
          tab_id: this.tabId,
          table: node.title,
        })
        .then((resp) => {
          this.removeChildNodes(node);

          this.insertNode(node, "Triggers", {
            icon: "fas node-all fa-bolt node-trigger",
            type: "trigger_list",
            contextMenu: "cm_triggers",
          });
          this.insertNode(node, "Indexes", {
            icon: "fas node-all fa-thumbtack node-index",
            type: "indexes",
            contextMenu: "cm_indexes",
          });
          this.insertNode(node, "Uniques", {
            icon: "fas node-all fa-key node-unique",
            type: "uniques",
            contextMenu: "cm_uniques",
          });
          this.insertNode(node, "Foreign Keys", {
            icon: "fas node-all fa-key node-fkey",
            type: "foreign_keys",
            contextMenu: "cm_fks",
          });
          this.insertNode(node, "Primary Key", {
            icon: "fas node-all fa-key node-pkey",
            type: "primary_key",
            contextMenu: "cm_pks",
          });
          this.insertNode(node, `Columns (${resp.data.length})`, {
            icon: "fas node-all fa-columns node-column",
            type: "column_list",
            contextMenu: "cm_columns",
          });
          const columns_node = this.getFirstChildNode(node);
          resp.data.reduceRight((_, el) => {
            this.insertNode(columns_node, el.column_name, {
              icon: "fas node-all fa-columns node-column",
              type: "table_field",
              contextMenu: "cm_column",
            });
            const table_field = this.getFirstChildNode(columns_node);

            this.insertNode(
              table_field,
              `Nullable: ${el.nullable}`,
              {
                icon: "fas node-all fa-ellipsis-h node-bullet",
              },
              true
            );
            this.insertNode(
              table_field,
              `Type: ${el.data_type}`,
              {
                icon: "fas node-all fa-ellipsis-h node-bullet",
              },
              true
            );
          }, null);
        })
        .catch((error) => {
          showError(error.response.data.data);
        });
    },
    getPKSqlite(node) {
      axios
        .post("/get_pk_sqlite/", {
          database_index: this.databaseIndex,
          tab_id: this.tabId,
          table: this.getParentNode(node).title,
        })
        .then((resp) => {
          this.removeChildNodes(node);
          this.$refs.tree.updateNode(node.path, {
            title: `Primary Key (${resp.data.length})`,
          });

          resp.data.forEach((el) => {
            this.insertNode(node, el, {
              icon: "fas node-all fa-key node-pkey",
              type: "pk",
              contextMenu: "cm_pk",
            });
          });
        })
        .catch((error) => {
          showError(error.response.data.data);
        });
    },
    getPKColumnsSqlite(node) {
      const table_node = this.getParentNode(this.getParentNode(node));
      axios
        .post("/get_pk_columns_sqlite/", {
          database_index: this.databaseIndex,
          tab_id: this.tabId,
          table: table_node.title,
        })
        .then((resp) => {
          this.removeChildNodes(node);
          resp.data.forEach((el) => {
            this.insertNode(
              node,
              el,
              {
                icon: "fas node-all fa-columns node-column",
              },
              true
            );
          });
        });
    },
    getFKsSqlite(node) {
      axios
        .post("/get_fks_sqlite/", {
          database_index: this.databaseIndex,
          tab_id: this.tabId,
          table: this.getParentNode(node).title,
        })
        .then((resp) => {
          this.removeChildNodes(node);
          this.$refs.tree.updateNode(node.path, {
            title: `Foreign Keys (${resp.data.length})`,
          });
          resp.data.reduceRight((_, el) => {
            this.insertNode(node, el, {
              icon: "fas node-all fa-key node-fkey",
              type: "foreign_key",
              contextMenu: "cm_fk",
            });
          }, null);
        })
        .catch((error) => {
          showError(error.response.data.data);
        });
    },
    getFKsColumnsSqlite(node) {
      const table_node = this.getParentNode(this.getParentNode(node));
      axios
        .post("/get_fks_columns_sqlite/", {
          database_index: this.databaseIndex,
          tab_id: this.tabId,
          table: table_node.title,
          fkey: node.title,
        })
        .then((resp) => {
          this.removeChildNodes(node);
          this.insertNode(
            node,
            `${resp.data.column_name} <i class='fas node-all fa-arrow-right'></i> ${resp.data.r_column_name}`,
            {
              icon: "fas node-all fa-columns node-column",
              raw_html: true,
            },
            true
          );
          this.insertNode(
            node,
            `Update Rule: ${resp.data.update_rule}`,
            {
              icon: "fas node-all fa-ellipsis-h node-bullet",
            },
            true
          );
          this.insertNode(
            node,
            `Delete Rule: ${resp.data.delete_rule}`,
            {
              icon: "fas node-all fa-ellipsis-h node-bullet",
            },
            true
          );
          this.insertNode(
            node,
            `Referenced Table: ${resp.data.r_table_name}`,
            {
              icon: "fas node-all fa-table node-table",
            },
            true
          );
        })
        .catch((error) => {
          showError(error.response.data.data);
        });
    },
    getUniquesSqlite(node) {
      axios
        .post("/get_uniques_sqlite/", {
          database_index: this.databaseIndex,
          tab_id: this.tabId,
          table: this.getParentNode(node).title,
        })
        .then((resp) => {
          this.removeChildNodes(node);
          this.$refs.tree.updateNode(node.path, {
            title: `Uniques (${resp.data.length})`,
          });
          resp.data.forEach((el) => {
            this.insertNode(node, el, {
              icon: "fas node-all fa-key node-unique",
              type: "unique",
              contextMenu: "cm_unique",
            });
          });
        })
        .catch((error) => {
          showError(error.response.data.data);
        });
    },
    getUniquesColumnsSqlite(node) {
      const table_node = this.getParentNode(this.getParentNode(node));
      axios
        .post("/get_uniques_columns_sqlite/", {
          database_index: this.databaseIndex,
          tab_id: this.tabId,
          table: table_node.title,
          unique: node.title,
        })
        .then((resp) => {
          this.removeChildNodes(node);
          resp.data.forEach((el) => {
            this.insertNode(
              node,
              el,
              {
                icon: "fas node-all fa-columns node-column",
              },
              true
            );
          });
        })
        .catch((error) => {
          showEror(error.response.data.data);
        });
    },
    getIndexesSqlite(node) {
      axios
        .post("/get_indexes_sqlite/", {
          database_index: this.databaseIndex,
          tab_id: this.tabId,
          table: this.getParentNode(node).title,
        })
        .then((resp) => {
          this.removeChildNodes(node);
          this.$refs.tree.updateNode(node.path, {
            title: `Indexes (${resp.data.length})`,
          });
          // add suffix to fix replace issue
          resp.data.forEach((el) => {
            this.insertNode(node, `${el.index_name} (${el.uniqueness})`, {
              icon: "fas node-all fa-thumbtack node-index",
              type: "index",
              contextMenu: "cm_index",
            });
          });
        })
        .catch((error) => {
          showEror(error.response.data.data);
        });
    },
    getIndexesColumnsSqlite(node) {
      const table_node = this.getParentNode(this.getParentNode(node));
      //FIX INDEX
      axios
        .post("/get_indexes_columns_sqlite/", {
          database_index: this.databaseIndex,
          tab_id: this.tabId,
          table: table_node.title,
          index: node.title
            .replace(" (Non Unique)", "")
            .replace(" (Unique)", ""),
        })
        .then((resp) => {
          this.removeChildNodes(node);
          resp.data.forEach((el) => {
            this.insertNode(
              node,
              el,
              {
                icon: "fas node-all fa-columns node-column",
              },
              true
            );
          });
        })
        .catch((error) => {
          showError(error.response.data.data);
        });
    },
    getTriggersSqlite(node) {
      axios
        .post("/get_triggers_sqlite/", {
          database_index: this.databaseIndex,
          tab_id: this.tabId,
          table: this.getParentNode(node).title,
        })
        .then((resp) => {
          this.removeChildNodes(node);
          this.$refs.tree.updateNode(node.path, {
            title: `Triggers (${resp.data.length})`,
          });

          resp.data.forEach((el) => {
            this.insertNode(
              node,
              el,
              {
                icon: "fas node-all fa-bolt node-trigger",
                type: "trigger",
                contextMenu: "cm_trigger",
              },
              true
            );
          });
        })
        .catch((erorr) => {
          showError(error.response.data.data);
        });
    },
    getViewsSqlite(node) {
      axios
        .post("/get_views_sqlite/", {
          database_index: this.databaseIndex,
          tab_id: this.tabId,
        })
        .then((resp) => {
          this.removeChildNodes(node);
          this.$refs.tree.updateNode(node.path, {
            title: `Views (${resp.data.length})`,
          });
          resp.data.forEach((element) => {
            this.insertNode(node, element, {
              icon: "fas node-all fa-eye node-view",
              type: "view",
              contextMenu: "cm_view",
            });
          });
        })
        .catch((error) => {
          showError(error.response.data.data);
        });
    },
    getViewsColumnsSqlite(node) {
      axios
        .post("/get_views_columns_sqlite/", {
          database_index: this.databaseIndex,
          tab_id: this.tabId,
          table: node.title,
        })
        .then((resp) => {
          this.removeChildNodes(node);

          this.insertNode(node, "Triggers", {
            icon: "fas node-all fa-bolt node-trigger",
            type: "trigger_list",
            contextMenu: "cm_view_triggers",
          });
          this.insertNode(node, `Columns (${resp.data.length})`, {
            icon: "fas node-all fa-columns node-column",
          });
          const columns_node = this.getFirstChildNode(node);

          resp.data.reduceRight((_, el) => {
            this.insertNode(columns_node, el.column_name, {
              icon: "fas node-all fa-columns node-column",
              type: "table_field",
            });
            const table_field = this.getFirstChildNode(columns_node);

            this.insertNode(
              table_field,
              `Type: ${el.data_type}`,
              {
                icon: "fas node-all fa-ellipsis-h node-bullet",
              },
              true
            );
          }, null);
        })
        .catch((error) => {
          showError(error.response.data.data);
        });
    },
    removeChildNodes(node) {
      this.$refs.tree.updateNode(node.path, { children: [] });
    },
    insertSpinnerNode(node) {
      this.insertNode(
        node,
        "",
        {
          icon: "node-spin",
        },
        true
      );
    },
    insertNode(node, title, data, isLeaf = false) {
      this.$refs.tree.insert(
        { node: node, placement: "inside" },
        {
          title: title,
          isLeaf: isLeaf,
          isExpanded: false,
          isDraggable: false,
          data: data,
        }
      );
    },
    getParentNode(node) {
      const parentNode = this.$refs.tree.getNode(node.path.slice(0, -1));
      return parentNode;
    },
    getSelectedNode() {
      return this.$refs.tree.getSelected()[0];
    },
    getFirstChildNode(node) {
      const actualNode = this.$refs.tree.getNode(node.path);
      return actualNode.children[0];
    },
    expandNode(node) {
      this.$refs.tree.updateNode(node.path, { isExpanded: true });
    },
    toggleNode(node) {
      this.$refs.tree.updateNode(node.path, { isExpanded: !node.isExpanded });
    },
    refreshNode() {
      const node = this.getSelectedNode();
      this.expandNode(node);
      this.refreshTreeSqlite(node);
    },
  },
};
</script>
