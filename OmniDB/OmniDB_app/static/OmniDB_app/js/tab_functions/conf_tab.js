let createConfTab = function () {

    // Removing last tab of the inner tab list
  v_connTabControl.selectedTab.tag.tabControl.removeLastTab();

  let tab = v_connTabControl.selectedTab.tag.tabControl.createTab({
    p_name: '<span>Configuration</span>',
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
  <div id='configuration_tab_${tab.id}' class="pt-3">
    <config></config>
  </div>`

  let tag = {
    tab_id : tab.id,
    mode: 'configuration',
    div_result: document.getElementById(`configuration_tab_${tab.id}`,
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
    components: {
        'config': Vue.defineAsyncComponent(() => loadModule('../static/OmniDB_app/js/vuejs/components/Config.vue', options)),  
    },
    })

  app.mount(`#configuration_tab_${tab.id}`);
}   
