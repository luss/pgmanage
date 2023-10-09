<template>
  <splitpanes class="default-theme query-body" horizontal>
    <pane size="30">
      <QueryEditor ref="editor" class="h-100" :read-only="readOnlyEditor" :tab-id="tabId" tab-mode="query" />
    </pane>

    <pane size="70">
      <!-- ACTION BUTTONS-->
      <div class="row mb-1">
        <div class="tab-actions col-12">
          <button :id="`bt_start_${tabId}`" class="btn btn-sm btn-primary" title="Run" @click="queryRunOrExplain()">
            <i class="fas fa-play fa-light"></i>
          </button>

          <button :id="`bt_indent_${tabId}`" class="btn btn-sm btn-secondary" title="Indent SQL" @click="indentSQL()">
            <i class="fas fa-indent fa-light"></i>
          </button>

          <button :class="`bt_history_${tabId}`" class="btn btn-sm btn-secondary" title="Command History"
            @click="showCommandList()">
            <i class="fas fa-clock-rotate-left fa-light"></i>
          </button>

          <template v-if="postgresqlDialect">
            <!-- EXPLAIN ANALYZE BUTTONS-->
            <div class="btn-group ml-2 mr-2">
              <button :id="`bt_explain_${tabId}`" class="btn btn-sm btn-secondary" title="Explain" @click="runExplain(0)"
                :disabled="!enableExplainButtons">
                <i class="fas fa-chart-simple fa-light"></i>
              </button>

              <button :id="`bt_analyze_${tabId}`" class="btn btn-sm btn-secondary" title="Explain Analyze"
                @click="runExplain(1)" :disabled="!enableExplainButtons">
                <i class="fas fa-magnifying-glass-chart fa-light"></i>
              </button>
            </div>

            <!-- AUTOCOMMIt-->
            <div class="omnidb__form-check form-check form-check-inline">
              <input :id="`check_autocommit_${tabId}`" class="form-check-input" type="checkbox" v-model="autocommit" />
              <label class="form-check-label custom-checkbox query_info"
                :for="`check_autocommit_${tabId}`">Autocommit</label>
            </div>

            <div class="omnidb__tab-status">
              <i :id="`query_tab_status_${tabId}`" :title="statusText"
                :class="['fas fa-dot-circle tab-status', statusClass]">
                <div v-if="tabStatus === 1 || tabStatus === 2" class="tab-status-indicator">
                  <span :class="circleWavesClass">
                    <span v-for="n in 4" :key="n"></span>
                  </span>
                </div>
              </i>

              <span :id="`query_tab_status_text_${tabId}`" :title="statusText" class="ml-1">
                {{ statusText }}
              </span>
            </div>
          </template>

          <!-- Query ACTIONS BUTTONS-->
          <button :id="`bt_fetch_more_${tabId}`" class="btn btn-sm btn-secondary" title="Run" v-if="showFetchButtons"
            @click="querySQL(queryModes.FETCH_MORE)">
            Fetch More
          </button>

          <button :id="`bt_fetch_all_${tabId}`" class="btn btn-sm btn-secondary" title="Run" v-if="showFetchButtons"
            @click="querySQL(queryModes.FETCH_ALL)">
            Fetch all
          </button>

          <template v-if="activeTransaction">
            <button :id="`bt_commit_${tabId}`" class="btn btn-sm btn-primary" title="Run"
              @click="querySQL(queryModes.COMMIT)">
              Commit
            </button>

            <button :id="`bt_rollback_${tabId}`" class="btn btn-sm btn-secondary" title="Run"
              @click="querySQL(queryModes.ROLLBACK)">
              Rollback
            </button>
          </template>

          <CancelButton v-if="executingState" :tab-id="tabId" :conn-id="connId" @cancelled="cancelSQLTab()" />

          <!-- QUERY INFO DIV-->
          <div :id="`div_query_info_${tabId}`">
            <span v-if="cancelled">
              <b>Cancelled</b>
            </span>
            <span v-else-if="queryStartTime && queryDuration" class="mr-2">
              <b>Start time:</b> {{ queryStartTime }} <b>Duration:</b>
              {{ queryDuration }}
            </span>
            <span v-else-if="queryStartTime">
              <b>Start time:</b> {{ queryStartTime }}
            </span>
          </div>

          <!-- EXPORT BUTTON with SELECT OPTIONS -->
          <button class="btn btn-sm btn-primary ml-auto" title="Export Data" @click="exportData()">
            <i class="fas fa-download fa-light"></i>
          </button>

          <select v-model="exportType" :id="`sel_export_type${tabId}`" class="form-control" style="width: 80px">
            <option v-for="(name, value) in exportTypes" :value="value">
              {{ name }}
            </option>
          </select>
        </div>
      </div>

      <div :id="`query_result_tabs_container_${tabId}`" class="omnidb__query-result-tabs tab-body">
        <button :id="`bt_fullscreen_${tabId}`" style="position: absolute; top: 0.25rem; right: 0.25rem" type="button"
          class="btn btn-sm btn-icon btn-icon-secondary">
          <i class="fas fa-expand"></i>
        </button>

        <!-- DATA, MESSAGE, EXPLAIN tabs-->
        <div :id="`query_result_tabs_${tabId}`" class="h-100">
          <div class="omnidb__tab-menu">
            <div class="nav nav-tabs" role="tablist">
              <a ref="dataTab" class="omnidb__tab-menu__link nav-item nav-link active" :id="`nav_data_tab_${tabId}`"
                data-toggle="tab" :data-target="`#nav_data_${tabId}`" type="button" role="tab"
                :aria-controls="`nav_data_${tabId}`" aria-selected="true">
                <span class="omnidb__tab-menu__link-name"> Data </span>
              </a>
              <template v-if="postgresqlDialect">
                <a ref="messagesTab" class="omnidb__tab-menu__link nav-item nav-link" :id="`nav_messages_tab_${tabId}`"
                  data-toggle="tab" :data-target="`#nav_messages_${tabId}`" type="button" role="tab"
                  :aria-controls="`nav_messages_${tabId}`" aria-selected="true">
                  <span class="omnidb__tab-menu__link-name">
                    Messages
                    <a v-if="noticesCount">{{ noticesCount }}</a>
                  </span>
                </a>
                <a ref="explainTab" class="nav-item nav-link omnidb__tab-menu__link" :id="`nav_explain_tab_${tabId}`"
                  data-toggle="tab" :data-target="`#nav_explain_${tabId}`" type="button" role="tab"
                  :aria-controls="`nav_explain_${tabId}`" aria-selected="false">
                  <span class="omnidb__tab-menu__link-name"> Explain </span>
                </a>
              </template>
            </div>
          </div>

          <div class="tab-content">
            <div class="tab-pane active" :id="`nav_data_${tabId}`" role="tabpanel"
              :aria-labelledby="`nav_data_tab_${tabId}`">
              <div class="omnidb__theme-border--primary p-2">
                <div class="result-div">
                  <template v-if="exportFileName && exportDownloadName">
                    The file is ready.
                    <a class="link_text" :href="exportFileName" :download="exportDownloadName">Save</a>
                  </template>
                  <template v-else-if="errorMessage" class="error_text" style="white-space: pre">
                    {{ errorMessage }}
                  </template>
                  <template v-else-if="queryInfoText">
                    <div class="query_info">
                      {{ queryInfoText }}
                    </div>
                  </template>
                  <template v-else>
                    <hot-table ref="hotTableComponent" :settings="hotSettings"></hot-table>
                    <div ref="hotTableInputHolder" class="handsontableInputHolder" style="z-index: -1"></div>
                  </template>
                </div>
              </div>
            </div>

            <template v-if="postgresqlDialect">
              <div class="tab-pane" :id="`nav_messages_${tabId}`" role="tabpanel"
                :aria-labelledby="`nav_messages_tab_${tabId}`">
                <div class="omnidb__theme-border--primary p-2">
                  <div class="result-div">
                    <p v-for="notice in notices">{{ notice }}</p>
                  </div>
                </div>
              </div>
              <div class="tab-pane" :id="`nav_explain_${tabId}`" role="tabpanel"
                :aria-labelledby="`nav_explain_tab_${tabId}`">
                <div class="omnidb__theme-border--primary pt-2">
                  <div class="result-div">
                    <template v-if="!query && !plan">
                      <p class="lead text-center text-muted mt-5">
                        Nothing to visualize. Please click Explain or Analyze
                        button on the toolbar above.
                      </p>
                    </template>

                    <template v-else>
                      <pev2 class="h-100" :plan-source="plan" :plan-query="query" :key="reRenderCounter" />
                    </template>
                  </div>
                </div>
              </div>
            </template>
          </div>
        </div>
      </div>
    </pane>
  </splitpanes>

  <CommandsHistoryModal :tab-id="tabId" />
