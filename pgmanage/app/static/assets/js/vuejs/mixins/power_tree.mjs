export default {
  computed: {
    cmRefreshObject() {
      return {
        label: "Refresh",
        icon: "fas cm-all fa-sync-alt",
        onClick: this.refreshNode,
      };
    },
  },
  methods: {
    onClickHandler(node, e) {
      // fix this not to use window
      if (window.v_connTabControl.selectedTab.tag.treeTabsVisible)
        this.getPropertiesSqlite(node);
    },
    onToggle(node, e) {
      this.$refs.tree.select(node.path);
      if (node.isExpanded) return;
      this.refreshTreeSqlite(node);
      this.getNodeEl(node.path).scrollIntoView({
        block: "start",
        inline: "nearest",
        behavior: "smooth",
      });
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
    getNodeEl(path) {
      return this.$refs.tree.$el.querySelector(
        `[path="${JSON.stringify(path)}"]`
      );
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
    formatTitle(node) {
      if (node.data.uniqueness !== undefined) {
        return `${node.title} (${node.data.uniqueness})`;
      }
      return node.title;
    },
  },
};
