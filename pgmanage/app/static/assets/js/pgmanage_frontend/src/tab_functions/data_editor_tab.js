import {
    removeTab,
    showMenuNewTab,
  } from "../workspace";

import { createApp } from "vue";
import DataEditorTab from "../components/DataEditorTab.vue";
import { beforeCloseTab } from "../create_tab_functions";

export let  createDataEditorTab = function(table, schema = '') {
    let tab_name = schema ? `Edit data: ${schema}.${table}` : `Edit data: ${table}`
    let table_name = table.replace(/^"(.*)"$/, '$1')
    v_connTabControl.selectedTab.tag.tabControl.removeLastTab();

    let tab = v_connTabControl.selectedTab.tag.tabControl.createTab({
      p_icon: '<i class="fas fa-table icon-tab-title"></i>',
      p_name: '<span id="tab_title">' + tab_name + '</span><span id="tab_loading" style="visibility:hidden;"><i class="tab-icon node-spin"></i></span><i title="" id="tab_check" style="display: none;" class="fas fa-check-circle tab-icon icon-check"></i>',
      p_closeFunction: function(e,p_tab) {
        let current_tab = p_tab;
        beforeCloseTab(e,
          function() {
            current_tab.app.unmount();
            removeTab(current_tab);
        });
      }
    });

    v_connTabControl.selectedTab.tag.tabControl.selectTab(tab);

    tab.elementDiv.innerHTML = `
    <div id='data_editor_tab_${tab.id}' class="pt-3">
      <data-editor-tab></data-editor-tab>
    </div>`;

    let tag = {
        tab_id: tab.id,
        div_result: document.getElementById(`data_editor_tab_${tab.id}`),
    };
    tab.tag = tag

    const DIALECT_MAP = {
      'oracle': 'oracledb',
      'mariadb': 'mysql'
    }

    let dialect =  v_connTabControl.selectedTab.tag.selectedDBMS
    let mapped_dialect = DIALECT_MAP[dialect] || dialect
    let app = createApp({
      components: {
          "data-editor-tab": DataEditorTab,
      }
      },{
        database_index: v_connTabControl.selectedTab.tag.selectedDatabaseIndex,
        tab_id: v_connTabControl.selectedTab.id,
        table: table_name,
        schema: schema,
        dialect: mapped_dialect,
        query_filter: '' //to be used in the future for passing extra filters when tab is opened
    });

    tab.app = app;
    app.mount(`#data_editor_tab_${tab.id}`);

    let add_tab = v_connTabControl.selectedTab.tag.tabControl.createTab({
        p_name: "+",
        p_close: false,
        p_isDraggable: false,
        p_selectable: false,
        p_clickFunction: function (e) {
          showMenuNewTab(e);
        },
    });

    add_tab.tag = {
        mode: "add",
    };
  };