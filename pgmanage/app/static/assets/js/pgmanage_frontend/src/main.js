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
import 'vue-toast-notification/dist/theme-sugar.css';
import 'xterm/css/xterm.css'
import '@imengyu/vue3-context-menu/lib/vue3-context-menu.css'
import '../../../scss/components/modal.scss'
import ace from 'ace-builds'
import 'ace-builds/esm-resolver'
import axios from 'axios'
import { getCookie } from './ajax_control.js';
import { showAlert } from './notification_control.js';
import moment from 'moment';

ace.config.setModuleUrl('ace/theme/omnidb', omniURL)
ace.config.setModuleUrl('ace/theme/omnidb_dark', omniDarkURL)

axios.defaults.headers.common['X-CSRFToken'] = getCookie(v_csrf_cookie_name);
axios.interceptors.response.use(response => {
  return response;
}, error => {
  if (error.response.status === 401) {
    showAlert('User not authenticated, please reload the page.');
  }
  return Promise.reject(error);
});

moment.defaultFormat = date_format;

console.log('Hello from Vite')