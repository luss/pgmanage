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
              >
                <i :class="tab.icon"></i>
              </span>
              <span class="omnidb__tab-menu__link-name">
                {{ tab.name }}
              </span>
            </span>

            <i
              v-if="tab.close"
              class="fas fa-times tab-icon omnidb__tab-menu__link-close"
              @click.stop.prevent="tab.closeFunction"
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
      ></component>
    </div>
  </div>
</template>

<script>
import WelcomeScreen from "./WelcomeScreen.vue";
import ShortUniqueId from "short-unique-id";
import { showMenuNewTabOuter } from "../workspace.js";
export default {
  components: {
    WelcomeScreen,
  },
  props: {
    hierarchy: {
        type: String,
        validator(value) {
            return ["primary", "secondary"].includes(value)
        }
    }, 
  },
  data() {
    return {
      id: new ShortUniqueId({
        dictionary: "alphanum_lower",
      }).randomUUID(),
      tabs: [],
      selectedTab: "",
    };
  },
  methods: {
    createTab({
      clickFunction = null,
      close = true,
      closeFunction = null,
      dblClickFunction = null,
      disabled = false,
      icon = false,
      isDraggable = true,
      name = "",
      rightClickFunction = false,
      selectFunction = null,
      selectable = true,
      tooltip = false,
      component = null,
    }) {

        const tab = {
        id: new ShortUniqueId({
          dictionary: "alphanum_lower",
        }).randomUUID(), //change this
        icon: icon,
        disabled: disabled,
        isDraggable: isDraggable,
        name: name,
        selectFunction: selectFunction,
        clickFunction: clickFunction,
        dblClickFunction: dblClickFunction,
        closeFunction: closeFunction,
        rightClickFunction: rightClickFunction,
        close: close,
        component: component,
        tooltip: tooltip,
        selectable: selectable,
      }
      this.tabs.push(tab);

      return tab
    },
    selectTab(tab) {
      this.selectedTab = tab;

      if (tab.selectFunction != null) {
        tab.selectFunction();
      }
    },
    clickHandler(event, tab) {
      if (tab.selectable) {
        this.selectTab(tab);
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
  },
  mounted() {
    if (this.hierarchy == "primary") {
      this.createTab({
        icon: "fas fa-bolt",
        name: "Connections",
        close: false,
          selectable: false,
        tooltip: "Connections",
        clickFunction: function (e) {
          showMenuNewTabOuter(e);
        },
      });

      const welcomeTab = this.createTab({
        icon: "fas fa-hand-spock",
        name: "Welcome",
        selectFunction: function () {
          document.title = "Welcome to PgManage";
        },
        close: false,
        tooltip: "Welcome to PgManage",
        component: "WelcomeScreen",
      });
      this.selectTab(welcomeTab)
    }

    this.$nextTick(() => {
      $('[data-toggle="tab"]').tooltip({
        placement: "right",
        boundary: "window",
        html: true,
        delay: { show: 500, hide: 100 },
      });
    });
  },
};
</script>
