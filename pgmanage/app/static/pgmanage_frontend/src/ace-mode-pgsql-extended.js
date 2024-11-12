ace.define(
  "ace/mode/pgsql_extended",
  ["require", "exports", "ace/lib/oop", "ace/mode/text", "ace/range"],
  function (acequire, exports) {
    const oop = acequire("ace/lib/oop");
    const PgsqlMode = acequire("ace/mode/pgsql").Mode;
    const SqlFoldMode = acequire("./folding/sql").FoldMode;

    const ExtendedPgsqlMode = function () {
      PgsqlMode.call(this);
      this.foldingRules = new SqlFoldMode();
    };
    oop.inherits(ExtendedPgsqlMode, PgsqlMode);

    // Export the mode
    exports.Mode = ExtendedPgsqlMode;
  }
);
