import { format } from "sql-formatter";

const indentSQLMixin = {
  data() {
    return {
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
  methods: {
    indentSQL() {
      let editor_value = this.editor.getValue();
      let formatted = format(editor_value, this.formatOptions);
      if (formatted.length) {
        this.editor.setValue(formatted);
        this.editor.clearSelection();
        this.editor.gotoLine(0, 0, true);
      }
    },
  },
};

export { indentSQLMixin };
