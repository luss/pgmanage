<template>
  <PowerTree ref="tree" v-model="nodes" @nodedblclick="doubleClickNode" @toggle="onToggle"
    @nodecontextmenu="onContextMenu" :allow-multiselect="false" @nodeclick="onClickHandler">
    <template v-slot:toggle="{ node }">
      <i v-if="node.isExpanded" class="exp_col fas fa-chevron-down"></i>
      <i v-if="!node.isExpanded" class="exp_col fas fa-chevron-right"></i>
    </template>

    <template v-slot:title="{ node }">
      <span class="item-icon">
        <i :class="['icon_tree', node.data.icon]"></i>
      </span>
      <span v-if="node.data.raw_html" v-html="node.title"> </span>
      <span v-else>
        {{ formatTitle(node) }}
      </span>
    </template>
  </PowerTree>
</template>

<script>
import TreeMixin from "../mixins/power_tree.mjs";
const { PowerTree } = window["VuePowerTree"];

export default {
  name: "TreeSnippets",
  components: {
    PowerTree,
  },
  mixins: [TreeMixin],
  props: {
    snippetTag: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      nodes: [
        {
          title: "Snippets",
          isExpanded: false,
          isDraggable: false,
          data: {
            icon: "fas node-all fa-list-alt node-snippet-list",
            type: "node",
            contextMenu: "cm_node_root",
            id: null,
          },
        },
      ],
    };
  },
  computed: {
    contextMenu() {
      return {
        cm_node_root: [
          this.cmRefreshObject,
          {
            label: "New Folder",
            icon: "fas cm-all fa-folder-plus",
            onClick: () => {
              this.newNodeSnippet(this.selectedNode, "node");
            },
          },
          {
            label: "New Snippet",
            icon: "fas cm-all fa-file-circle-plus",
            onClick: () => {
              this.newNodeSnippet(this.selectedNode, "snippet");
            },
          },
        ],
        cm_node: [
          this.cmRefreshObject,
          {
            label: "New Folder",
            icon: "fas cm-all fa-folder-plus",
            onClick: () => {
              this.newNodeSnippet(this.selectedNode, "node");
            },
          },
          {
            label: "New Snippet",
            icon: "fas cm-all fa-file-circle-plus",
            onClick: () => {
              this.newNodeSnippet(this.selectedNode, "snippet");
            },
          },
          {
            label: "Rename Folder",
            icon: "fas cm-all fa-i-cursor",
            onClick: () => {
              this.renameNodeSnippet(this.selectedNode);
            },
          },
          {
            label: "Delete Folder",
            icon: "fas cm-all fa-times",
            onClick: () => {
              this.deleteNodeSnippet(this.selectedNode);
            },
          },
        ],
        cm_snippet: [
          {
            label: "Edit",
            icon: "fas cm-all fa-edit",
            onClick: () => {
              this.startEditSnippetText(this.selectedNode);
            },
          },
          {
            label: "Rename",
            icon: "fas cm-all fa-i-cursor",
            onClick: () => {
              this.renameNodeSnippet(this.selectedNode);
            },
          },
          {
            label: "Delete",
            icon: "fas cm-all fa-times",
            onClick: () => {
              this.deleteNodeSnippet(this.selectedNode);
            },
          },
        ],
      };
    },
  },
  methods: {
    refreshTree(node) {
      if (node.children.length == 0) this.insertSpinnerNode(node);
      if (node.data.type === "node") {
        this.getChildSnippetNodes(node);
      }
    },
    getChildSnippetNodes(node) {
      this.api
        .post("/get_node_children/", {
          snippet_id: node.data.id,
        })
        .then((resp) => {
          this.removeChildNodes(node);

          resp.data.list_texts.forEach((el) => {
            this.insertNode(
              node,
              el.name,
              {
                icon: "far node-all fa-file-code node-snippet-snippet",
                type: "snippet",
                contextMenu: "cm_snippet",
                id: el.id,
                id_parent: node.data.id,
                name: el.name,
                parent: node,
              },
              true
            );
          });

          resp.data.list_nodes.forEach((el) => {
            this.insertNode(node, el.name, {
              icon: "fas node-all fa-folder node-snippet-folder",
              type: "node",
              contextMenu: "cm_node",
              id: el.id,
              id_parent: node.data.id,
              name: el.name,
              parent: node,
            });
          });
        })
        .catch((error) => {
          this.nodeOpenError(error, node);
        });
    },
    newNodeSnippet(node, mode) {
      let placeholder = "Snippet Name";
      if (mode === "node") placeholder = "Node Name";

      showConfirm(
        `<input id="element_name" class="form-control" placeholder="${placeholder}" style="width: 100%;">`,
        () => {
          this.api
            .post("/new_node_snippet/", {
              snippet_id: node.data.id,
              mode: mode,
              name: document.getElementById("element_name").value,
            })
            .then((resp) => {
              this.refreshTree(node);

              getAllSnippets();
            })
            .catch((error) => {
              this.nodeOpenError(error, node);
            });
        },
        null,
        () => {
          let input = document.getElementById("element_name");
          input.focus();
          input.selectionStart = 0;
          input.selectionEnd = 10000;
        }
      );
    },
    renameNodeSnippet(node) {
      showConfirm(
        '<input id="element_name" class="form-control" value="' +
        node.title +
        '" style="width: 100%;">',
        () => {
          this.api
            .post("/rename_node_snippet/", {
              id: node.data.id,
              mode: node.data.type,
              name: document.getElementById("element_name").value,
            })
            .then((resp) => {
              this.refreshTree(this.getParentNode(node));

              getAllSnippets();
            })
            .catch((error) => {
              this.nodeOpenError(error, node);
            });
        }
      );
    },
    deleteNodeSnippet(node) {
      createMessageModal(
        `Are you sure you want to delete this ${node.data.type}?`,
        () => {
          this.api
            .post("/delete_node_snippet/", {
              id: node.data.id,
              mode: node.data.type,
            })
            .then((resp) => {
              this.refreshTree(this.getParentNode(node));

              getAllSnippets();
            })
            .catch((error) => {
              this.nodeOpenError(error, node);
            });
        }
      );
    },
    startEditSnippetText(node) {
      // Checking if there is a tab for this snippet.
      let snippet_tab_list = this.snippetTag.tabControl.tabList;
      let avaiable_tab = false;

      snippet_tab_list.forEach((snippet_tab) => {
        let snippet_object = snippet_tab.tag.snippetObject;
        if (typeof snippet_object === "object") {
          if (snippet_object.id === node.data.id) {
            avaiable_tab = snippet_tab;
          }
        }
      });

      if (avaiable_tab) {
        this.snippetTag.tabControl.selectTab(avaiable_tab);
      } else {
        v_connTabControl.tag.createSnippetTextTab(node.data);
      }

      this.api
        .post("/get_snippet_text/", {
          snippet_id: node.data.id,
        })
        .then((resp) => {
          console.log(resp);
          v_connTabControl.snippet_tag.tabControl.selectedTab.tag.editor.setValue(
            resp.data.data
          );
          v_connTabControl.snippet_tag.tabControl.selectedTab.tag.editor.clearSelection();
          v_connTabControl.snippet_tag.tabControl.selectedTab.tag.editor.gotoLine(
            0,
            0,
            true
          );
        })
        .catch((error) => {
          this.nodeOpenError(error, node);
        });
    },
  },
};
</script>
