<template>
  <div class="omnidb__tab-status">
    <i :title="statusText" :class="['fas fa-dot-circle tab-status', statusClass]">
      <div v-if="tabStatus === 1 || tabStatus === 2" class="tab-status-indicator">
        <span :class="circleWavesClass">
          <span v-for="n in 4" :key="n"></span>
        </span>
      </div>
    </i>

    <span :title="statusText" class="ml-1">
      {{ statusText }}
    </span>
  </div>
</template>

<script>
import { tabStatusMap } from "../constants";

export default {
  name: "TabStatusIndicator",
  props: {
    tabStatus: {
      type: Number,
      validator: function (value) {
        return Object.values(tabStatusMap).includes(value);
      },
    },
  },
  computed: {
    statusText() {
      const statusMap = {
        0: "Not Connected",
        1: "Idle",
        2: "Running",
        3: "Idle in transaction",
        4: "Idle in transaction (aborted)",
      };
      return statusMap[this.tabStatus] || "";
    },
    statusClass() {
      const statusClassMap = {
        0: "tab-status-closed",
        1: "tab-status-idle position-relative",
        2: "tab-status-running position-relative",
        3: "tab-status-idle_in_transaction",
        4: "tab-status-idle_in_transaction_aborted",
      };

      return `${statusClassMap[this.tabStatus] || ""}`;
    },
    circleWavesClass() {
      return {
        "omnis__circle-waves":
          this.tabStatus === tabStatusMap.IDLE ||
          this.tabStatus === tabStatusMap.RUNNING,
        "omnis__circle-waves--idle": this.tabStatus === tabStatusMap.IDLE,
        "omnis__circle-waves--running": this.tabStatus === tabStatusMap.RUNNING,
      };
    },
  },
};
</script>

<style scoped>
.tab-status-indicator {
  position: absolute;
  width: 15px;
  height: 15px;
  overflow: visible;
  left: 0px;
  top: 0px;
  display: block;
}
</style>
