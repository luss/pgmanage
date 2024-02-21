<template>
  <div class="container-fluid px-0">
    <div class="row">
      <div class="col">
        <div class="omnidb__txt-console">
          <div ref="console" class="custom-console"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { Terminal } from "xterm";
import { settingsStore } from "../stores/stores_initializer";
import { FitAddon } from "xterm-addon-fit";
import { createRequest } from "../long_polling";
import { queryRequestCodes, requestState } from "../constants";
import { tabsStore } from "../stores/stores_initializer";
import { emitter } from "../emitter";

export default {
  name: "TerminalTab",
  props: {
    tabId: String,
    databaseIndex: Number,
  },
  data() {
    return {
      term: null,
      fitAddon: null,
      lastCommand: "",
      state: "",
      clearTerminal: true,
    };
  },
  mounted() {
    this.setupTerminal();
    this.setupEvents();
  },
  unmounted() {
    this.clearEvents();
  },
  methods: {
    setupTerminal() {
      this.term = new Terminal({
        fontSize: settingsStore.fontSize,
        fontFamily: "Monospace",
        theme: settingsStore.terminalTheme,
        rendererType: "dom", //FIXME: investigate in detail, for no use dom renderer because in nwjs we had some text rendering bugs on light theme
      });

      this.term.open(this.$refs.console);
      this.term.onData((data) => {
        this.terminalRun(false, data);
      });

      this.fitAddon = new FitAddon();
      this.term.loadAddon(this.fitAddon);
      this.fitAddon.fit();

      this.term.focus();
      this.term.write("Starting terminal...");

      this.terminalRun(
        true,
        `stty rows ${this.term.rows} cols ${this.term.cols} \n`
      );
    },
    setupEvents() {
      window.addEventListener("resize", this.resizeBrowserHandler);

      emitter.on(`${this.tabId}_resize`, () => {
        this.$nextTick(() => {
          this.resizeBrowserHandler();
        });
      });

      emitter.on(`${this.tabId}_adjust_terminal_dimensions`, () => {
        this.adjustTermninalDimensions();
        this.term.focus();
      });
    },
    clearEvents() {
      window.removeEventListener("resize", this.resizeBrowserHandler);
      emitter.all.delete(`${this.tabId}_resize`);
      emitter.all.delete(`${this.tabId}_adjust_terminal_dimensions`);
    },
    terminalRun(spawn = true, query = "\r") {
      this.lastCommand = query;
      let messageData = {
        v_cmd: query,
        v_tab_id: this.tabId,
        v_db_index: null,
        v_spawn: spawn,
        v_ssh_id: this.databaseIndex,
      };

      let context = {
        callback: this.handleResponse.bind(this),
      };

      createRequest(queryRequestCodes.Terminal, messageData, context);

      this.state = requestState.Executing;
    },
    handleResponse(data, context) {
      if (this.clearTerminal) {
        this.term.write("\x1b[H\x1b[2J");
        this.clearTerminal = false;
      }

      this.state = requestState.Idle;

      this.term.write(data.v_data.v_data);
    },
    resizeBrowserHandler() {
      if (this.tabId === tabsStore.selectedPrimaryTab.id) {
        this.fitAddon.fit();
      }
    },
    adjustTermninalDimensions() {
      this.terminalRun(
        false,
        `stty rows ${this.term.rows} cols ${this.term.cols} \n`
      );
    },
  },
};
</script>

<style scoped>
.custom-console {
  width: 100%;
  height: 100vh;
}
</style>
