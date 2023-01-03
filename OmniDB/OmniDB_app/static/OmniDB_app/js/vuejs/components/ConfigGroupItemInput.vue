<template>
    <div class="text-center" v-if="setting.vartype === 'bool'">
        <input type="checkbox"
                v-model="setting.setting"
                true-value="on"
                false-value="off"
                @change="changeSetting"
                :disabled="isReadOnly"
        />
    </div>
    <select v-else-if="setting.vartype === 'enum'" 
    class="form-control form-control-sm" 
    :name="setting.name" 
    v-model="setting.setting" 
    @input="changeSetting"
    :disabled="isReadOnly">
        <option v-for="v in setting.enumvals" :value="v">{{ v }}</option>
    </select>
    <input v-else data-html="true" type="text" 
    :name="setting.name"
    :placeholder="setting.name" 
    v-model="setting.setting" 
    @input="changeSetting" 
    :id="inputId"
    :disabled="isReadOnly"
    >
    <button v-if="setting.setting != setting.boot_val && setting.category != 'Preset Options'" 
    type="button" 
    class="btn btn-link btn-sm" 
    :id="buttonId"  
    :title="`Reset to: ${setting.boot_val}`"
    @click.prevent="setDefault">
        <span class="fa fa-undo" aria-hidden="true"></span>
        Reset to default
    </button>
</template>

<script>
export default {
    props:{
        initialSetting: {
            type: Object,
            required: true
        },
        index: {
            type: Number,
            required: true
        }
    },
    emits: ['settingChange']
    ,
    data() {
        return {
            tooltipTitle: `<table>
                    <tr>
                        <td>Type:</td>
                        <td><b>${ this.initialSetting.vartype }</b></td>
                    </tr>
                    <tr>
                        <td>Unit:</td>
                        <td><b>${ this.initialSetting.unit }</b></td>
                    </tr>
                    <tr>
                        <td>Minimum:</td>
                        <td><b>${this.initialSetting.min_val}</b></td>
                    </tr>
                    <tr>
                        <td>Maximum:</td>
                        <td><b>${this.initialSetting.max_val}
                        </b>
                        </td>
                    </tr>
                    </table>`,
            inputId: `${this.initialSetting.name}_input`,
            buttonId: `buttonResetDefault_${this.initialSetting.name}`,
        }
    },
    computed: {
        setting() {
            return Object.assign({}, this.initialSetting)
        },
        isReadOnly() {
            return this.initialSetting.category === 'Preset Options'
        }
    },
    methods: {
        changeSetting(e) {
            $(`#${this.buttonId}`).tooltip('dispose')
            $(`#${this.buttonId}`).tooltip({
            sanitize: false,
            boundary: 'window',
            html: true,
            delay: { "show": 500, "hide": 100}
        })
            this.$emit('settingChange', {
                changedSetting: this.setting,
                index: this.index
            })
        },
        setDefault() {
            this.setting.setting = this.setting.boot_val
            this.changeSetting()
        }
    },
    mounted() {
        this.$nextTick(() => {
        $(`#${this.inputId}`).tooltip({
            sanitize: false, 
            title: this.tooltipTitle, 
            boundary: 'window', 
            html: true, 
            delay: { "show": 500, "hide": 100 } })
        });
        $(`#${this.buttonId}`).tooltip({
            sanitize: false,
            boundary: 'window',
            html: true,
            delay: { "show": 500, "hide": 100}
        })
    }
}
</script>