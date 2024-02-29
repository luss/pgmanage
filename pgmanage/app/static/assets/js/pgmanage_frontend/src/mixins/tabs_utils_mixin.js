import { tabsStore } from "../stores/stores_initializer.js";
import { createRequest } from "../long_polling.js";
import { queryRequestCodes } from "../constants.js";
import { showConfirm } from "../notification_control.js";
import ContextMenu from "@imengyu/vue3-context-menu";

export default {
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
  },
  methods: {
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
    contextMenuHandler(event, tab) {
      if (tab.rightClickFunction) {
        event.stopPropagation();
        event.preventDefault();
        tab.rightClickFunction(event, tab);
      }
      if (tab.tooltip) {
        $('[data-toggle="tab"]').tooltip("hide");
      }
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

        if (tab.metaData.mode === "outer_terminal") {
          messageData.tab_id = null;
        }

        createRequest(queryRequestCodes.CloseTab, [messageData]);
      }

      tabsStore.removeTab(tab);
    },
    beforeCloseTab(e, confirmFunction) {
      if (e) {
        if (e.clientX == 0 && e.clientY == 0) {
          showConfirm("Are you sure you want to remove this tab?", function () {
            confirmFunction();
          });
        } else {
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
                onClick: function () {
                  confirmFunction();
                },
              },
              {
                label: "Cancel",
                icon: "fas cm-all fa-times",
              },
            ],
          });
        }
      } else {
        confirmFunction();
      }
    },
  },
};
