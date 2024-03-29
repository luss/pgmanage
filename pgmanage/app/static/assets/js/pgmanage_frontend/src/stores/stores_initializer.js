import { useSnippetsStore } from "./snippets";
import { useSettingsStore } from "./settings";
import { useTabsStore } from "./tabs";
import { useConnectionsStore } from "./connections";
import { useDbMetadataStore } from "./db_metadata";
import { createPinia, setActivePinia } from "pinia";

const pinia = createPinia();
setActivePinia(pinia);

const snippetsStore = useSnippetsStore();

const settingsStore = useSettingsStore();

const tabsStore = useTabsStore();

const connectionsStore = useConnectionsStore();

const dbMetadataStore = useDbMetadataStore();

export { snippetsStore, settingsStore, tabsStore, connectionsStore, dbMetadataStore };
