<template>
<PowerTree ref="tree" v-model="nodes" @nodeclick="onNodeClick">

</PowerTree>

</template>

<script>
let nodes = [
{title: 'Item1', isLeaf: true},
    {title: 'Item2', isLeaf: true, data: { visible: false }},
    {title: 'Folder1'},
    {
      title: 'Folder2', isExpanded: true, children: [
        {title: 'Item3', isLeaf: true},
        {title: 'Item4', isLeaf: true},
        {
          title: 'Folder3', children: [
            {title: 'Item5', isLeaf: true}
          ]
        }
      ]
    },
    {title: 'Folder5', isExpanded: false},
    {title: 'Item6', isLeaf: true},
    {title: 'Item7', isLeaf: true, data: { visible: false }},
    {
      title: 'Folder6', children: [
        {
          title: 'Folder7', children: [
            {title: 'Item8', isLeaf: true},
            {title: 'Item9', isLeaf: true}
          ]
        }
      ]
    }
  ];
const {PowerTree} = window['VuePowerTree']
export default {
  name: 'SqliteTree',
  components: {
    PowerTree,
  },
  data() {
    return {
      nodes: nodes,
      contextMenu: {
        cm_server: [
          {
            label: "Refresh",
            icon: "fas cm-all fa-sync-alt",
            onClick: () => {
              if (this.selectedNode.children.length == 1) {
                this.refreshTreeSqlite(node);
              } else {
                this.selectedNode.treeNodeSpec.state.expanded =
                  !this.selectedNode.treeNodeSpec.state.expanded;
              }
            },
          },
        ],
        cm_tables: [
          {
            label: "Refresh",
            icon: "fas cm-all fa-sync-alt",
            onClick: () => {
              if (this.selectedNode.children.length == 1) {
                this.refreshTreeSqlite(node);
              } else {
                this.selectedNode.treeNodeSpec.state.expanded =
                  !this.selectedNode.treeNodeSpec.state.expanded;
              }
            },
          },
          {
            label: "Create Table",
            icon: "fas cm-all fa-edit",
            onClick: () => {
              tabSQLTemplate("Create Table", this.templates.create_table);
            },
          },
        ],
      },
    }
  },
  methods: {
    onNodeClick(node, e) {
      const title = '<i class="icon_tree node-sqlite">Item5</i>'
      this.$refs.tree.insert({node: node, placement: 'inside'}, {title: title, isLeaf: true})
      
    }
  }
}
</script>