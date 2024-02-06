<template>
  <div ref="editor" @contextmenu.stop.prevent="contextMenu" >
  </div>
</template>

<script>
import ContextMenu from "@imengyu/vue3-context-menu";
import { snippetsStore, settingsStore } from "../stores/stores_initializer";
import { buildSnippetContextMenuObjects } from "../tree_context_functions/tree_snippets";
import {
  autocomplete_start,
  autocomplete_keydown,
  autocomplete_update_editor_cursor,
  close_autocomplete,
  v_keywords
} from "../autocomplete";
import { emitter } from "../emitter";
import { format } from "sql-formatter";
import { setupAceDragDrop } from "../file_drop";
import { maxLinesForIndentSQL } from "../constants";
import { showToast } from "../notification_control";
import axios from 'axios'
import distance from 'jaro-winkler'

export default {
  props: {
    readOnly: {
      type: Boolean,
      default: false,
    },
    autocomplete: {
      type: Boolean,
      default: true,
    },
    tabId: String,
    tabMode: String,
    dialect: String,
  },
  emits: ["editorChange"],
  data() {
    return {
      editor: "",
      formatOptions: {
        tabWidth: 2,
        keywordCase: "upper",
        //sql-formatter uses 'plsql' for oracle sql flavor
        // otherwise - our db technology names match perfectly
        language: this.dialect === "oracle" ? "plsql" : this.dialect,
        linesBetweenQueries: 1,
      },
    };
  },
  computed: {
    autocompleteMode() {
      return this.tabMode === "query" ? 0 : 1;
    },
  },
  watch: {
    readOnly(newValue, oldValue) {
      this.editor.setReadOnly(newValue);
    },
  },
  mounted() {
    this.setupEditor();
    this.setupEvents();
    this.editor.on("change", () => {
      this.$emit("editorChange", this.editor.getValue().trim());
    });

    this.editor.on("blur", () => {
      setTimeout(() => {
        close_autocomplete();
      }, 200);
    });

    settingsStore.$subscribe((mutation, state) => {
      this.editor.setTheme(`ace/theme/${state.editorTheme}`);
      this.editor.setFontSize(state.fontSize);
    });
  },
  unmounted() {
    this.clearEvents();
  },
  methods: {
    setupEditor() {
      this.editor = ace.edit(this.$refs.editor);
      this.editor.$blockScrolling = Infinity;
      this.editor.setTheme(`ace/theme/${settingsStore.editorTheme}`);
      this.editor.session.setMode("ace/mode/sql");
      this.editor.setFontSize(settingsStore.fontSize);
      this.editor.setShowPrintMargin(false);

      // Remove shortcuts from ace in order to avoid conflict with pgmanage shortcuts
      this.editor.commands.bindKey("ctrl-space", null);
      this.editor.commands.bindKey("alt-e", null);
      this.editor.commands.bindKey("Cmd-,", null);
      this.editor.commands.bindKey("Cmd-Delete", null);
      this.editor.commands.bindKey("Ctrl-Delete", null);
      this.editor.commands.bindKey("Ctrl-Up", null);
      this.editor.commands.bindKey("Ctrl-Down", null);
      this.editor.commands.bindKey("Ctrl-F", null);
      this.editor.commands.bindKey("Ctrl-,", null);
      this.editor.commands.bindKey("Up", null);
      this.editor.commands.bindKey("Down", null);

      this.editor.setOption({enableBasicAutocompletion: true})
      this.editor.setOption({enableLiveAutocompletion: true})

      let get_editor_last_word = function(editor) {
        let cursor = editor.selection.getCursor();
        let prefix_pos = editor.session.doc.positionToIndex(cursor)-1;
        let editor_text = editor.getValue();
        let left_text = editor_text
        let pos_iterator = prefix_pos;
        let word_length = 0;

        const SEPARATORS = [' ', '\n', '\'', '(', ')', ',']

        // skip any leading separators first
        while ([' ', '\n'].includes(editor_text[pos_iterator]) && pos_iterator >=0 ) {
          pos_iterator--
        }

        // adjust word start/end pointer until we meet another separator
        while (!SEPARATORS.includes(editor_text[pos_iterator]) && pos_iterator >=0 ) {
          pos_iterator--
          word_length++
        }

        if (pos_iterator >= 0) {
          pos_iterator++;
          return editor_text.substring(pos_iterator,pos_iterator + word_length);
        }
        else {
          return editor_text.substring(pos_iterator,pos_iterator + word_length + 1);
        }
      }

      this.editor.setOptions({
        enableBasicAutocompletion: [
          {
            getCompletions: function (editor, session, pos, prefix, callback) {
              // console.log(prefix)

              // debugger
              // p_value should be the whole word to the left of cursor

              // console.log(last_word)
              // todo: resolve context to complete from: like select * from [resolve table here]
              let ret = [];
              // debugger
              let prefix_is_upcase = /^[A-Z]+$/.test(prefix)
              v_keywords.forEach(function(keyword) {
                let dist = distance(prefix, keyword, { caseSensitive: false })
                if(dist > 0.85) {
                  ret.push({
                      caption: keyword,
                      value: prefix_is_upcase ? keyword : keyword.toLowerCase(),
                      meta: 'keyword',
                      score: dist * 100
                  });
                }
              });
              console.log(ret)
              let last_word = get_editor_last_word(editor)
              axios.post("/get_autocomplete_results/", {
                p_database_index: window.v_connTabControl.selectedTab.tag.selectedDatabaseIndex,
                p_tab_id: window.v_connTabControl.selectedTab.id,
                p_sql: editor.getValue(),
                p_value: last_word,
                p_pos: pos.column
              })
              .then((resp) => {

                let data = resp.data.v_data.data;
                console.log(last_word)
                data.forEach((el) => {
                  let candidates = el.elements.map((item) => {
                    return {
                      caption: item.select_value,
                      value: item.value,
                      meta: el.type,
                      score: 0
                    }
                  })
                  ret = ret.concat(candidates)
                })
                callback(null,ret)
              })
              .catch((error) => {
                showToast("error", error.response.data.data)
              })
            }
          }
        ],
        // to make popup appear automatically, without explicit _ctrl+space_
        enableLiveAutocompletion: false
      });


      this.editor.focus();
      this.editor.resize();

      setupAceDragDrop(this.editor);
    },
    getQueryEditorValue(raw_query) {
      if (raw_query) return this.editor.getValue().trim();
      let selectedText = this.editor.getSelectedText();
      let lineAtCursor = this.editor.session.getLine(
        this.editor.getCursorPosition().row
      );
      return !!selectedText ? selectedText : lineAtCursor;
    },
    contextMenu(event) {
      let option_list = [
        {
          label: "Run selection/line at cursor",
          icon: "fas cm-all fa-play fa-light",
          onClick: () => {
            this.$emit("run-selection");
          },
        },
        {
          label: "Copy",
          icon: "fas cm-all fa-terminal",
          disabled: !this.editor.getSelectedText(),
          onClick: () => {
            document.execCommand("copy");
          },
        },
        {
          label: "Save as snippet",
          icon: "fas cm-all fa-save",
          children: buildSnippetContextMenuObjects(
            "save",
            snippetsStore,
            this.editor.getValue()
          ),
        },
      ];

      if (snippetsStore.files.length != 0 || snippetsStore.folders.length != 0)
        option_list.push({
          label: "Use snippet",
          icon: "fas cm-all fa-file-code",
          children: buildSnippetContextMenuObjects(
            "load",
            snippetsStore,
            this.editor.getValue()
          ),
        });
      ContextMenu.showContextMenu({
        theme: "pgmanage",
        x: event.x,
        y: event.y,
        zIndex: 1000,
        minWidth: 230,
        items: option_list,
      });
    },
    autocompleteKeyDown(event) {
      // don't call autocomplete while typing in the searchbar
      if(event.target.classList.contains('ace_search_field'))
        return
      if (this.autocomplete) {
        autocomplete_keydown(this.editor, event);
      } else {
        autocomplete_update_editor_cursor(this.editor, event);
      }
    },
    autocompleteStart(event, force = null) {
      if (this.autocomplete) {
        autocomplete_start(this.editor, this.autocompleteMode, event, force);
      }
    },
    indentSQL() {
      let editor_value = this.editor.getValue();

      if (this.editor.session.getLength() > maxLinesForIndentSQL) {
        showToast(
          "error",
          `Max lines(${maxLinesForIndentSQL}) for indentSQL exceeded.`
        );
        return;
      }

      let formatted = format(editor_value, this.formatOptions);
      if (formatted.length) {
        this.editor.setValue(formatted);
        this.editor.clearSelection();
        this.editor.gotoLine(0, 0, true);
      }
    },
    focus() {
      this.editor.focus();
    },
    setupEvents() {
      emitter.on(`${this.tabId}_show_autocomplete_results`, (event) => {
        this.autocompleteStart(event, true);
      });

      emitter.on(`${this.tabId}_copy_to_editor`, (command) => {
        this.editor.setValue(command);
        this.editor.clearSelection();
        this.editor.gotoLine(0, 0, true);
      });

      emitter.on(`${this.tabId}_insert_to_editor`, (command) => {
        this.editor.insert(command);
        this.editor.clearSelection();
      });

      emitter.on(`${this.tabId}_indent_sql`, () => {
        this.indentSQL();
      });

      emitter.on(`${this.tabId}_find_replace`, () => {
        this.editor.execCommand("find")
      });
    },
    clearEvents() {
      emitter.all.delete(`${this.tabId}_show_autocomplete_results`);
      emitter.all.delete(`${this.tabId}_copy_to_editor`);
      emitter.all.delete(`${this.tabId}_indent_sql`);
    },
  },
};
</script>
