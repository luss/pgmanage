<template>
  <div
    class="omnidb__tab-menu--container omnidb__tab-menu--container--primary omnidb__tab-menu--container--menu-shown"
  >
    <div
      class="omnidb__tab-menu border-bottom omnidb__tab-menu--primary omnidb__theme-bg--menu-primary"
    >
      <nav>
        <div class="nav nav-tabs">
          <a
            :id="tab.id"
            data-toggle="tab"
            :class="[
              'omnidb__tab-menu__link',
              'nav-item',
              'nav-link',
              { disabled: tab.disabled, active: tab.id == selectedTab.id },
            ]"
            role="tab"
            aria-selected="false"
            :aria-controls="`${tab.id}_content`"
            :href="`#${tab.id}_content`"
            :draggable="tab.isDraggable"
            @dragend="tab.dragEndFunction($event, tab)"
            @click.prevent.stop="clickHandler($event, tab)"
            @dblclick="tab.dblClickFunction && tab.dblClickFunction(tab)"
            @contextmenu="contextMenuHandler($event, tab)"
            v-for="tab in tabs"
          >
            <span class="omnidb__tab-menu__link-content">
              <span
                v-if="tab.icon"
                class="omnidb__menu__btn omnidb__tab-menu__link-icon"
                v-html="tab.icon"
              >
              </span>
              <span class="omnidb__tab-menu__link-name">
                <span>{{ tab.name }}</span>
              </span>
            </span>

            <i
              v-if="tab.closable"
              class="fas fa-times tab-icon omnidb__tab-menu__link-close"
              @click.stop.prevent="tab.closeFunction($event, tab)"
            ></i>
          </a>
        </div>
      </nav>
    </div>

    <div class="tab-content omnidb__tab-content omnidb__tab-content--primary">
      <component
        v-for="tab in tabs"
        :key="tab.id"
        :is="tab.component"
        :id="`${tab.id}_content`"
        v-show="tab.id === selectedTab.id || tab.name === 'Snippets'"
        v-bind="getCurrentProps(tab)"
        role="tabpanel"
      ></component>
    </div>
  </div>
</template>

<script>
import { defineAsyncComponent, h } from "vue";
import { tabsStore, connectionsStore } from "../stores/stores_initializer";
import { emitter } from "../emitter";
import { showMenuNewTabOuter } from "../workspace.js";
import { createRequest } from "../long_polling";
import { showToast } from "../notification_control";
import moment from "moment";
import ContextMenu from "@imengyu/vue3-context-menu";
import { queryRequestCodes } from "../constants";
import WelcomeScreen from "./WelcomeScreen.vue";
import SnippetPanel from "./SnippetPanel.vue";
import TabsUtils from "../mixins/tabs_utils_mixin.js";

