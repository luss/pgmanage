import { createApp } from 'vue'
import SettingsModal from './components/SettingsModal.vue'

const settingsModal = createApp({
	components: {
		'settings-modal': SettingsModal
	}
})

function settingsModalInit() {
	settingsModal.mount('#settings-modal-wrap')
}

export { settingsModalInit }