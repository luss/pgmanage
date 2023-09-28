<template>
  <splitpanes class="default-theme query-body" horizontal>
    <pane size="30">
      <div ref="editor" :id="`txt_query_${tabId}`" class="h-100"></div>
    </pane>

    <pane size="70">
      <!-- ACTION BUTTONS-->
      <div class="row mb-1">
        <div class="tab-actions col-12">
          <button :id="`bt_start_${tabId}`" class="btn btn-sm btn-primary" title="Run" @click="console.log('CLICK')">
            <i class="fas fa-play fa-light"></i>
          </button>

          <button :id="`bt_indent_${tabId}`" class="btn btn-sm btn-secondary" title="Indent SQL" @click="indentSQL()">
            <i class="fas fa-indent fa-light"></i>
          </button>

          <button :class="`bt_history_${tabId}`" class="btn btn-sm btn-secondary" title="Command History">
            <i class="fas fa-clock-rotate-left fa-light"></i>
          </button>

          <!-- EXPLAIN ANALYZE BUTTONS-->
          <div class="btn-group ml-2 mr-2">
            <button :id="`bt_explain_${tabId}`" class="btn btn-sm btn-secondary" title="Explain" disabled>
              <i class="fas fa-chart-simple fa-light"></i>
            </button>

            <button :id="`bt_analyze_${tabId}`" class="btn btn-sm btn-secondary" title="Explain Analyze" disabled>
              <i class="fas fa-magnifying-glass-chart fa-light"></i>
            </button>
          </div>

          <!-- AUTOCOMMIt-->
          <div class="omnidb__form-check form-check form-check-inline">
            <input :id="`check_autocommit_${tabId}`" class="form-check-input" type="checkbox" checked />
            <label class="form-check-label custom-checkbox query_info"
              :for="`check_autocommit_${tabId}`">Autocommit</label>
          </div>

          <div class="omnidb__tab-status">
            <i :id="`query_tab_status_${tabId}`" title="Not Connected"
              class="fas fa-dot-circle tab-status tab-status-closed omnidb__tab-status__icon"></i>
            <span :id="`query_tab_status_text_${tabId}`" title="Not connected" class="tab-status-text ml-1">Not
              connected</span>
          </div>

          <!-- Query ACTIONS BUTTONS-->
          <button :id="`bt_fetch_more_${tabId}`" class="btn btn-sm btn-secondary" title="Run" style="display: none">
            Fetch More
          </button>

          <button :id="`bt_fetch_all_${tabId}`" class="btn btn-sm btn-secondary" title="Run"
            style="margin-left: 5px; display: none">
            Fetch all
          </button>

          <button :id="`bt_commit_${tabId}`" class="btn btn-sm btn-primary" title="Run"
            style="margin-left: 5px; display: none">
            Commit
          </button>

          <button :id="`bt_rollback_${tabId}`" class="btn btn-sm btn-secondary" title="Run"
            style="margin-left: 5px; display: none">
            Rollback
          </button>

          <button :id="`bt_cancel_${tabId}`" class="btn btn-sm btn-danger" title="Cancel" style="display: none">
            Cancel
          </button>

          <!-- QUERY INFO DIV-->
          <div :id="`div_query_info_${tabId}`"></div>

          <!-- EXPORT BUTTON with SELECT OPTIONS -->
          <button class="btn btn-sm btn-primary ml-auto" title="Export Data" @click="console.log('EXPORT DATA')">
            <i class="fas fa-download fa-light"></i>
          </button>

          <select :id="`sel_export_type${tabId}`" class="form-control" style="width: 80px">
            <option value="csv" selected>CSV</option>
            <option value="csv-no_headers">CSV(no headers)</option>
            <option value="xlsx">XLSX</option>
            <option value="xlsx-no_headers">XLSX(no headers)</option>
          </select>
        </div>
      </div>

      <div :id="`query_result_tabs_container_${tabId}`" class="omnidb__query-result-tabs h-100">
        <button :id="`bt_fullscreen_${tabId}`" style="position: absolute; top: 0.25rem; right: 0.25rem" type="button"
          class="btn btn-sm btn-icon btn-icon-secondary">
          <i class="fas fa-expand"></i>
        </button>

        <!-- DATA, MESSAGE, EXPLAIN tabs-->
        <div :id="`query_result_tabs_${tabId}`" class="h-100">
          <div class="omnidb__tab-menu">
            <nav>
              <div class="nav nav-tabs" role="tablist">
                <a ref="dataTab" class="omnidb__tab-menu__link nav-item nav-link active" :id="`nav_data_tab_${tabId}`"
                  data-toggle="tab" :data-target="`#nav_data_${tabId}`" type="button" role="tab"
                  :aria-controls="`nav_data_${tabId}`" aria-selected="true">
                  <span class="omnidb__tab-menu__link-name"> Data </span>
                </a>
                <a ref="messageTab" class="nav-item nav-link omnidb__tab-menu__link" :id="`nav_message_tab_${tabId}`"
                  data-toggle="tab" :data-target="`#nav_message_${tabId}`" type="button" role="tab"
                  :aria-controls="`nav_message_${tabId}`" aria-selected="false">
                  <span class="omnidb__tab-menu__link-name"> Message </span>
                </a>
                <a @click="console.log('EXPLAIN CLICKED')" ref="explainTab"
                  class="nav-item nav-link omnidb__tab-menu__link" :id="`nav_explain_tab_${tabId}`" data-toggle="tab"
                  :data-target="`#nav_explain_${tabId}`" type="button" role="tab" :aria-controls="`nav_explain_${tabId}`"
                  aria-selected="false">
                  <span class="omnidb__tab-menu__link-name"> Explain </span>
                </a>
              </div>
            </nav>
          </div>

          <div class="tab-content h-100">
            <div class="tab-pane active h-100" :id="`nav_data_${tabId}`" role="tabpanel"
              :aria-labelledby="`nav_data_tab_${tabId}`">
              <div class="omnidb__query-result-tabs__content omnidb__theme-border--primary p-2 h-100">
                <div class="omnidb__query-result-tabs__content"></div>
              </div>
            </div>
            <div class="tab-pane h-100" :id="`nav_message_${tabId}`" role="tabpanel"
              :aria-labelledby="`nav_message_tab_${tabId}`">
              <div class="omnidb__query-result-tabs__content omnidb__theme-border--primary p-2 h-100">
                <div class="omnidb__query-result-tabs__content"></div>
              </div>
            </div>
            <div class="tab-pane h-100" :id="`nav_explain_${tabId}`" role="tabpanel"
              :aria-labelledby="`nav_explain_tab_${tabId}`">
              <div class="omnidb__query-result-tabs__content omnidb__theme-border--primary p-2 h-100">
                <div class="omnidb__query-result-tabs__content"></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </pane>
  </splitpanes>
