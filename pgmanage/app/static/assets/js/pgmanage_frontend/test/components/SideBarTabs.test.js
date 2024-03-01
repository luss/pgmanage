import {
  describe,
  test,
  vi,
  expect,
  beforeEach,
  afterEach,
  beforeAll,
} from "vitest";
import { mount, enableAutoUnmount } from "@vue/test-utils";
import SideBarTabs from "../../src/components/SideBarTabs.vue";
import "bootstrap";
import { nextTick } from "vue";
import { emitter } from "../../src/emitter";
import { useTabsStore } from "../../src/stores/tabs";
import { useConnectionsStore } from "../../src/stores/connections";

vi.mock("@/workspace.js", () => {
  const showMenuNewTabOuter = vi.fn();

  return { showMenuNewTabOuter };
});

vi.mock("@/header_actions.js", () => {
  const showConfigUser = vi.fn;
  return { showConfigUser };
});

vi.mock("xterm", () => {
  const Terminal = vi.fn();
  return { Terminal };
});

const connectionMock = {
  id: 1,
  alias: "TestConnection",
  technology: "postgresql",
};
vi.stubGlobal("v_url_folder", "test_folder");

describe("SideBarTabs.vue", () => {
  enableAutoUnmount(afterEach);
  let tabsStore, connectionsStore;

  beforeAll(() => {
    connectionsStore = useConnectionsStore();
    connectionsStore.$patch({ connections: [connectionMock] });
  });

  beforeEach(() => {
    tabsStore = useTabsStore();
  });

  afterEach(() => {
    tabsStore.$reset();
  });
  test("renders a component", async () => {
    let wrapper = mount(SideBarTabs, {
      shallow: true,
    });

    expect(wrapper.html()).toContain("omnidb__tab-menu--container--primary");
    await nextTick();

    expect(wrapper.html()).toContain("Snippets");
    expect(wrapper.html()).toContain("Connections");
    expect(wrapper.html()).toContain("Welcome");
  });
  describe("Events", () => {
    test("setup events on mount", () => {
      const emitterSpy = vi.spyOn(emitter, "on");

      const wrapper = mount(SideBarTabs, {
        shallow: true,
      });

      expect(emitterSpy).toHaveBeenCalledTimes(2);
      expect(emitterSpy.mock.calls[0]).toContain(
        `${tabsStore.id}_create_conn_tab`
      );
    });
    test("call createConnectionPanel on create_conn_tab event", async () => {
      const wrapper = mount(SideBarTabs, {
        shallow: true,
      });
      const createConnectionPanelSpy = vi.spyOn(
        wrapper.vm,
        "createConnectionPanel"
      );

      emitter.emit(`${tabsStore.id}_create_conn_tab`, { index: 1 });

      await nextTick();

      expect(createConnectionPanelSpy).toHaveBeenCalledOnce();
      expect(wrapper.html()).toContain("TestConnection");
    });
    test("call createTerminalTab on create_terminal_tab event", async () => {
      const wrapper = mount(SideBarTabs, {
        shallow: true,
      });

      const createTerminalTabSpy = vi.spyOn(wrapper.vm, "createTerminalTab");

      emitter.emit(`${tabsStore.id}_create_terminal_tab`, {
        index: 1,
        alias: "TestTerminal",
      });

      await nextTick();
      expect(createTerminalTabSpy).toHaveBeenCalledOnce();
      expect(wrapper.html()).toContain("TestTerminal");
    });
  });
});
