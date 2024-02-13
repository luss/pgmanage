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
            :title="tab.tooltip"
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
            @dragend="dragEndFunction"
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
                {{ tab.name }}
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
        :id="tab.id"
        :is="tab.component"
        v-show="tab.id == selectedTab.id"
        v-bind="getCurrentProps(tab)"
      ></component>
    </div>
  </div>
</template>

<script>
import WelcomeScreen from "./WelcomeScreen.vue";
import ConnectionTab from "./ConnectionTab.vue";
import { showMenuNewTabOuter } from "../workspace.js";
import { tabsStore } from "../stores/stores_initializer";
import { emitter } from "../emitter";
import { connectionsStore } from "../stores/connections";
import { showToast } from "../notification_control";
import moment from "moment";
import { beforeCloseTab } from "../create_tab_functions";
import { createRequest } from "../long_polling";
import { queryRequestCodes } from "../constants";

export default {
  components: {
    WelcomeScreen,
    ConnectionTab,
  },
  props: {
    hierarchy: {
      type: String,
      validator(value) {
        return ["primary", "secondary"].includes(value);
      },
    },
    connTabId: {
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
        return tabsStore.getSecondaryTabs(this.connTabId);
      }
    },
    selectedTab() {
      if (this.hierarchy === "primary") {
        return tabsStore.selectedPrimaryTab;
      } else {
        return tabsStore.getSelectedSecondaryTab(this.connTabId);
      }
    },
  },
  methods: {
    getCurrentProps(tab) {
      const componentsProps = {
        ConnectionTab: {
          "conn-tab-id": tab.id,
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
    dragEndFunction(event) {
      console.log("Not implemented");
    },
    createConnectionTab(
      index,
      create_query_tab = true,
      name = false,
      tooltip_name = false
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

        if (!tooltip_name) {
          tooltip_name = "";

          if (v_conn.conn_string && v_conn.conn_string !== "") {
            if (v_conn.alias) {
              tooltip_name += `<h5 class="my-1">${v_conn.alias}</h5>`;
            }
            tooltip_name += `<div class="mb-1">${v_conn.conn_string}</div>`;
          } else {
            if (v_conn.alias) {
              tooltip_name += `<h5 class="my-1">${v_conn.alias}</h5>`;
            }
            if (v_conn.details1) {
              tooltip_name += `<div class="mb-1">${v_conn.details1}</div>`;
            }
            if (v_conn.details2) {
              tooltip_name += `<div class="mb-1">${v_conn.details2}</div>`;
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

          let v_icon = `<img src="${v_url_folder}${imgPath}${imgName}.svg"/>`;

          const connTab = tabsStore.addTab({
            name: connName,
            component: "ConnectionTab",
            icon: v_icon,
            tooltip: tooltip_name,
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
                    tab.tag.mode == "query" ||
                    tab.tag.mode == "edit" ||
                    tab.tag.mode == "debug" ||
                    tab.tag.mode == "console"
                  ) {
                    var v_message_data = {
                      tab_id: tab.id,
                      tab_db_id: null,
                      conn_tab_id: primaryTab.id,
                    };
                    if (tab.mode == "query")
                      v_message_data.tab_db_id = tab.tag.tab_db_id;
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

          connTab.tag = {
            mode: "connection",
            selectedDatabaseIndex: 0,
          };
          tabsStore.selectTab(connTab);
        }
      }
    },
  },
  mounted() {
    tabsStore.$onAction((action) => {
      if (action.name == "addTab") {
        action.after((result) => {
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
        icon: '<i class="fas fa-bolt"></i>',
        name: "Connections",
        closable: false,
        selectable: false,
        tooltip: "Connections",
        clickFunction: function (e) {
          showMenuNewTabOuter(e);
        },
      });

      const welcomeTab = tabsStore.addTab({
        icon: '<i class="fas fa-hand-spock"></i>',
        name: "Welcome",
        selectFunction: function () {
          document.title = "Welcome to PgManage";
        },
        closable: false,
        tooltip: "Welcome to PgManage",
        component: "WelcomeScreen",
      });
      tabsStore.selectTab(welcomeTab);

      emitter.on(
        `${tabsStore.id}_create_conn_tab`,
        (
          index,
          create_query_tab = true,
          name = false,
          tooltip_name = false
        ) => {
          this.createConnectionTab(index, create_query_tab, name, tooltip_name);
        }
      );
    }
  },
};
</script>
