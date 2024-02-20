<template>
  <div
    :class="`omnidb__tab-menu--container omnidb__tab-menu--container--${hierarchy} omnidb__tab-menu--container--menu-shown`"
  >
    <div
      :class="`omnidb__tab-menu border-bottom omnidb__tab-menu--${hierarchy} omnidb__theme-bg--menu-${hierarchy}`"
    >
      <nav>
        <div
          :class="[
            'nav',
            'nav-tabs',
            {
              'text-nowrap': isSecondaryTab,
              'flex-nowrap': isSecondaryTab,
              'scrollable-menu': isSecondaryTab,
            },
          ]"
        >
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
                  v-if="isSecondaryTab && tab.metaData.mode !== 'add'"
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
import ContextMenu from "@imengyu/vue3-context-menu";

export default {
  components: {
    WelcomeScreen,
    ConsoleTab: defineAsyncComponent(() => import("./ConsoleTab.vue")),
    QueryTab: defineAsyncComponent(() => import("./QueryTab.vue")),
    MonitoringDashboard: defineAsyncComponent(() =>
      import("./MonitoringDashboard.vue")
    ),
    ConfigTab: defineAsyncComponent(() => import("./ConfigTab.vue")),
    BackupTab: defineAsyncComponent(() => import("./BackupTab.vue")),
    RestoreTab: defineAsyncComponent(() => import("./RestoreTab.vue")),
    ERDTab: defineAsyncComponent(() => import("./ERDTab.vue")),
    DataEditorTab: defineAsyncComponent(() => import("./DataEditorTab.vue")),
    SchemaEditorTab: defineAsyncComponent(() =>
      import("./SchemaEditorTab.vue")
    ),
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
        mode: "add",
        clickFunction: (event) => {
          if (tabsStore.getPrimaryTabById(this.tabId).name === "Snippets") {
            this.createSnippetTab();
          } else {
            this.showMenuNewTab(event);
          }
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

      emitter.on(`${this.tabId}_create_query_tab`, (data) => {
        this.createQueryTab(
          data?.name,
          data?.tabDbId,
          data?.tabDbName,
          data?.initialQuery
        );
      });

      emitter.on(`${this.tabId}_create_conf_tab`, () => {
        this.createConfigurationTab();
      });

      emitter.on(
        `${this.tabId}_create_utility_tab`,
        ({ node, utility, backupType = "objects" }) => {
          this.createUtilityTab(node, utility, backupType);
        }
      );

      emitter.on(`${this.tabId}_create_erd_tab`, (schema) => {
        this.createERDTab(schema);
      });

      emitter.on(
        `${this.tabId}_create_data_editor_tab`,
        ({ table, schema = "" }) => {
          this.createDataEditorTab(table, schema);
        }
      );

      emitter.on(
        `${this.tabId}_create_schema_editor_tab`,
        ({ node, mode, dialect }) => {
          this.createSchemaEditorTab(node, mode, dialect);
        }
      );
    }
  },
  unmounted() {
    emitter.all.delete(`${this.tabId}_create_console_tab`);
    emitter.all.delete(`${this.tabId}_create_query_tab`);
    emitter.all.delete(`${this.tabId}_create_utility_tab`);
    emitter.all.delete(`${this.tabId}_create_erd_tab`);
    emitter.all.delete(`${this.tabId}_create_data_editor_tab`);
  },
  methods: {
    getCurrentProps(tab) {
      let primaryTab;
      if (tab.parentId) {
        primaryTab = tabsStore.getPrimaryTabById(tab.parentId);
      }
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
          connId: tab.parentId,
          tabId: tab.id,
          consoleHelp: primaryTab?.metaData?.consoleHelp,
          databaseIndex: primaryTab?.metaData?.selectedDatabaseIndex,
          dialect: primaryTab?.metaData?.selectedDBMS,
        },
        QueryTab: {
          connId: tab.parentId,
          tabId: tab.id,
          databaseIndex: primaryTab?.metaData?.selectedDatabaseIndex,
          dialect: primaryTab?.metaData?.selectedDBMS,
          databaseName:
            tab.metaData.databaseName ?? primaryTab?.metaData?.selectedDatabase,
          initTabDatabaseId: tab.metaData.initTabDatabaseId,
          initialQuery: tab.metaData.initialQuery,
        },
        MonitoringDashboard: {
          connId: tab.parentId,
          tabId: tab.id,
          databaseIndex: primaryTab?.metaData?.selectedDatabaseIndex,
        },
        BackupTab: {
          connId: tab.parentId,
          tabId: tab.id,
          databaseIndex: primaryTab?.metaData?.selectedDatabaseIndex,
          backupType: tab.metaData.backupType,
          treeNode: tab.metaData.treeNode,
        },
        RestoreTab: {
          connId: tab.parentId,
          tabId: tab.id,
          databaseIndex: primaryTab?.metaData?.selectedDatabaseIndex,
          restoreType: tab.metaData.backupType,
          treeNode: tab.metaData.treeNode,
        },
        ERDTab: {
          tabId: tab.parentId,
          databaseIndex: primaryTab?.metaData?.selectedDatabaseIndex,
          databaseName: primaryTab?.metaData?.selectedDatabase,
          schema: tab.metaData?.schema,
        },
        DataEditorTab: {
          connId: tab.parentId,
          tabId: tab.id,
          databaseIndex: primaryTab?.metaData?.selectedDatabaseIndex,
          databaseName: primaryTab?.metaData?.selectedDatabase,
          table: tab.metaData.table,
          schema: tab.metaData.schema,
          dialect: tab.metaData.dialect,
          query_filter: tab.metaData.dialect,
        },
        SchemaEditorTab: {
          connId: tab.parentId,
          tabId: tab.id,
          databaseIndex: primaryTab?.metaData?.selectedDatabaseIndex,
          databaseName: primaryTab?.metaData?.selectedDatabase,
          mode: tab.metaData.editMode,
          schema: tab.metaData.schema,
          table: tab.metaData.table,
          treeNode: tab.metaData.treeNode,
          dialect: tab.metaData.dialect,
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
          selectFunction: () => {
            document.title = "PgManage";
            this.checkTabStatus();
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
    createMonitoringDashboardTab() {
      const tab = tabsStore.addTab({
        parentId: this.tabId,
        name: "Monitoring",
        component: "MonitoringDashboard",
        mode: "monitoring_dashboard",
        selectFunction: function () {
          emitter.emit(`${this.id}_redraw_widget_grid`);
        },
        closeFunction: function (e, tab) {
          beforeCloseTab(e, function () {
            tabsStore.removeTab(tab);
          });
        },
        // p_dblClickFunction: renameTab, //TODO: implement rename functionality
      });

      tabsStore.selectTab(tab);
    },
    createQueryTab(
      name = "Query",
      tabDbId = null,
      tabDbName = null,
      initialQuery = null
    ) {
      const tab = tabsStore.addTab({
        parentId: this.tabId,
        name: name,
        component: "QueryTab",
        mode: "query",
        selectFunction: function () {
          emitter.emit(`${this.id}_check_query_status`);
        },
        closeFunction: (e, tab) => {
          beforeCloseTab(e, () => {
            this.removeTab(tab);
          });
        },
        // dblClickFunction: renameTab //TODO: implement rename functionality
      });
      tab.metaData.databaseName = tabDbName;
      tab.metaData.initTabDatabaseId = tabDbId;
      tab.metaData.initialQuery = initialQuery;
      tabsStore.selectTab(tab);
    },
    createConfigurationTab() {
      const tab = tabsStore.addTab({
        parentId: this.tabId,
        name: "Configuration",
        component: "ConfigTab",
        mode: "configuration",
        closeFunction: (e, tab) => {
          beforeCloseTab(e, () => {
            this.removeTab(tab);
          });
        },
      });
      tabsStore.selectTab(tab);
    },
    createUtilityTab(node, utility, backupType = "objects") {
      let utilityTitle =
        backupType === "objects"
          ? `(${node.data.type}:${node.title})`
          : backupType;
      let tabName = `${utility} ${utilityTitle}`;
      let mode = utility.toLowerCase();

      const tab = tabsStore.addTab({
        parentId: this.tabId,
        name: tabName,
        mode: mode,
        component: `${utility}Tab`,
        closeFunction: (e, tab) => {
          beforeCloseTab(e, () => {
            this.removeTab(tab);
          });
        },
      });

      tab.metaData.treeNode = node;
      tab.metaData.backupType = backupType;

      tabsStore.selectTab(tab);
    },
    createERDTab(schema = "") {
      let tabName = schema ? `ERD: ${schema}` : "ERD";

      const tab = tabsStore.addTab({
        parentId: this.tabId,
        name: tabName,
        component: "ERDTab",
        icon: '<i class="fab fa-hubspot icon-tab-title"></i>',
        selectFunction: function () {
          document.title = "PgManage";
        },
        closeFunction: (e, tab) => {
          beforeCloseTab(e, () => {
            this.removeTab(tab);
          });
        },
      });

      tab.metaData.schema = schema;

      tabsStore.selectTab(tab);
    },
    createDataEditorTab(table, schema = "") {
      let tabName = schema
        ? `Edit data: ${schema}.${table}`
        : `Edit data: ${table}`;

      const tab = tabsStore.addTab({
        parentId: this.tabId,
        name: tabName,
        component: "DataEditorTab",
        closeFunction: (e, tab) => {
          beforeCloseTab(e, () => {
            this.removeTab(tab);
          });
        },
      });

      const DIALECT_MAP = {
        oracle: "oracledb",
        mariadb: "mysql",
      };
      let dialect = tabsStore.selectedPrimaryTab.metaData.selectedDBMS;
      let mappedDialect = DIALECT_MAP[dialect] || dialect;

      tab.metaData.dialect = mappedDialect;
      tab.metaData.table = table;
      tab.metaData.schema = schema;
      tab.metaData.query_filter = ""; //to be used in the future for passing extra filters when tab is opened

      tabsStore.selectTab(tab);
    },
    createSchemaEditorTab(node, mode, dialect) {
      let tableName = node.title.replace(/^"(.*)"$/, "$1");
      let tabTitle = mode === "alter" ? `Alter: ${tableName}` : "New Table";

      const tab = tabsStore.addTab({
        parentId: this.tabId,
        name: tabTitle,
        component: "SchemaEditorTab",
        closeFunction: (e, tab) => {
          beforeCloseTab(e, () => {
            this.removeTab(tab);
          });
        },
      });

      tab.metaData.dialect = dialect || "postgres";
      tab.metaData.editMode = mode;
      tab.metaData.schema = node.data.schema;
      tab.metaData.table = mode === "alter" ? tableName : null;
      tab.metaData.treeNode = node;

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
    showMenuNewTab(e) {
      let optionList = [
        {
          label: "Query Tab",
          icon: "fas cm-all fa-search",
          onClick: () => {
            this.createQueryTab();
          },
        },
        {
          label: "Console Tab",
          icon: "fas cm-all fa-terminal",
          onClick: () => {
            this.createConsoleTab();
          },
        },
      ];

      if (
        ["postgresql", "mysql", "mariadb"].includes(
          tabsStore.selectedPrimaryTab.metaData.selectedDBMS
        )
      ) {
        optionList.push({
          label: "Monitoring Dashboard",
          icon: "fas cm-all fa-chart-line",
          onClick: () => {
            this.createMonitoringDashboardTab();
          },
        });
      }

      if (tabsStore.selectedPrimaryTab.metaData.selectedDBMS === "postgresql") {
        optionList.push({
          label: "Backends",
          icon: "fas cm-all fa-tasks",
          onClick: () => {
            console.log("Not implemented");
            // this.createMonitoringTab(
            // 		'Backends',
            // 		'select * from pg_stat_activity', [{
            // 				icon: 'fas fa-times action-grid action-close',
            // 				title: 'Terminate',
            // 				action: 'postgresqlTerminateBackend'
            // 		}]);
          },
        });
      } else if (
        ["mysql", "mariadb"].includes(
          tabsStore.selectedPrimaryTab.metaData.selectedDBMS
        )
      ) {
        optionList.push({
          label: "Process List",
          icon: "fas cm-all fa-tasks",
          onClick: () => {
            console.log("Not implemented");
            // this.createMonitoringTab(
            // 		'Process List',
            // 		'select * from information_schema.processlist', [{
            // 				icon: 'fas fa-times action-grid action-close',
            // 				title: 'Terminate',
            // 				action: 'mysqlTerminateBackend'
            // 		}]);
          },
        });
      }

      ContextMenu.showContextMenu({
        theme: "pgmanage",
        x: e.x,
        y: e.y,
        zIndex: 1000,
        minWidth: 230,
        items: optionList,
      });
    },
    removeTab(tab) {
      if (
        ["query", "edit", "console", "outer_terminal"].includes(
          tab.metaData.mode
        )
      ) {
        let messageData = {
          tab_id: tab.id,
          tab_db_id: null,
          conn_tab_id: tabsStore.selectedPrimaryTab.id,
        };
        if (tab.metaData.mode === "query") {
          messageData.tab_db_id = tab.metaData.initTabDatabaseId;
        }

        createRequest(queryRequestCodes.CloseTab, [messageData]);
      }

      tabsStore.removeTab(tab);
    },
  },
};
</script>

<style scoped>
.scrollable-menu {
  overflow-y: hidden;
  overflow-x: auto;
}
</style>
