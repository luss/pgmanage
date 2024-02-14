<template>
  <div
    :id="`${tabId}_panel_snippet`"
    :class="[
      'omnidb__panel omnidb__panel--snippet',
      { 'omnidb__panel--slide-in': isVisible },
    ]"
    style="height: 100vh"
  >
    <button
      type="button"
      class="px-4 btn btn-secondary omnidb__panel__toggler"
      @click="showPanel"
      style="left: 80%;"
    >
    <!-- style above is only for developing purposes, delete after implementing snippet panel-->
      <i class="fas fa-arrows-alt-v"></i>
    </button>

    <div class="container-fluid h-100" style="position: relative">
      <div :id="`${tabId}_snippet_div_layout_grid`" class="row h-100">
        <div
          :id="`${tabId}_snippet_div_left`"
          class="omnidb__snippets__div-left col h-100"
          style="flex: 0 0 300px"
        >
          <div class="row h-100">
            <div class="omnidb__snippets__content-left border-right">
              <div
                :id="`${tabId}_snippet_tree`"
                style="overflow: auto; flex-grow: 1; transition: scroll 0.3s"
              ></div>
            </div>
          </div>
          <div
            :id="`${tabId}_snippet_resize_line_vertical`"
            class="omnidb__resize-line__container--vertical"
          >
            <div class="resize_line_vertical"></div>
          </div>
        </div>
        <div
          :id="`${tabId}_snippet_div_right`"
          class="omnidb__snippets__div-right pt-0 col"
          style="position: relative"
        >
          <div class="row">
            <Tabs
              :id="`${tabId}`"
              class="w-100"
              hierarchy="secondary"
              :conn-tab-id="tabId"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { emitter } from "../emitter";
import Tabs from "./Tabs.vue";
export default {
  components: {
    Tabs,
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
.omnidb__panel--slide-in {
  transform: translateY(-90vh);
}
</style>
