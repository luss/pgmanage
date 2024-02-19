import { defineStore } from "pinia";
import ShortUniqueId from "short-unique-id";

const useTabsStore = defineStore("tabs", {
  state: () => ({
    id: new ShortUniqueId({
      dictionary: "alpha_lower",
      length: 8
    }).randomUUID(),
    tabs: [],
    selectedPrimaryTab: "",
  }),
  getters: {
    selectablePrimaryTabs() {
      return this.tabs.filter((tab) => tab.selectable);
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
        dictionary: "alpha_lower",
        length: 8
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
        dragEndFunction: this.dragEndFunction,
      };
      if (parentId) {
        let primaryTab = this.tabs.find((tab) => tab.id === parentId);
        //TODO: handle case if tab with specified Id not exist
        if (name === "+") {
          primaryTab.metaData.secondaryTabs.push(tab);
        } else {
          primaryTab.metaData.secondaryTabs.splice(-1, 0, tab);
        }
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
      const isPrimaryTab = !tabToRemove.parentId;
      if (isPrimaryTab) {
        this.removePrimaryTab(tabToRemove);
      } else {
        this.removeSecondaryTab(tabToRemove);
      }
    },
    removePrimaryTab(tabToRemove) {
      const tabIndex = this.tabs.indexOf(tabToRemove);
      if (this.selectedPrimaryTab === tabToRemove) {
        const selectableTabs = this.selectablePrimaryTabs;
        const nextTabIndex = selectableTabs.indexOf(tabToRemove) + 1;
        const newSelectedTab =
          nextTabIndex < selectableTabs.length
            ? selectableTabs[nextTabIndex]
            : selectableTabs[nextTabIndex - 2];

        this.selectedPrimaryTab = newSelectedTab;
      }
      this.tabs.splice(tabIndex, 1);
    },
    removeSecondaryTab(tabToRemove) {
      const primaryTab = this.tabs.find(
        (tab) => tab.id === tabToRemove.parentId
      );

      const secondaryTabs = primaryTab.metaData.secondaryTabs;
      const tabIndex = secondaryTabs.indexOf(tabToRemove);
      if (primaryTab.metaData.selectedTab === tabToRemove) {
        const nextTabIndex = tabIndex + 1;

        const newSelectedTab = secondaryTabs[nextTabIndex].selectable
          ? secondaryTabs[nextTabIndex]
          : secondaryTabs[nextTabIndex - 1];
        primaryTab.metaData.selectedTab = newSelectedTab;
      }
      secondaryTabs.splice(tabIndex, 1);
    },
    getSecondaryTabs(parentId) {
      const primaryTabIdx = this.tabs.findIndex((tab) => tab.id === parentId);
      return this.tabs[primaryTabIdx]?.metaData?.secondaryTabs || [];
    },
    getSelectedSecondaryTab(parentId) {
      const primaryTabIdx = this.tabs.findIndex((tab) => tab.id === parentId);
      return this.tabs[primaryTabIdx]?.metaData?.selectedTab;
    },
    dragEndFunction(e, tab) {
      // Get the dragged element and drop position
      let el = e.target;
      let drop_pos_x = e.clientX;
      let drop_pos_y = e.clientY;
      let allNodes = Array.from(el.parentNode.children);
      let oldIndex = allNodes.indexOf(el);

      // Filter out non-draggable siblings
      let siblings = allNodes.filter((node) => node !== el && !!node.draggable);

      // Find the new index based on drop position
      let newIndex = siblings.findIndex((sibling) => {
        let rect = sibling.getBoundingClientRect();
        return (
          drop_pos_x >= rect.left &&
          drop_pos_x <= rect.right &&
          drop_pos_y >= rect.top &&
          drop_pos_y <= rect.bottom
        );
      });

      // Handle case where newIndex is -1 (drop position not found among siblings)
      if (newIndex === -1) {
        newIndex = siblings.length;
      } else if (newIndex === oldIndex) {
        newIndex++;
      }

      // Reorder the tabs based on the new index
      if (oldIndex !== -1 && oldIndex !== newIndex) {
        if (!tab.parentId) {
          let removedEl = this.tabs.splice(oldIndex, 1)[0];
          this.tabs.splice(newIndex, 0, removedEl);
        } else {
          let primaryTab = this.tabs.find(
            (primaryTab) => primaryTab.id === tab.parentId
          );
          let removedEl = primaryTab.metaData.secondaryTabs.splice(
            oldIndex,
            1
          )[0];
          primaryTab.metaData.secondaryTabs.splice(newIndex, 0, removedEl);
        }
      }
    },
    getPrimaryTabById(tabId) {
      return this.tabs.find((tab) => tab.id === tabId);
    },
  },
});

export { useTabsStore };
