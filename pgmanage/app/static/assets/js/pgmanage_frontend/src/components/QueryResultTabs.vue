<template>
  <div ref="resultDiv" :id="`query_result_tabs_container_${tabId}`" class="omnidb__query-result-tabs tab-body">
    <button :id="`bt_fullscreen_${tabId}`" style="position: absolute; top: 0.25rem; right: 0.5rem" type="button"
      class="btn btn-sm btn-icon btn-icon-secondary" @click="toggleFullScreen()">
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
        <div class="tab-pane active pt-2" :id="`nav_data_${tabId}`" role="tabpanel" :aria-labelledby="`nav_data_tab_${tabId}`">
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
              <hot-table v-show="showTable" ref="hotTableComponent" :settings="hotSettings"></hot-table>
              <div ref="hotTableInputHolder" class="handsontableInputHolder" style="z-index: -1"></div>
          </div>
        </div>

        <template v-if="postgresqlDialect">
          <div class="tab-pane" :id="`nav_messages_${tabId}`" role="tabpanel"
            :aria-labelledby="`nav_messages_tab_${tabId}`">
            <div class="messages__wrap p-2">
              <div class="result-div">
                <p v-for="notice in notices">{{ notice }}</p>
              </div>
            </div>
          </div>
          <ExplainTabContent :tab-id="tabId" :query="query" :plan="plan" />
        </template>
      </div>
    </div>
  </div>
</template>

<script>
import ExplainTabContent from "./ExplainTabContent.vue";
import { queryModes, tabStatusMap } from "../constants";
import { HotTable } from "@handsontable/vue3";
import { cellDataModal } from "../header_actions";
import { emitter } from "../emitter";

export default {
  components: {
    ExplainTabContent,
    HotTable,
  },
  props: {
    tabId: String,
    connId: String,
    editorContent: String,
    dialect: String,
    tabStatus: Number,
  },
  emits: ["enableExplainButtons", "runExplain", "showFetchButtons"],
  data() {
    return {
      errorMessage: "",
      exportFileName: "",
      exportDownloadName: "",
      notices: [],
      queryInfoText: "",
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
                //TODO overwrite cellDataModal function
                cellDataModal(
                  this,
                  selection[0].start.row,
                  selection[0].start.col,
                  this.getDataAtCell(
                    selection[0].start.row,
                    selection[0].start.col
                  ),
                  false
                );
              },
            },
          },
        },
      },
      query: "",
      plan: "",
    };
  },
  computed: {
    queryModes() {
      return queryModes;
    },
    postgresqlDialect() {
      return this.dialect === "postgresql";
    },
    noticesCount() {
      return this.notices.length;
    },
    showTable() {
      return !((!!this.exportFileName && !!this.exportDownloadName) || !!this.errorMessage || !!this.queryInfoText)
    }
  },
  mounted() {
    if (this.dialect === "postgresql") {
      $(`#${this.$refs.explainTab.id}`).on("shown.bs.tab", () => {
        this.$emit("enableExplainButtons");
        if (!(this.tabStatus === tabStatusMap.RUNNING))
          this.$emit("runExplain");
      });

      $(`#${this.$refs.explainTab.id}`).on("hidden.bs.tab", () => {
        this.$emit("enableExplainButtons");
      });
    }
  },
  methods: {
    renderResult(data, context) {
      this.clearData();
      if (data.v_error) {
        this.errorMessage = data.v_data.message;
      } else {
        if (context.cmd_type === "explain") {
          this.showExplainTab(data.v_data.data);
        } else if (!!context.cmd_type && context.cmd_type.includes("export")) {
          this.showExport(data.v_data);
        } else {
          this.showDataTab(data.v_data, context);

          let mode = ["CREATE", "DROP", "ALTER"];
          if (!!data.v_data.status && isNaN(data.v_data.status)) {
            let status = data.v_data.status?.split(" ");
            if (mode.includes(status[0])) {
              let node_type = status[1]
                ? `${status[1].toLowerCase()}_list`
                : null;

              if (!!node_type)
                emitter.emit(`refreshTreeRecursive_${this.connId}`, node_type);
            }
          }
        }
      }
    },
    showExplainTab(data) {
      $(`#${this.$refs.explainTab.id}`).tab("show");

      // Adjusting data.
      let explain_text = data.join("\n");

      if (explain_text.length > 0) {
        this.query = this.editorContent;
        this.plan = explain_text;
      }
    },
    showExport(data) {
      $(`#${this.$refs.dataTab.id}`).tab("show");

      this.exportFileName = data.file_name;
      this.exportDownloadName = data.download_name;
    },
    showDataTab(data, context) {
      $(`#${this.$refs.dataTab.id}`).tab("show");

      if (data.notices.length) {
        this.notices = data.notices;
      }

      //Show fetch buttons if data has 50 rows
      if (
        data.data.length >= 50 &&
        context.mode !== this.queryModes.FETCH_ALL
      ) {
        this.$emit("showFetchButtons", true);
      } else {
        this.$emit("showFetchButtons", false);
      }

      if (context.mode === this.queryModes.DATA_OPERATION) {
        this.showDataOperationResult(data);
      } else if (
        context.mode === this.queryModes.FETCH_MORE ||
        context.mode === this.queryModes.FETCH_ALL
      ) {
        this.fetchData(data);
      } else {
        this.queryInfoText = data.status;
      }
    },
    showDataOperationResult(data) {
      if (data.data.length === 0) {
        if (data.col_names.length === 0) {
          this.queryInfoText = data.status ? data.status : "Done";
        } else {
          this.queryInfoText = "No results";
        }
      } else {
        this.updateHotTable(data);
      }
    },
    updateHotTable(data) {
      this.$refs.hotTableComponent.hotInstance.updateSettings({
        colHeaders: data.col_names,
        copyPaste: {
          pasteMode: "",
          uiContainer: this.$refs.hotTableInputHolder,
        },
      });
      this.$refs.hotTableComponent.hotInstance.updateData(data.data);

      this.$nextTick(() =>{
        this.$refs.hotTableComponent.hotInstance.render()
      })
    },
    fetchData(data) {
      let initialData =
        this.$refs.hotTableComponent.hotInstance.getSourceData();

      data.data.forEach((row) => {
        initialData.push(row);
      });

      this.$refs.hotTableComponent.hotInstance.updateData(initialData);
    },
    clearData() {
      this.notices = [];
      this.queryInfoText = "";
      this.exportDownloadName = "";
      this.exportFileName = "";
      this.errorMessage = "";
    },
    toggleFullScreen() {
      this.$refs.resultDiv.classList.toggle("omnidb__panel-view--full");
    },
  },
};
</script>

<style scoped>
.tab-body {
  height: calc(100% - 25px);
}

.tab-content,
.messages__wrap {
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