</template>

<script>
import { Splitpanes, Pane } from "splitpanes";
import { showToast } from "../notification_control";
import moment from "moment";
import { createRequest } from "../long_polling";
import { v_queryRequestCodes, refreshTreeNode } from "../query";
import { Plan } from "pev2";
import { HotTable } from "@handsontable/vue3";
import { registerAllModules } from "handsontable/registry";
import { queryModes, queryState, tabStatusMap } from "../constants";
import CancelButton from "./CancelSQLButton.vue";
import QueryEditor from "./QueryEditor.vue";
import { emitter } from "../emitter";
import CommandsHistoryModal from "./CommandsHistoryModal.vue";
import { showCommandList } from "../command_history";

// register Handsontable's modules
registerAllModules();

export default {
  name: "QueryTab",
  components: {
    Splitpanes,
    Pane,
    pev2: Plan,
    HotTable,
    CancelButton,
    QueryEditor,
    CommandsHistoryModal,
  },
  props: {
    connId: String,
    tabId: String,
    databaseIndex: Number,
    databaseName: String,
    dialect: String,
    initTabDatabaseId: Number,
  },
  data() {
    return {
      queryState: queryState.Idle,
      tabStatus: tabStatusMap.NOT_CONNECTED,
      autocommit: true,
      queryStartTime: "",
      queryDuration: "",
      data: "",
      context: "",
      tabDatabaseId: this.initTabDatabaseId,
      cancelled: false,
      enableExplainButtons: false,
      query: "",
      plan: "",
      reRenderCounter: 0,
      exportTypes: {
        csv: "CSV",
        "csv-no_headers": "CSV(no headers)",
        xlsx: "XLSX",
        "xlsx-no_headers": "XLSX(no headers)",
      },
      exportType: "csv",
      exportFileName: "",
      exportDownloadName: "",
      errorMessage: "",
      showFetchButtons: false,
      hotSettings: {
        data: [],
        height: "auto",
        width: "100%",
        readOnly: true,
        rowHeaders: true,
        fillHandle: false,
        manualColumnResize: true,
        licenseKey: "non-commercial-and-evaluation",
        contextMenu: {
          items: {
            copy: {
              name() {
                return '<div class="position-absolute"><i class="fas fa-copy cm-all align-middle"></i></div><div class="pl-5">Copy</div>';
              },
            },
            view_data: {
              name() {
                return '<div class="position-absolute"><i class="fas fa-edit cm-all align-middle"></i></div><div class="pl-5">View Content</div>';
              },
              callback(key, selection, clickEvent) {
                //TODO need to change cellDataModal function
                // cellDataModal(this,options[0].start.row,options[0].start.col,this.getDataAtCell(options[0].start.row,options[0].start.col),false);
              },
            },
          },
        },
      },
      queryInfoText: "",
      readOnlyEditor: false,
      notices: [],
    };
  },
  computed: {
    postgresqlDialect() {
      return this.dialect === "postgresql";
    },
    idleState() {
      return this.queryState === queryState.Idle;
    },
    executingState() {
      return this.queryState === queryState.Executing;
    },
    statusText() {
      const statusMap = {
        0: "Not Connected",
        1: "Idle",
        2: "Running",
        3: "Idle in transaction",
        4: "Idle in transaction (aborted)",
      };
      return statusMap[this.tabStatus] || "";
    },
    statusClass() {
      const statusClassMap = {
        0: "tab-status-closed",
        1: "tab-status-idle position-relative",
        2: "tab-status-running position-relative",
        3: "tab-status-idle_in_transaction",
        4: "tab-status-idle_in_transaction_aborted",
      };

      return `${statusClassMap[this.tabStatus] || ""}`;
    },
    circleWavesClass() {
      return {
        "omnis__circle-waves":
          this.tabStatus === tabStatusMap.IDLE ||
          this.tabStatus === tabStatusMap.RUNNING,
        "omnis__circle-waves--idle": this.tabStatus === tabStatusMap.IDLE,
        "omnis__circle-waves--running": this.tabStatus === tabStatusMap.RUNNING,
      };
    },
    activeTransaction() {
      return [
        tabStatusMap.IDLE_IN_TRANSACTION,
        tabStatusMap.IDLE_IN_TRANSACTION_ABORTED,
      ].includes(this.tabStatus);
    },
    queryModes() {
      return queryModes;
    },
    noticesCount() {
      return this.notices.length;
    },
  },
  watch: {
    plan: function () {
      this.reRenderCounter++;
    },
  },
  mounted() {
    emitter.on(`${this.tabId}_check_query_status`, () => {
      this.$refs.editor.focus();
      if (this.queryState === queryState.Ready) {
        this.querySQLReturnRender(this.data, this.context);
      }
    });

    emitter.on(`${this.tabId}_run_query`, () => {
      this.queryRunOrExplain();
    });

    emitter.on(`${this.tabId}_run_explain`, () => {
      this.runExplain(0);
    });

    emitter.on(`${this.tabId}_run_explain_analyze`, () => {
      this.runExplain(1);
    });

    emitter.on(`${this.tabId}_indent_sql`, () => {
      this.indentSQL();
    });

    if (this.dialect === "postgresql") {
      $(`#${this.$refs.explainTab.id}`).on("shown.bs.tab", () => {
        this.enableExplainButtons = true;
        if (!(this.tabStatus === tabStatusMap.RUNNING)) this.runExplain(0);
      });

      $(`#${this.$refs.explainTab.id}`).on("hidden.bs.tab", () => {
        this.enableExplainButtons = false;
      });
    }
  },
  unmounted() {
    emitter.all.delete(`${this.tabId}_check_query_status`);
    emitter.all.delete(`${this.tabId}_run_explain`);
    emitter.all.delete(`${this.tabId}_run_explain_analyze`);
    emitter.all.delete(`${this.tabId}_indent_sql`);
  },
  methods: {
    getQueryEditorValue(raw_query) {
      return this.$refs.editor.getQueryEditorValue(raw_query);
    },
    querySQL(
      mode,
      cmd_type = null,
      all_data = false,
      query = this.getQueryEditorValue(false),
      log_query = true,
      save_query = this.getQueryEditorValue(true),
      clear_data = false
    ) {
      let tab_tag = v_connTabControl.selectedTab.tag.tabControl.selectedTab.tag;
      this.queryDuration = "";
      this.cancelled = false;
      this.exportFileName = "";
      this.exportDownloadName = "";
      this.queryInfoText = "";
      this.showFetchButtons = false;
      this.notices = [];

      if (!this.idleState) {
        showToast("info", "Tab with activity in progress.");
      } else {
        if (!query) {
          showToast("info", "Please provice a string.");
        } else {
          let message_data = {
            sql_cmd: query,
            mode: mode,
            autocommit: this.autocommit,
            v_db_index: this.databaseIndex,
            v_conn_tab_id: this.connId,
            v_tab_id: this.tabId,
            tab_db_id: this.tabDatabaseId,
            sql_save: save_query,
            database_name: this.databaseName,
            cmd_type: cmd_type,
            all_data: all_data, // maybe not needed, it is used only by export command
            log_query: log_query,
            // change the we are getting tab title
            tab_title: tab_tag.tab_title_span.innerHTML,
          };

          this.readOnlyEditor = true;

          this.queryStartTime = moment().format();

          let context = {
            tab_tag: tab_tag,
            database_index: this.databaseIndex,
            start_datetime: this.queryStartTime,
            acked: false,
            vue: true,
            callback: this.querySQLReturn.bind(this),
            clear_data: clear_data, // need to clear handsontable when using export
            cmd_type: cmd_type,
            mode: mode,
          };

          context.tab_tag.context = context;

          createRequest(v_queryRequestCodes.Query, message_data, context);

          this.queryState = queryState.Executing;

          //FIXME: change into event emitting later
          tab_tag.tab_loading_span.style.visibility = "visible";
          tab_tag.tab_check_span.style.display = "none";

          this.tabStatus = tabStatusMap.RUNNING;
        }
      }
    },
    querySQLReturn(data, context) {
      //Update tab_db_id if not null in response
      if (data.v_data.inserted_id) {
        this.tabDatabaseId = data.v_data.inserted_id;
      }

      //If query wasn't canceled already

      if (!this.idleState) {
        if (
          this.tabId === context.tab_tag.tabControl.selectedTab.id &&
          this.connId ===
          context.tab_tag.connTab.tag.connTabControl.selectedTab.id
        ) {
          this.querySQLReturnRender(data, context);
        } else {
          this.queryState = queryState.Ready;
          this.data = data;
          this.context = context;

          //FIXME: change into event emitting later
          context.tab_tag.tab_loading_span.style.visibility = "hidden";
          context.tab_tag.tab_check_span.style.display = "";
        }
      }
    },
    querySQLReturnRender(data, context) {
      this.queryState = queryState.Idle;

      this.context = "";
      this.data = "";

      this.readOnlyEditor = false;

      if (data.v_error) {
        this.errorMessage = data.v_data.message;
      } else {
        if (context.cmd_type === "explain") {
          $(`#${this.$refs.explainTab.id}`).tab("show");

          // Adjusting data.
          let explain_text = data.v_data.data.join("\n");

          if (explain_text.length > 0) {
            this.query = this.getQueryEditorValue(false);
            this.plan = explain_text;
          }
        } else if (!!context.cmd_type && context.cmd_type.includes("export")) {
          this.exportFileName = data.v_data.file_name;
          this.exportDownloadName = data.v_data.download_name;
        } else {
          $(`#${this.$refs.dataTab.id}`).tab("show");

          if (data.v_data.notices.length) {
            this.notices = data.v_data.notices;
          }

          //Show fetch buttons if data has 50 rows
          if (
            data.v_data.data.length >= 50 &&
            context.mode !== this.queryModes.FETCH_ALL
          ) {
            this.showFetchButtons = true;
          } else {
            this.showFetchButtons = false;
          }
          if (context.mode === this.queryModes.DATA_OPERATION) {
            // if no data that means that it is create, upsert, delete operation
            if (
              data.v_data.data.length === 0 &&
              data.v_data.col_names.length === 0
            ) {
              this.queryInfoText = data.v_data.status
                ? data.v_data.status
                : "Done";
            } else {
              this.$refs.hotTableComponent.hotInstance.updateSettings({
                colHeaders: data.v_data.col_names,
                copyPaste: {
                  pasteMode: "",
                  uiContainer: this.$refs.hotTableInputHolder,
                },
              });
              this.$refs.hotTableComponent.hotInstance.updateData(
                data.v_data.data
              );
            }
          } else if (
            context.mode === this.queryModes.FETCH_MORE ||
            context.mode === this.queryModes.FETCH_ALL
          ) {
            let initialData =
              this.$refs.hotTableComponent.hotInstance.getSourceData();

            data.v_data.data.forEach((row) => {
              initialData.push(row);
            });

            this.$refs.hotTableComponent.hotInstance.updateData(initialData);
          } else {
            this.queryInfoText = data.v_data.status;
          }

          let mode = ["CREATE", "DROP", "ALTER"];
          if (!!data.v_data.status && isNaN(data.v_data.status)) {
            let status = data.v_data.status?.split(" ");
            let status_name = status[1];
            if (mode.includes(status[0])) {
              //FIXME: replace this with event emitting on tree instance
              let root_node =
                v_connTabControl.selectedTab.tag.tree.getRootNode();
              if (!!status_name) refreshTreeNode(root_node, status_name);
            }
          }
        }
      }
      this.tabStatus = data.v_data.con_status;
      this.queryDuration = data.v_data.duration;

      //FIXME: change into event emitting later
      context.tab_tag.tab_loading_span.style.visibility = "hidden";
      context.tab_tag.tab_check_span.style.display = "none";
    },
    runExplain(explainMode) {
      let command = this.getQueryEditorValue(false);

      if (command.trim() === "") {
        showToast("info", "Please provide a string.");
      } else {
        let should_prepend =
          command.trim().split(" ")[0].toUpperCase() !== "EXPLAIN";
        if (should_prepend) {
          if (explainMode === 0) {
            command = "explain " + command;
          } else if (explainMode === 1) {
            command = "explain (analyze, buffers) " + command;
          }
        }

        this.querySQL(this.queryModes.DATA_OPERATION, "explain", true, command);
      }
    },
    queryRunOrExplain() {
      if (this.dialect === "postgresql") {
        let query = this.getQueryEditorValue(false);
        let should_explain =
          query.trim().split(" ")[0].toUpperCase() === "EXPLAIN";
        if (should_explain) {
          return this.querySQL(this.queryModes.DATA_OPERATION, "explain", true);
        }
      }

      this.querySQL(this.queryModes.DATA_OPERATION);
    },
    exportData() {
      $(`#${this.$refs.dataTab.id}`).tab("show");
      let cmd_type = `export_${this.exportType}`;
      let query = this.getQueryEditorValue(false);
      this.querySQL(
        this.queryModes.DATA_OPERATION,
        cmd_type,
        true,
        query,
        true,
        query,
        true
      );
    },
    cancelSQLTab() {
      this.readOnlyEditor = false;

      this.queryState = queryState.Idle;
      this.tabStatus = tabStatusMap.NOT_CONNECTED;

      this.cancelled = true;
    },
    indentSQL() {
      this.$refs.editor.indentSQL();
    },
    showCommandList,
  },
};
</script>

<style scoped>
.tab-status-indicator {
  position: absolute;
  width: 15px;
  height: 15px;
  overflow: visible;
  left: 0px;
  top: 0px;
  display: block;
}

.query-body {
  height: calc(100vh - 60px);
}

.tab-actions {
  align-items: center;
  display: flex;
  justify-content: flex-start;
  min-height: 35px;
}

.tab-actions>button {
  margin-right: 5px;
}

.splitpanes .splitpanes__pane {
  transition: none;
}

.tab-body {
  height: calc(100% - 40px);
}

.tab-content,
.omnidb__theme-border--primary {
  height: calc(100% - 20px);
}

.tab-pane,
.result-div {
  height: 100%;
}

.result-div {
  overflow: auto;
}
</style>
