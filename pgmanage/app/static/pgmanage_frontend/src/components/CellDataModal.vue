<template>
  <div
    id="cell_data_modal"
    ref="cellDataModal"
    class="modal fade"
    aria-hidden="true"
    role="dialog"
    tabindex="-1"
  >
    <div class="modal-dialog" role="document">
      <div class="modal-content">
        <div class="modal-header align-items-center">
          <h2 class="modal-title font-weight-bold">Show Data</h2>
          <button
            type="button"
            class="btn-close"
            data-dismiss="modal"
            aria-label="Close"
            @click="store.hideModal()"
          ></button>
        </div>
        <div class="modal-body">
          <Transition :duration="100">
            <div
              v-if="showLoading"
              class="div_loading d-block"
              style="z-index: 10"
            >
              <div class="div_loading_cover"></div>
              <div class="div_loading_content">
                <div
                  class="spinner-border spinner-size text-primary"
                  role="status"
                >
                  <span class="sr-only">Loading...</span>
                </div>
              </div>
            </div>
          </Transition>
          <div ref="editor" class="ace-editor"></div>
        </div>
        <div
          class="modal-footer"
          :class="{ 'justify-content-between': store.showControls }"
        >
          <div v-if="store.showControls" class="row">
            <div class="col-auto align-content-center">
              <span> View as </span>
            </div>
            <div class="col-auto">
              <select class="form-select" v-model="contentMode">
                <option
                  v-for="(modePath, modeName, index) in contentModes"
                  :value="modePath"
                  :key="index"
                >
                  {{ modeName }}
                </option>
              </select>
            </div>
            <div class="col-auto form-check align-content-center">
              <input
                type="checkbox"
                class="form-check-input"
                v-model="autoFormat"
              />
              <label for="" class="form-check-label">Autoformat</label>
            </div>
            <div class="col-auto">
              <button class="btn btn-sm btn-primary" @click="formatContent">
                Format
              </button>
            </div>
          </div>
          <button
            type="button"
            class="btn btn-secondary"
            data-dismiss="modal"
            @click="store.hideModal()"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { beautify } from "ace-builds/src-noconflict/ext-beautify";
import {
  settingsStore,
  cellDataModalStore,
} from "../stores/stores_initializer";
import { Modal } from "bootstrap";

export default {
  name: "CellDataModal",
  data() {
    return {
      editor: null,
      modalInstance: null,
      contentModes: {
        TEXT: "ace/mode/plain_text",
        JSON: "ace/mode/json",
        HTML: "ace/mode/xml",
        SQL: "ace/mode/sql",
      },
      contentMode: "ace/mode/plain_text",
      autoFormat: true,
      showLoading: true,
    };
  },
  computed: {
    store() {
      return cellDataModalStore;
    },
  },
  mounted() {
    cellDataModalStore.$onAction((action) => {
      if (action.name === "showModal") {
        action.after(() => {
          this.setupEdidor();
          this.setEditorContent();
          this.modalInstance = Modal.getOrCreateInstance(
            this.$refs.cellDataModal,
            {
              backdrop: "static",
              keyboard: false,
            }
          );
          this.modalInstance.show();
        });
      }

      if (action.name === "hideModal") {
        this.editor.destroy();
        this.modalInstance.hide();
        // erase leftover css classes left after editor destruction
        this.$refs.editor.classList.remove("ace-omnidb", "ace-omnidb_dark");
      }
    });
  },
  watch: {
    contentMode(newValue) {
      this.editor.session.setMode(newValue);
      if (this.autoFormat) {
        beautify(this.editor.session);
      }
    },
  },
  methods: {
    setupEdidor() {
      this.editor = ace.edit(this.$refs.editor);
      this.editor.$blockScrolling = Infinity;
      this.editor.setTheme(`ace/theme/${settingsStore.editorTheme}`);
      this.editor.setFontSize(settingsStore.fontSize);
      this.editor.setShowPrintMargin(false);
      this.editor.setReadOnly(true);

      this.editor.commands.bindKey("Cmd-,", null);
      this.editor.commands.bindKey("Ctrl-,", null);
      this.editor.commands.bindKey("Cmd-Delete", null);
      this.editor.commands.bindKey("Ctrl-Delete", null);
    },
    setEditorContent() {
      this.showLoading = true;
      let cellContent = this.store.cellContent || "";
      if (cellContent) cellContent = this.store.cellContent.toString();
      const cellType = this.store.cellType || "default";

      // Determine the mode based on cellType
      this.contentMode = this.getAceMode(cellType);
      this.editor.setValue(cellContent);
      this.editor.clearSelection();
      this.showLoading = false;
    },
    getAceMode(cellType) {
      switch (cellType) {
        case "json":
        case "jsonb":
          return "ace/mode/json";
        case "xml":
        case "xmltype":
          return "ace/mode/xml";
        case "sql":
        case "enum":
        case "set":
        case "cursor":
        case "object":
          return "ace/mode/sql";
        default:
          return "ace/mode/plain_text";
      }
    },
    formatContent() {
      beautify(this.editor.getSession());
    },
  },
};
</script>

<style scoped>
.modal-dialog {
  width: 1200px;
  max-width: 90vw;
}

.ace-editor {
  height: 70vh;
}

.modal-body {
  white-space: pre-line;
}
</style>