</template>

<script>
import { Splitpanes, Pane } from "splitpanes";
import { settingsStore } from "../stores/settings";
import ace from "ace-builds";
import { indentSQLMixin } from "../mixins/indent_sql";

export default {
  name: "QueryTab",
  mixins: [indentSQLMixin],
  components: {
    Splitpanes,
    Pane,
  },
  props: {
    connId: String,
    tabId: String,
    databaseIndex: Number,
    dialect: String,
  },
  data() {
    return {};
  },
  mounted() {
    this.setupEditor();
    // console.log(this.$refs.explainTab.id)
    // $(`#${this.$refs.explainTab.id}`).tab('show')
  },
  methods: {
    setupEditor() {
      this.editor = ace.edit(this.$refs.editor);
      this.editor.$blockScrolling = Infinity;
      this.editor.setTheme(`ace/theme/${settingsStore.editorTheme}`);
      this.editor.session.setMode("ace/mode/sql");
      this.editor.setFontSize(settingsStore.fontSize);

      // Remove shortcuts from ace in order to avoid conflict with pgmanage shortcuts
      this.editor.commands.bindKey("ctrl-space", null);
      this.editor.commands.bindKey("alt-e", null);
      this.editor.commands.bindKey("Cmd-,", null);
      this.editor.commands.bindKey("Ctrl-,", null);
      this.editor.commands.bindKey("Cmd-Delete", null);
      this.editor.commands.bindKey("Ctrl-Delete", null);
      this.editor.commands.bindKey("Ctrl-Up", null);
      this.editor.commands.bindKey("Ctrl-Down", null);
      this.editor.commands.bindKey("Up", null);
      this.editor.commands.bindKey("Down", null);
      this.editor.commands.bindKey("Tab", null);

      this.editor.focus();
      this.editor.resize();
    },
  },
};
</script>

<style scoped>
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
</style>
