import 'vite/modulepreload-polyfill';
import './ace_themes/theme-omnidb.js';
import './ace_themes/theme-omnidb_dark.js';
import 'ace-builds/src-noconflict/mode-sql'
import 'ace-builds/src-noconflict/ext-language_tools'
import omniURL from './ace_themes/theme-omnidb.js?url'
import omniDarkURL from './ace_themes/theme-omnidb_dark.js?url'
import './workspace'
import './plugin_hook'
import './components/postgresql_modals'
import '@onekiloparsec/vue-power-tree/dist/style.css'
import 'vue-toast-notification/dist/theme-sugar.css';
import 'xterm/css/xterm.css'
import '@imengyu/vue3-context-menu/lib/vue3-context-menu.css'
import ace from 'ace-builds'

ace.config.setModuleUrl('ace/theme/omnidb', omniURL)
ace.config.setModuleUrl('ace/theme/omnidb_dark', omniDarkURL)

console.log('Hello from Vite')