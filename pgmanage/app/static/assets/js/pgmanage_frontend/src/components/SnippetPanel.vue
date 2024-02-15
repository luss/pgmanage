<template>
  <div
    :id="`${tabId}_panel_snippet`"
    :class="[
      'panel-body',
      'omnidb__panel omnidb__panel--snippet',
      { 'omnidb__panel--slide-in': isVisible },
    ]"
  >
    <button
      type="button"
      class="px-4 btn btn-secondary omnidb__panel__toggler"
      @click="showPanel"
      style="left: 80%"
    >
      <!-- style above is only for developing purposes, delete after implementing snippet panel-->
      <i class="fas fa-arrows-alt-v"></i>
    </button>

    <div class="container-fluid h-100 position-relative">
      <div :id="`${tabId}_snippet_div_layout_grid`" class="row h-100">
        <splitpanes class="default-theme">
          <pane size="20">
            <div class="omnidb__snippets__div-left col h-100">
              <div class="row h-100">
                <div class="omnidb__snippets__content-left border-right">
                  <div class="snippets-tree">
                    <TreeSnippets />
                  </div>
                </div>
              </div>
            </div>
          </pane>
          <pane>
            <div
              class="omnidb__snippets__div-right pt-0 col h-100 position-relative"
            >
              <div class="row">
                <Tabs
                  :id="`${tabId}`"
                  class="w-100"
                  hierarchy="secondary"
                  :tab-id="tabId"
                />
              </div>
            </div>
          </pane>
        </splitpanes>
      </div>
    </div>
  </div>
</template>

<script>
import { Splitpanes, Pane } from "splitpanes";
import { emitter } from "../emitter";
import Tabs from "./Tabs.vue";
import TreeSnippets from "./TreeSnippets.vue";

export default {
  components: {
    Tabs,
    Splitpanes,
    Pane,
    TreeSnippets,
  },
  data() {
    return {
      isVisible: false,
    };
  },
  props: {
    tabId: String,
  },
  methods: {
    showPanel() {
      $(".omnidb__panel-view--full").removeClass("omnidb__panel-view--full");
      this.isVisible = !this.isVisible;
    },
  },
  mounted() {
    emitter.on(`toggle_snippet_panel`, () => {
      this.showPanel();
    });
  },
};
</script>

<style scoped>
.snippets-tree {
  overflow: auto;
  flex-grow: 1;
  transition: scroll 0.3s;
}

.panel-body {
  height: 100vh;
}
.omnidb__panel--slide-in {
  transform: translateY(-98vh);
}
</style>
