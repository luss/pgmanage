<template>
  <div class="text-center" v-if="setting.vartype === 'bool'">
    <input class="config-checkbox" type="checkbox" v-model="setting.setting" true-value="on" false-value="off"
      @change="changeSetting" :disabled="isReadOnly" />
  </div>
  <select v-else-if="setting.vartype === 'enum'" class="form-control form-control-sm" :name="setting.name"
    v-model="setting.setting" @input="changeSetting" :disabled="isReadOnly">
    <option v-for="v in setting.enumvals" :value="v">{{ v }}</option>
  </select>
  <input v-else data-html="true" type="text" :name="setting.name" :placeholder="setting.name" v-model="setting.setting"
    @input="changeSetting" :id="inputId" :disabled="isReadOnly" />
  <button v-if="
    setting.setting != setting.boot_val &&
    setting.category != 'Preset Options'
  " type="button" class="btn btn-link btn-sm" :id="buttonId" :title="`Reset to: ${setting.boot_val}`"
    @click.prevent="setDefault">
    <span class="fa fa-undo" aria-hidden="true"></span>
    Reset to default
  </button>
</template>

<script>
export default {
  props: {
    initialSetting: {
      type: Object,
      required: true,
    },
    index: {
      type: Number,
      required: true,
    },
  },
  emits: ["settingChange"],
  data() {
    return {
      tooltipTitle: `<table>
              <tr>
                <td>Type:</td>
                <td><b>${this.initialSetting.vartype}</b></td>
              </tr>
              <tr>
                <td>Unit:</td>
                <td><b>${this.initialSetting.unit}</b></td>
              </tr>
              <tr>
                <td>Minimum:</td>
                <td><b>${this.initialSetting.min_val}</b></td>
              </tr>
              <tr>
                <td>Maximum:</td>
                <td><b>${this.initialSetting.max_val}</b></td>
              </tr>
              </table>`,
      inputId: `${this.initialSetting.name}_input`,
      buttonId: `buttonResetDefault_${this.initialSetting.name}`,
    };
  },
  computed: {
    setting() {
      return Object.assign({}, this.initialSetting);
    },
    isReadOnly() {
      return this.initialSetting.category === "Preset Options";
    },
  },
  mounted() {
    this.$nextTick(() => {
      $(`#${this.inputId}`).tooltip({
        sanitize: false,
        title: this.tooltipTitle,
        boundary: "window",
        html: true,
        delay: { show: 500, hide: 100 },
      });
      $(`#${this.buttonId}`).tooltip({
        sanitize: false,
        boundary: "window",
        html: true,
        delay: { show: 500, hide: 100 },
      });
    });
  },
  methods: {
    changeSetting(e) {
      $(`#${this.buttonId}`).tooltip("dispose");
      $(`#${this.buttonId}`).tooltip({
        sanitize: false,
        boundary: "window",
        html: true,
        delay: { show: 500, hide: 100 },
      });
      this.$emit("settingChange", {
        changedSetting: this.setting,
        index: this.index,
      });
    },
    setDefault() {
      this.setting.setting = this.setting.boot_val;
      this.changeSetting();
    },
  },
};
</script>

<style scoped>
.config-checkbox[type="checkbox"] {
  width: 30px;
  height: 30px;
}

.config-checkbox[type="checkbox"]:before {
  position: relative;
  display: block;
  width: 30px;
  height: 30px;
  content: "";
  background: #fff;
}

.config-checkbox[type="checkbox"]:after {
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
  top: -30px;
  width: 30px;
  height: 30px;
  content: "Off";
  background: #dc3545;
  color: #fff;
}

.config-checkbox[type="checkbox"]:checked:after {
  background: #28a745;
  content: "On";
}

.config-checkbox[type="checkbox"]:disabled:after {
  -webkit-filter: opacity(0.4);
}
</style>