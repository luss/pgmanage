<template>
  <div class="container-fluid position-relative">
    <div class="row">
      <div
        :id="`${connTabId}_div_left`"
        class="omnidb__workspace__div-left col-2"
      >
        <div class="row">
          <div class="omnidb__workspace__content-left border-right">
            <div class="omnidb__workspace__connection-details">
              <i class="fas fa-server mr-1"></i>selected DB:
              <b>{{ databaseName }}</b>
              <div
                class="omnidb__switch omnidb__switch--sm float-right"
                data-toggle="tooltip"
                data-placement="bottom"
                data-html="true"
                title=""
                data-original-title="<h5>Toggle autocomplete.</h5><div>Switch OFF <b>disables the autocomplete</b> on the inner tabs for this connection.</div>"
              >
                <input
                  type="checkbox"
                  :id="`${connTabId}_autocomplete`"
                  class="omnidb__switch--input"
                  v-model="autocompleteStatus"
                  @change="emitConnectionSave"
                />
                <label
                  :for="`${connTabId}_autocomplete`"
                  class="omnidb__switch--label"
                  @change="toggleConnectionAutocomplete"
                >
                  <span>
                    <i class="fas fa-spell-check"></i>
                  </span>
                </label>
              </div>
            </div>

            <div :id="`${connTabId}_tree`" class="database-tree">
              <component
                :is="treeComponent"
                :tab-id="connTabId"
                :database-index="databaseIndex"
              ></component>
            </div>
            <div
              :id="`${connTabId}_left_resize_line_horizontal`"
              class="omnidb__resize-line__container--horizontal"
            >
              <div class="resize_line_horizontal"></div>
              <div style="height: 5px"></div>
            </div>
            <div
              :id="`tree_tabs_parent_${connTabId}`"
              class="omnidb__tree-tabs--not-in-view omnidb__tree-tabs"
              style="position: relative; flex-shrink: 0"
            >
              <div
                :id="`${connTabId}_loading`"
                class="div_loading"
                style="z-index: 1000"
              >
                <div class="div_loading_cover"></div>
                <div class="div_loading_content">
                  <div
                    class="spinner-border text-primary"
                    style="width: 4rem; height: 4rem"
                    role="status"
                  >
                    <span class="sr-only">Loading...</span>
                  </div>
                </div>
              </div>
              <button
                type="button"
                class="btn btn-icon btn-icon-secondary omnidb__tree-tabs__toggler mr-2"
              >
                <i class="fas fa-arrows-alt-v"></i>
              </button>
              <div
                :id="`tree_tabs_${connTabId}`"
                class="omnidb__tree-tabs__container"
                style="position: relative"
              ></div>
            </div>
          </div>
        </div>
        <div
          :id="`${connTabId}_left_resize_line_vertical`"
          class="omnidb__resize-line__container--vertical"
        >
          <div class="resize_line_vertical"></div>
        </div>
      </div>
      <div
        :id="`${connTabId}_div_right`"
        class="omnidb__workspace__div-right col-10 position-relative"
      >
        <div class="row">
          <button
            :id="`${connTabId}_tree_toggler`"
            type="button"
            class="py-4 px-0 btn btn-secondary omnidb__tree__toggler"
          >
            <i class="fas fa-arrows-alt-h"></i>
          </button>
          <Tabs
            :id="`${connTabId}`"
            class="w-100"
            hierarchy="secondary"
            :tab-id="connTabId"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Tabs from "./Tabs.vue";
import { connectionsStore } from "../stores/connections";
import { tabsStore } from "../stores/stores_initializer";
import axios from "axios";
import { defineAsyncComponent } from "vue";
import { emitter } from "../emitter";
import { truncateText } from "../utils";

