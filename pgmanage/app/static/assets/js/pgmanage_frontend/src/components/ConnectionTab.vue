<template>
  <div style="position: relative">
    <div
      style="
        display: grid;
        grid-template-areas: \'left right\';
        grid-template-columns: auto minmax(0, 1fr);
      "
    >
      <div
        :id="`${connTabId}_div_left`"
        class="omnidb__workspace__div-left col"
        style="max-width: 300px; width: 300px"
      >
        <div class="row">
          <div class="omnidb__workspace__content-left border-right">
            <div
              :id="`${connTabId}_details`"
              class="omnidb__workspace__connection-details"
            ></div>
            <div
              :id="`${connTabId}_tree`"
              style="overflow: auto; flex-grow: 1; transition: scroll 0.3s"
            ></div>
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
        class="omnidb__workspace__div-right"
        style="position: relative"
      >
        <div class="row">
          <button
            :id="`${connTabId}_tree_toggler`"
            type="button"
            class="py-4 px-0 btn btn-secondary omnidb__tree__toggler"
          >
            <i class="fas fa-arrows-alt-h"></i>
          </button>
          <div :id="`${connTabId}_tabs`" class="w-100"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "ConnectionTab",
  props: {
    connTabId: String,
  },
  data() {
    return {};
  },
  mounted() {},
};
</script>
