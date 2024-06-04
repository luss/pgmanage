<template>
  <div
    ref="cellDataModal"
    class="modal show"
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
            class="close"
            data-dismiss="modal"
            aria-label="Close"
            @click="store.hideModal()"
          >
            <span aria-hidden="true"><i class="fa-solid fa-xmark"></i></span>
          </button>
        </div>
        <div class="modal-body">
          <div ref="editor" class="ace-editor"></div>
        </div>
        <div class="modal-footer">
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
import {
  settingsStore,
  cellDataModalStore,
} from "../stores/stores_initializer";

export default {
  name: "CellDataModal",
  data() {
    return {
      editor: null,
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
          $(this.$refs.cellDataModal).modal({
            backdrop: "static",
            keyboard: false,
          });
        });
      }

      if (action.name === "hideModal") {
        this.editor.destroy();
        // erase leftover css classes left after editor destruction
        this.$refs.editor.classList.remove('ace-omnidb', 'ace-omnidb_dark')
        $(this.$refs.cellDataModal).modal("hide");
      }
    });
  },
  methods: {
    setupEdidor() {
      this.editor = ace.edit(this.$refs.editor);
      this.editor.$blockScrolling = Infinity;
      this.editor.setTheme(`ace/theme/${settingsStore.editorTheme}`);
      this.editor.session.setMode("ace/mode/sql");
      this.editor.setFontSize(settingsStore.fontSize);
      this.editor.setShowPrintMargin(false);
      this.editor.setReadOnly(true);

      this.editor.commands.bindKey("Cmd-,", null);
      this.editor.commands.bindKey("Ctrl-,", null);
      this.editor.commands.bindKey("Cmd-Delete", null);
      this.editor.commands.bindKey("Ctrl-Delete", null);
    },
    setEditorContent() {
      let cellContent = this.store.cellContent;
      if (cellContent) cellContent = this.store.cellContent.toString();
      this.editor.setValue(cellContent);
      this.editor.clearSelection();
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
  border: 1px solid rgb(195, 195, 195);
}

.modal-body {
  white-space: pre-line;
}
</style>
