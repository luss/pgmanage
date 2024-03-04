<template>
  <SettingsModal />
  <SideBarTabs />
</template>

<script>
import SettingsModal from "./components/SettingsModal.vue";
import SideBarTabs from "./components/SideBarTabs.vue";
export default {
  name: "PgManage",
  components: {
    SettingsModal,
    SideBarTabs,
  },
};
</script>
