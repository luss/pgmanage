import {
  allowedFileTypes,
  maxFileSizeInKB,
  maxFileSizeInMB,
} from "../constants";
import { showToast } from "../notification_control";
import { emitter } from "../emitter";
import { tabsStore } from "../stores/stores_initializer";

export default {
  methods: {
    handleFileInputChange(e) {
      const [file] = e.target.files;
      if (!file?.type || !allowedFileTypes.includes(file.type)) {
        showToast("error", `File with type '${file.type}' is not supported.`);
        return;
      }

      if (file.size > maxFileSizeInKB) {
        showToast(
          "error",
          `Please select a file that is ${maxFileSizeInMB}MB or less.`
        );
        return;
      }
      try {
        if (window.FileReader) {
          let reader = new FileReader();
          reader.onload = () => {
            emitter.emit(`${this.tabId}_copy_to_editor`, reader.result);
          };
          reader.readAsText(file);

          let selectedTab;
          if (this.$options.name === "SnippetTab") {
            let snippetPanel = tabsStore.tabs.find(
              (tab) => tab.name === "Snippets"
            );
            selectedTab = snippetPanel.metaData.selectedTab;
          } else {
            selectedTab = tabsStore.selectedPrimaryTab.metaData.selectedTab;
          }
          selectedTab.name = file.name;

          if (!!file?.path) {
            selectedTab.metaData.filePath = file.path.replace(file.name, "");
          }
        }
      } catch (err) {
        showToast("error", err);
        e.preventDefault();
        e.stopPropagation();
      }
    },
  },
};
