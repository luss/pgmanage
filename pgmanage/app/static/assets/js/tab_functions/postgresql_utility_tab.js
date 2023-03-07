let createUtilityTab = function (node, utility_type, backup_type = "objects") {
  // Removing last tab of the inner tab list
  v_connTabControl.selectedTab.tag.tabControl.removeLastTab();
  let tab_name = `${utility_type} ${
    utility_type === "Backup" ? backup_type : ""
  }`;
  let mode = utility_type.toLowerCase();

  let tab = v_connTabControl.selectedTab.tag.tabControl.createTab({
    p_name: `<span>${tab_name}</span>`,
    p_closeFunction: function (e, tab) {
      let current_tab = tab;
      beforeCloseTab(e, function () {
        removeTab(current_tab);
      });
    },
  });

  // Selecting the newly created tab
  v_connTabControl.selectedTab.tag.tabControl.selectTab(tab);

  tab.elementDiv.innerHTML = `
  <div id='${mode}_tab_${tab.id}' class="pt-3">
    <component :is="currentComp" v-bind="currentProps"></component>
  </div>`;
  let tag = {
    tab_id: tab.id,
    mode: mode,
    div_result: document.getElementById(`${mode}_tab_${tab.id}`),
  };
  tab.tag = tag;

  let add_tab = v_connTabControl.selectedTab.tag.tabControl.createTab({
    p_name: "+",
    p_close: false,
    p_selectable: false,
    p_clickFunction: function (e) {
      showMenuNewTab(e);
    },
  });
  add_tab.tag = {
    mode: "add",
  };

  const { createApp } = Vue;

  const app = createApp({
    data() {
      return {
        currentUtility: utility_type,
        backupType: backup_type,
        treeNode: node,
      };
    },
    computed: {
      currentComp() {
        const currentComponent = this.currentUtility;
        return Vue.defineAsyncComponent(() =>
          loadModule(
            `../static/assets/js/vuejs/components/${currentComponent}Tab.vue`,
            options
          )
        );
      },
      currentProps() {
        if (this.currentUtility === "Backup") {
          return { "backup-type": this.backupType, "tree-node": this.treeNode };
        } else if (this.currentUtility === "Restore") {
          return { "tree-node": this.treeNode };
        }
      },
    },
  });

  app.mount(`#${mode}_tab_${tab.id}`);
};