export default {
  name: "SideBarTabs",
  mixins: [TabsUtils],
  components: {
    WelcomeScreen,
    SnippetPanel,
    ConnectionTab: defineAsyncComponent(() => import("./ConnectionTab.vue")),
    TerminalTab: defineAsyncComponent(() => import("./TerminalTab.vue")),
  },
  computed: {
    tabs() {
      return tabsStore.tabs;
    },
    selectedTab() {
      return tabsStore.selectedPrimaryTab;
    },
  },
  mounted() {
    this.createConnectionsTab();
    this.createWelcomeTab();
    this.createSnippetPanel();
    this.setupEvents();
  },
  methods: {
    getCurrentProps(tab) {
      const componentsProps = {
        ConnectionTab: {
          "conn-tab-id": tab.id,
        },
        SnippetPanel: {
          "tab-id": tab.id,
        },
        TerminalTab: {
          tabId: tab.id,
          databaseIndex: tab?.metaData?.selectedDatabaseIndex,
        },
      };
      return componentsProps[tab.component];
    },
    setupEvents() {
      emitter.on(
        `${tabsStore.id}_create_conn_tab`,
        ({
          index,
          createInitialTabs = true,
          name = false,
          tooltipName = false,
        }) => {
          this.createConnectionPanel(
            index,
            createInitialTabs,
            name,
            tooltipName
          );
        }
      );

      emitter.on(
        `${tabsStore.id}_create_terminal_tab`,
        ({ index, alias, details }) => {
          this.createTerminalTab(index, alias, details);
        }
      );
    },
    createConnectionsTab() {
      tabsStore.addTab({
        name: "Connections",
        icon: '<i class="fas fa-bolt"></i>',
        tooltip: "Connections",
        closable: false,
        selectable: false,
        clickFunction: function (e) {
          showMenuNewTabOuter(e);
        },
      });
    },
    createWelcomeTab() {
      const tab = tabsStore.addTab({
        name: "Welcome",
        component: "WelcomeScreen",
        icon: '<i class="fas fa-hand-spock"></i>',
        tooltip: "Welcome to PgManage",
        closable: false,
        selectFunction: function () {
          document.title = "Welcome to PgManage";
        },
      });

      tabsStore.selectTab(tab);
    },
    createSnippetPanel() {
      tabsStore.addTab({
        name: "Snippets",
        component: "SnippetPanel",
        icon: '<i class="fas fa-file-code"></i>',
        tooltip: "Snippets Panel",
        closable: false,
        selectable: false,
        clickFunction: function () {
          emitter.emit("toggle_snippet_panel");
        },
      });
    },
    createConnectionPanel(
      index,
      createInitialTabs = true,
      name = false,
      tooltipName = false
    ) {
      if (connectionsStore.connections.length == 0) {
        showToast("error", "Create connections first.");
      } else {
        let v_conn = connectionsStore.connections[0];
        for (let i = 0; i < connectionsStore.connections.length; i++) {
          if (connectionsStore.connections[i].id === index) {
            // patch the connection last used date when connecting
            // to refresh last-used labels on the welcome screen
            connectionsStore.connections[i].last_access_date = moment.now();
            v_conn = connectionsStore.connections[i];
          }
        }

        let connName = "";
        if (name) {
          connName = name;
        }
        if (connName === "" && v_conn.alias && v_conn.alias !== "") {
          connName = v_conn.alias;
        }

        if (!tooltipName) {
          tooltipName = "";

          if (v_conn.conn_string && v_conn.conn_string !== "") {
            if (v_conn.alias) {
              tooltipName += `<h5 class="my-1">${v_conn.alias}</h5>`;
            }
            tooltipName += `<div class="mb-1">${v_conn.conn_string}</div>`;
          } else {
            if (v_conn.alias) {
              tooltipName += `<h5 class="my-1">${v_conn.alias}</h5>`;
            }
            if (v_conn.details1) {
              tooltipName += `<div class="mb-1">${v_conn.details1}</div>`;
            }
            if (v_conn.details2) {
              tooltipName += `<div class="mb-1">${v_conn.details2}</div>`;
            }
          }
        }

        const imgPath =
          import.meta.env.MODE === "development"
            ? `${import.meta.env.BASE_URL}src/assets/images/`
            : `${import.meta.env.BASE_URL}assets/`;

        let imgName;
        if (
          import.meta.env.MODE === "development" ||
          v_conn.technology === "sqlite"
        ) {
          imgName = v_conn.technology;
        } else {
          imgName = `${v_conn.technology}2`;
        }

        let icon = `<img src="${v_url_folder}${imgPath}${imgName}.svg"/>`;

        const connTab = tabsStore.addTab({
          name: connName,
          component: "ConnectionTab",
          icon: icon,
          tooltip: tooltipName,
          mode: "connection",
          selectFunction: () => {
            document.title = "PgManage";
            this.checkTabStatus();
          },
          closeFunction: (e, primaryTab) => {
            $('[data-toggle="tab"]').tooltip("hide");
            this.beforeCloseTab(e, function () {
              var v_tabs_to_remove = [];

              let tabs = tabsStore.getSecondaryTabs(primaryTab.id);

              tabs.forEach((tab) => {
                if (
                  tab.metaData.mode == "query" ||
                  tab.metaData.mode == "edit" ||
                  tab.metaData.mode == "debug" ||
                  tab.metaData.mode == "console"
                ) {
                  var v_message_data = {
                    tab_id: tab.id,
                    tab_db_id: null,
                    conn_tab_id: primaryTab.id,
                  };
                  if (tab.metaData.mode == "query")
                    v_message_data.tab_db_id = tab.metaData.initTabDatabaseId;
                  v_tabs_to_remove.push(v_message_data);
                }

                if (tab.closeFunction) tab.closeFunction(e, tab);
              });

              var v_message_data = {
                conn_tab_id: primaryTab.id,
                tab_db_id: null,
                tab_id: null,
              };
              v_tabs_to_remove.push(v_message_data);

              if (v_tabs_to_remove.length > 0) {
                createRequest(queryRequestCodes.CloseTab, v_tabs_to_remove);
              }
              tabsStore.removeTab(primaryTab);
            });
          },
        });

        connTab.metaData.selectedDatabaseIndex = v_conn.id;
        connTab.metaData.createInitialTabs = createInitialTabs;
        connTab.metaData.change_active_database_call_list = [];
        connTab.metaData.change_active_database_call_running = false;

        tabsStore.selectTab(connTab);
      }
    },
    createTerminalTab(index, alias, details) {
      let tooltipName = "";

      if (alias) {
        tooltipName += `<h5 class="my-1">${alias}</h5>`;
      }
      if (details) {
        tooltipName += `<div class="mb-1">${details}</div>`;
      }

      const tab = tabsStore.addTab({
        name: alias,
        component: "TerminalTab",
        icon: '<i class="fas fa-terminal"></i>',
        tooltip: tooltipName,
        closable: false,
        mode: "outer_terminal",
        selectFunction: function () {
          emitter.emit(`${this.id}_resize`);
        },
        rightClickFunction: (e, tab) => {
          this.terminalContextMenu(e, tab);
        },
      });
      tab.metaData.selectedDatabaseIndex = index;

      tabsStore.selectTab(tab);
    },
    checkTabStatus() {
      const tab = tabsStore.selectedPrimaryTab.metaData.selectedTab;
      switch (tab?.metaData?.mode) {
        case "query":
          emitter.emit(`${tab.id}_check_query_status`);
          break;
        case "console":
          emitter.emit(`${tab.id}_check_console_status`);
          break;
        case "edit":
          console.log("Not implemented"); // TODO: implement check tab status functionality for edit tab
          break;
        default:
          break;
      }
    },
    terminalContextMenu(e, tab) {
      let optionList = [
        {
          label: "Adjust Terminal Dimensions",
          icon: "fas cm-all fa-window-maximize",
          onClick: function () {
            emitter.emit(`${tab.id}_adjust_terminal_dimensions`);
          },
        },
        {
          label: h("p", {
            class: "mb-0 text-danger",
            innerHTML: "Close Terminal",
          }),
          onClick: () => {
            ContextMenu.closeContextMenu();
            ContextMenu.showContextMenu({
              theme: "pgmanage",
              x: e.x,
              y: e.y,
              zIndex: 1000,
              minWidth: 230,
              items: [
                {
                  label: "Confirm",
                  icon: "fas cm-all fa-check",
                  onClick: () => {
                    this.removeTab(tab);
                  },
                },
                {
                  label: "Cancel",
                  icon: "fas cm-all fa-times",
                },
              ],
            });
          },
        },
      ];

      ContextMenu.showContextMenu({
        theme: "pgmanage",
        x: e.x,
        y: e.y,
        zIndex: 1000,
        minWidth: 230,
        items: optionList,
      });
    },
  },
};
</script>
