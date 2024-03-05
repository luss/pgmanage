import { useSnippetsStore } from "./snippets";
import { useSettingsStore } from "./settings";
import { useTabsStore } from "./tabs";
import { useConnectionsStore } from "./connections";
import { createPinia, setActivePinia } from "pinia";

const pinia = createPinia();
setActivePinia(pinia);

const snippetsStore = useSnippetsStore();

const settingsStore = useSettingsStore();

const tabsStore = useTabsStore();

const connectionsStore = useConnectionsStore();

export { snippetsStore, settingsStore, tabsStore, connectionsStore };
