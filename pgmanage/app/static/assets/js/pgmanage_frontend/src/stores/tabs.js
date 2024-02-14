import { defineStore } from "pinia";
import ShortUniqueId from "short-unique-id";

const useTabsStore = defineStore("tabs", {
  state: () => ({
    id: new ShortUniqueId({
      dictionary: "alphanum_lower",
    }).randomUUID(),
    tabs: [],
    selectedPrimaryTab: "",
  }),
  getters: {
    formattedPrimaryTabs() {
      return this.tabs.map((tab) => tab.tab);
    },
  },
  actions: {
    addTab({
      parentId = null,
      name = "",
      component = null,
      icon = false,
      tooltip = false,
      disabled = false,
      isDraggable = true,
      selectable = true,
      clickFunction = null,
      closable = true,
      closeFunction = null,
      dblClickFunction = null,
      rightClickFunction = false,
      selectFunction = null,
    }) {
      let tabId = new ShortUniqueId({
        dictionary: "alphanum_lower",
      }).randomUUID();

      let tab = {
        id: tabId,
        parentId: parentId,
        name: name,
        component: component,
        icon: icon,
        tooltip: tooltip,
        disabled: disabled,
        isDraggable: isDraggable,
        selectable: selectable,
        closable: closable,
        clickFunction: clickFunction,
        selectFunction: selectFunction,
        dblClickFunction: dblClickFunction,
        closeFunction: closeFunction,
        rightClickFunction: rightClickFunction,
        metaData: {
          secondaryTabs: [],
          selectedTab: "",
        },
      };
      if (parentId) {
        let primaryTab = this.tabs.find((tab) => tab.id === parentId);
        //TODO: handle case if tab with specified Id not exist
        primaryTab.metaData.secondaryTabs.push(tab);
      } else {
        this.tabs.push(tab);
      }
      return tab;
    },
    selectTab(tab) {
      if (tab.parentId) {
        let primaryTab = this.tabs.find(
          (primaryTab) => primaryTab.id === tab.parentId
        );
        primaryTab.metaData.selectedTab = tab;
      } else {
        this.selectedPrimaryTab = tab;
      }

      if (tab.selectFunction != null) {
        tab.selectFunction();
      }
    },
    removeTab(tabToRemove) {
      if (tabToRemove.parentId) {
        let primaryTab = this.tabs.find(
          (primaryTab) => primaryTab.id === tabToRemove.parentId
        );
        let tabIndex = primaryTab.metaData.secondaryTabs.indexOf(tabToRemove);

        if (primaryTab.metaData.selectedTab === tabToRemove) {
          if (tabIndex > 0) {
            primaryTab.metaData.selectedTab =
              primaryTab.metaData.secondaryTabs[tabIndex - 1]; // fix this
          }
        }

        primaryTab.metaData.secondaryTabs.splice(tabIndex, 1);
      } else {
        let tabIndex = this.tabs.indexOf(tabToRemove);

        if (this.selectedPrimaryTab === tabToRemove) {
          if (tabIndex > 0) {
            this.selectedPrimaryTab = this.tabs[tabIndex - 1]; // fix this
          }
        }

        this.tabs.splice(tabIndex, 1);
      }
    },
    getSecondaryTabs(parentId) {
      const primaryTabIdx = this.tabs.findIndex((tab) => tab.id === parentId);
      return this.tabs[primaryTabIdx]?.metaData?.secondaryTabs || [];
    },
    getSelectedSecondaryTab(parentId) {
      const primaryTabIdx = this.tabs.findIndex((tab) => tab.id === parentId);
      return this.tabs[primaryTabIdx]?.metaData?.selectedTab;
    },
  },
});

export { useTabsStore };
