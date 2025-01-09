import { defineStore } from "pinia";

const useCellDataModalStore = defineStore("cellDataModal", {
  state: () => ({
    visible: false,
    cellContent: null,
    cellType: null,
  }),
  actions: {
    showModal(cellContent, cellType) {
      this.cellContent = cellContent;
      this.cellType = cellType;
      this.visible = true;
    },
    hideModal() {
      this.visible = false;
      this.cellContent = null;
      this.cellType = null;
    },
  },
});

export { useCellDataModalStore };
