let createBackupTab = function (node, type='objects') {

  // Removing last tab of the inner tab list
  v_connTabControl.selectedTab.tag.tabControl.removeLastTab();

  let tab = v_connTabControl.selectedTab.tag.tabControl.createTab({
    p_name: `<span>Backup ${type}</span>`,
    p_closeFunction: function(e, tab) {
        let current_tab = tab;
        beforeCloseTab(e,
          function() {
            removeTab(current_tab);
          });
      }
  });

  // Selecting the newly created tab
  v_connTabControl.selectedTab.tag.tabControl.selectTab(tab);

  tab.elementDiv.innerHTML =`
  <div id='backup_tab_${tab.id}' class="pt-3">
    <backup-tab :backup-type="backupType" :tree-node="treeNode"></backup-tab>
  </div>`

  let tag = {
    tab_id : tab.id,
    mode: 'backup',
    div_result: document.getElementById(`backup_tab_${tab.id}`,
    )
  }
  tab.tag = tag

  let add_tab = v_connTabControl.selectedTab.tag.tabControl.createTab({
    p_name: '+',
    p_close: false,
    p_selectable: false,
    p_clickFunction: function(e) {
      showMenuNewTab(e);
    }
  });
  add_tab.tag = {
    mode: 'add'
  }

  const {createApp} = Vue;  

  const app = createApp({
    data() {
      return {
        backupType: type,
        treeNode: node
      }
    },
    components: {
        'backup-tab': Vue.defineAsyncComponent(() => loadModule('../static/assets/js/vuejs/components/BackupTab.vue', options)),  
    },
    })

  app.mount(`#backup_tab_${tab.id}`);
  }   
