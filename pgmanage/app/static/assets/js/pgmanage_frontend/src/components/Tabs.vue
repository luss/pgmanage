<template>
  <div
    :class="`omnidb__tab-menu--container omnidb__tab-menu--container--${hierarchy} omnidb__tab-menu--container--menu-shown`"
  >
    <div
      :class="`omnidb__tab-menu border-bottom omnidb__tab-menu--${hierarchy} omnidb__theme-bg--menu-${hierarchy}`"
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
            :href="`#div_${tab.id}`"
            :aria-controls="`div_${tab.id}`"
            :draggable="tab.isDraggable"
            @dragend="tab.dragEndFunction($event, tab)"
            @click.prevent.stop="clickHandler($event, tab)"
            @dblclick="tab.dblClickFunction"
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
                <span
                  v-if="isSecondaryTab && tab.name !== '+'"
                  :class="{ invisible: !tab.metaData.isLoading }"
                >
                  <i class="tab-icon node-spin"></i>
                </span>
                <i
                  v-if="isSecondaryTab"
                  :class="[
                    'fas',
                    'fa-check-circle',
                    'tab-icon',
                    'icon-check',
                    { 'd-none': !tab.metaData.isReady },
                  ]"
                ></i>
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

    <div
      :class="`tab-content omnidb__tab-content omnidb__tab-content--${hierarchy}`"
    >
      <component
        v-for="tab in tabs"
        :key="tab.id"
        :is="tab.component"
        v-show="tab.id === selectedTab.id || tab.name === 'Snippets'"
        v-bind="getCurrentProps(tab)"
      ></component>
    </div>
  </div>
</template>

<script>
import WelcomeScreen from "./WelcomeScreen.vue";
import { showMenuNewTabOuter } from "../workspace.js";
import { tabsStore } from "../stores/stores_initializer";
import { emitter } from "../emitter";
import { connectionsStore } from "../stores/connections";
import { showToast } from "../notification_control";
import moment from "moment";
import { beforeCloseTab } from "../create_tab_functions";
import { createRequest } from "../long_polling";
import { queryRequestCodes } from "../constants";
import { defineAsyncComponent } from "vue";

export default {
  components: {
    WelcomeScreen,
    ConsoleTab: defineAsyncComponent(() => import("./ConsoleTab.vue")),
  },
  props: {
    hierarchy: {
      type: String,
      validator(value) {
        return ["primary", "secondary"].includes(value);
      },
    },
    tabId: {
      type: String,
    },
  },
  data() {
    return {};
  },
  computed: {
    tabs() {
      if (this.hierarchy === "primary") {
        return tabsStore.tabs;
      } else {
        return tabsStore.getSecondaryTabs(this.tabId);
      }
    },
    selectedTab() {
      if (this.hierarchy === "primary") {
        return tabsStore.selectedPrimaryTab;
      } else {
        return tabsStore.getSelectedSecondaryTab(this.tabId);
      }
    },
    isSecondaryTab() {
      return this.hierarchy === "secondary";
    },
    isSnippetsPanel() {
      if (!!this.tabId) {
        let primaryTab = tabsStore.getPrimaryTabById(this.tabId);
        return primaryTab?.name === "Snippets";
      }
      return false;
    },
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
        SnippetTab: {
          "tab-id": tab.id,
          snippet: tab.metaData.snippetObject,
        },
        ConsoleTab: {
          connId: this.tabId,
          tabId: tab.id,
          consoleHelp: tabsStore.selectedPrimaryTab.metaData.consoleHelp,
          databaseIndex:
            tabsStore.selectedPrimaryTab.metaData.selectedDatabaseIndex,
          dialect: tabsStore.selectedPrimaryTab.metaData.selectedDBMS,
        },
      };

      return componentsProps[tab.component];
    },
    clickHandler(event, tab) {
      if (tab.selectable) {
        tabsStore.selectTab(tab);
      }

      if (tab.clickFunction != null) {
        tab.clickFunction(event);
      }

      if (tab.tooltip) {
        $('[data-toggle="tab"]').tooltip("hide");
      }
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
          selectFunction: function () {
            document.title = "PgManage";
            // TODO: add missing code
          },
          closeFunction: function (e, primaryTab) {
            $('[data-toggle="tab"]').tooltip("hide");
            beforeCloseTab(e, function () {
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
                    v_message_data.tab_db_id = tab.metaData.tab_db_id;
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
    createSnippetTab(snippet) {
      let snippetName = "New Snippet";

      let snippetDetails = {
        id: null,
        name: null,
        parent: null,
        type: "snippet",
      };

      if (snippet) {
        snippetName = snippet.name;
        snippetDetails = {
          id: snippet.id,
          name: snippetName,
          parent: snippet.id_parent,
          type: "snippet",
        };
      }

      let tab = tabsStore.addTab({
        name: snippetName,
        parentId: this.tabId,
        component: "SnippetTab",
        mode: "snippet",
        selectFunction: function () {
          emitter.emit(`${this.id}_editor_focus`);
          emitter.emit(`${this.id}_resize`);
        },
        closeFunction: function (e, tab) {
          beforeCloseTab(e, function () {
            tabsStore.removeTab(tab);
          });
        },
      });

      tab.metaData.snippetObject = snippetDetails;

      tabsStore.selectTab(tab);
    },
    createConsoleTab() {
      const tab = tabsStore.addTab({
        parentId: this.tabId,
        name: "Console",
        component: "ConsoleTab",
        icon: "<i class='fas fa-terminal icon-tab-title'></i>",
        mode: "console",
        selectFunction: function () {
          emitter.emit(`${this.id}_resize`);
          emitter.emit(`${this.id}_check_console_status`);
        },
        closeFunction: function (e, tab) {
          beforeCloseTab(e, function () {
            tabsStore.removeTab(tab);
          });
        },
      });

      tabsStore.selectTab(tab);
    },
  },
  mounted() {
    tabsStore.$onAction((action) => {
      if (action.name == "addTab") {
        action.after((result) => {
          if (!result.tooltip) return;
          this.$nextTick(() => {
            $(`#${result.id}`).tooltip({
              placement: "right",
              boundary: "window",
              sanitize: false,
              title: result.tooltip,
              html: true,
              delay: { show: 500, hide: 100 },
            });
          });
        });
      }
    });

    if (this.hierarchy == "primary") {
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

      const welcomeTab = tabsStore.addTab({
        name: "Welcome",
        component: "WelcomeScreen",
        icon: '<i class="fas fa-hand-spock"></i>',
        tooltip: "Welcome to PgManage",
        closable: false,
        selectFunction: function () {
          document.title = "Welcome to PgManage";
        },
      });
      tabsStore.selectTab(welcomeTab);

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
    } else {
      tabsStore.addTab({
        name: "+",
        parentId: this.tabId,
        closable: false,
        isDraggable: false,
        selectable: false,
        clickFunction: () => {
          //TODO: depending on tab mode should different click function implementation
          this.createSnippetTab();
        },
      });

      if (this.isSnippetsPanel) {
        emitter.on("create_snippet_tab", (snippet) => {
          this.createSnippetTab(snippet);
        });
        this.createSnippetTab();
      }

      emitter.on(`${this.tabId}_create_console_tab`, () => {
        this.createConsoleTab();
      });
    }
  },
};
</script>
