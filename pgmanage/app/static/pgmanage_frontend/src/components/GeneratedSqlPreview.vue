<template>
  <p v-show="showLabel" class="fw-bold mb-2">{{ label }}</p>
  <div ref="editor" v-bind="$attrs"></div>
</template>

<script>
import { EDITOR_MODEMAP } from "../constants";
import { settingsStore, tabsStore } from "../stores/stores_initializer";
export default {
  props: {
    label: {
      type: String,
      default: "Preview",
    },
    showLabel: {
      type: Boolean,
      default: true,
    },
    editorText: {
      type: String,
    },
    databaseTechnology: {
      type: String,
    },
  },
  data() {
    return {};
  },
  mounted() {
    this.setupEditor();
  },
  watch: {
    editorText(newValue, oldValue) {
      this.editor.setValue(newValue);
      this.editor.clearSelection();
    },
  },
  methods: {
    setupEditor() {
      let editor_mode = EDITOR_MODEMAP[this.databaseTechnology] || "sql";
      this.editor = ace.edit(this.$refs.editor);
      this.editor.setTheme("ace/theme/" + settingsStore.editorTheme);
      this.editor.setFontSize(Number(settingsStore.fontSize));
      this.editor.session.setMode(`ace/mode/${editor_mode}`);
      this.editor.setReadOnly(true);
      this.editor.setShowPrintMargin(false);

      this.editor.clearSelection();
      this.editor.$blockScrolling = Infinity;

      //Remove shortcuts from ace in order to avoid conflict with omnidb shortcuts
      this.editor.commands.bindKey("ctrl-space", null);
      this.editor.commands.bindKey("Cmd-,", null);
      this.editor.commands.bindKey("Ctrl-,", null);
      this.editor.commands.bindKey("Cmd-Delete", null);
      this.editor.commands.bindKey("Ctrl-Delete", null);
      this.editor.commands.bindKey("Ctrl-Up", null);
      this.editor.commands.bindKey("Ctrl-Down", null);

      settingsStore.$subscribe((mutation, state) => {
        this.editor.setTheme(`ace/theme/${state.editorTheme}`);
        this.editor.setFontSize(state.fontSize);
      });

      this.addCopyToEditorButton();
    },
    addCopyToEditorButton() {
      const copyToEditorButton = document.createElement("button");
      copyToEditorButton.classList.add(
        "position-absolute",
        "btn",
        "btn-outline-secondary",
        "bg-light",
        "btn-sm",
        "m-2",
        "d-none",
        "d-block",
        "top-0",
        "end-0"
      );
      copyToEditorButton.setAttribute("title", "Copy to Query Editor");
      copyToEditorButton.onclick = () => {
        tabsStore.createQueryTab("Query", null, null, this.editor.getValue());
      };

      const iconEl = document.createElement("i");
      iconEl.classList.add("fa-solid", "fa-clipboard");

      copyToEditorButton.appendChild(iconEl);

      const editorContainer = this.$refs.editor;
      editorContainer.addEventListener("mouseover", () =>
        copyToEditorButton.classList.toggle("d-none")
      );
      editorContainer.addEventListener("mouseout", () =>
        copyToEditorButton.classList.toggle("d-none")
      );

      editorContainer.appendChild(copyToEditorButton);
    },
  },
};
</script>