export default {
  name: "ConnectionTab",
  components: {
    Tabs,
    TreePostgresql: defineAsyncComponent(() => import("./TreePostgresql.vue")),
    TreeSqlite: defineAsyncComponent(() => import("./TreeSqlite.vue")),
    TreeMariaDB: defineAsyncComponent(() => import("./TreeMariaDB.vue")),
    TreeOracle: defineAsyncComponent(() => import("./TreeOracle.vue")),
    TreeMysql: defineAsyncComponent(() => import("./TreeMysql.vue")),
  },
  props: {
    connTabId: String,
  },
  data() {
    return {};
  },
  computed: {
    connectionTab() {
      return tabsStore.getPrimaryTabById(this.connTabId);
    },
    databaseConnection() {
      return connectionsStore.getConnection(this.databaseIndex);
    },
    autocompleteStatus: {
      get() {
        return this.databaseConnection.autocomplete;
      },
      set(value) {
        let connection = connectionsStore.getConnection(this.databaseIndex);
        connection.autocomplete = value;
      },
    },
    databaseIndex() {
      return this.connectionTab.metaData.selectedDatabaseIndex;
    },
    databaseTechnology() {
      return this.connectionTab.metaData.selectedDBMS;
    },
    databaseName() {
      if (this.databaseTechnology === "sqlite") {
        return truncateText(this.connectionTab.metaData.selectedDatabase, 10);
      }
      return this.connectionTab.metaData.selectedDatabase;
    },
    treeComponent() {
      const treeTechnologiesMap = {
        postgresql: "TreePostgresql",
        sqlite: "TreeSqlite",
        mysql: "TreeMysql",
        mariadb: "TreeMariaDB",
        oracle: "TreeOracle",
      };
      return treeTechnologiesMap[this.databaseTechnology];
    },
  },
  mounted() {
    this.changeDatabase(this.connectionTab.metaData.selectedDatabaseIndex);
    $('[data-toggle="tooltip"]').tooltip({ animation: true }); // Loads or Updates all tooltips
  },
  methods: {
    changeDatabase(value) {
      let connObject = null;

      // Finding the connection object.
      for (let i = 0; i < connectionsStore.connections.length; i++) {
        if (value == connectionsStore.connections[i].id) {
          connObject = connectionsStore.connections[i];
          break;
        }
      }

      // Selecting the first connection when none is found.

      if (!connObject) {
        connObject = connectionsStore.connections[0];
      }

      let tabData = tabsStore.getPrimaryTabById(this.connTabId);

      tabData.metaData.selectedDatabaseIndex = value;
      tabData.metaData.selectedDBMS = connObject.technology;
      tabData.metaData.consoleHelp = connObject.console_help;
      tabData.metaData.selectedDatabase =
        connObject.last_used_database || connObject.service;
      tabData.metaData.selectedTitle = connObject.alias;

      this.queueChangeActiveDatabaseThreadSafe({
        database_index: value,
        tab_id: this.connTabId,
        database: tabData.metaData.selectedDatabase,
      });
    },
    queueChangeActiveDatabaseThreadSafe(data) {
      this.connectionTab.metaData.change_active_database_call_list.push(data);
      if (!this.connectionTab.metaData.change_active_database_call_running) {
        this.changeActiveDatabaseThreadSafe(
          this.connectionTab.metaData.change_active_database_call_list.pop()
        );
      }
    },
    changeActiveDatabaseThreadSafe(data) {
      this.connectionTab.metaData.change_active_database_call_running = true;
      axios
        .post("/change_active_database/", data)
        .then((resp) => {
          this.connectionTab.metaData.change_active_database_call_running = false;
          if (
            this.connectionTab.metaData.change_active_database_call_list
              .length > 0
          )
            this.changeActiveDatabaseThreadSafe(
              this.connectionTab.metaData.change_active_database_call_list.pop()
            );
        })
        .catch((error) => {
          console.log(error);
        });
    },
    emitConnectionSave() {
      let connection = connectionsStore.getConnection(this.databaseIndex);
      emitter.emit("connection-save", connection);
    },
  },
};
</script>

<style scoped>
.database-tree {
  overflow: auto;
  flex-grow: 1;
  transition: scroll 0.3s;
}
</style>
