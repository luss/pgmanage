<template>
  <div class="card" >
    <div class="card-header">
    {{ settingGroup.category }}
    </div>
    <div class="card-body">
      <form role="form">
        <table class="table table-sm">
          <tr 
            v-for="(setting, index) in settingGroup.rows"
            :key="setting.name">
            <td class="badge-settings">
              <span class="title-setting">
              {{ setting.name }}
              </span>
              <p class="text-muted mb-0 small">
                {{ setting.desc }}</p>
            </td>
            <td class="input-setting">
              <InputItem
              :initial-setting="setting"
              :index="index"
              @setting-change="changeSetting"
              />
            </td>
          </tr>
        </table>
      </form>
    </div>
  </div>
</template>

<script>
import ConfigGroupItemInput from './ConfigGroupItemInput.vue';

export default {
  name: 'ConfigGroup',
  props: {
    initialGroup: {
      type: Object,
      required: true
    }
  },
  emits:['groupChange'],
  computed: {
    settingGroup() {
      return Object.assign({}, this.initialGroup)
    }
  },
  methods: {
    changeSetting(event) {
      this.settingGroup.rows[event.index] = event.changedSetting
      this.$emit('groupChange', {
        changedGroup: this.settingGroup,
        updatedSetting: {
          name: event.changedSetting.name,
          setting: event.changedSetting.setting
        }
      })
    }
  },
  components: {
    InputItem: ConfigGroupItemInput
  }
}
</script>

<style scoped>
.input-setting {
  width: 20%;
}

.table td{
  vertical-align: middle;
}
</style>
