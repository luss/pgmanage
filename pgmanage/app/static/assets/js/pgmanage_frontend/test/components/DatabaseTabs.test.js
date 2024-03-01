import { describe, vi, test, beforeEach, afterEach, expect } from "vitest";
import { mount, enableAutoUnmount } from "@vue/test-utils";
import DatabaseTabs from "@/components/DatabaseTabs.vue";
import { useTabsStore } from "../../src/stores/tabs";
import { nextTick } from "vue";
import { emitter } from "../../src/emitter";

vi.mock("@/workspace.js", () => {
  const renameTab = vi.fn();

  return { renameTab };
});

describe("DatabaseTabs.vue", () => {
  let tabsStore, connTab, snippetTab;
  enableAutoUnmount(afterEach);

  beforeEach(() => {
    tabsStore = useTabsStore();
    snippetTab = tabsStore.addTab({ name: "Snippets" });
    connTab = tabsStore.addTab({ name: "TestConnection" });
    tabsStore.selectTab(connTab);
    connTab.metaData.selectedDBMS = "postgresql";
  });

  afterEach(() => {
    tabsStore.$reset();
  });

  test("renders a component", async () => {
    const wrapper = mount(DatabaseTabs, {
      props: {
        tabId: connTab.id,
      },
      shallow: true,
    });

    await nextTick();

    expect(wrapper.html()).toContain("omnidb__tab-content--secondary");
  });

  test("calls setupEvents method on mounted", () => {
    const setupEventsSpy = vi.spyOn(DatabaseTabs.methods, "setupEvents");
    const wrapper = mount(DatabaseTabs, {
      props: {
        tabId: connTab.id,
      },
      shallow: true,
    });

    expect(setupEventsSpy).toHaveBeenCalledOnce();
  });
  test("calls clearEvents method on unmounted", () => {
    const wrapper = mount(DatabaseTabs, {
      props: {
        tabId: connTab.id,
      },
      shallow: true,
    });

    const clearEventsSpy = vi.spyOn(wrapper.vm, "clearEvents");

    wrapper.unmount();

    expect(clearEventsSpy).toHaveBeenCalledOnce();
  });
  test("calls addTab method on add button click", async () => {
    const wrapper = mount(DatabaseTabs, {
      props: {
        tabId: connTab.id,
      },
      shallow: true,
    });

    const addTabSpy = vi.spyOn(wrapper.vm, "addTab");

    await wrapper.find('[data-testid="add-tab-button"]').trigger("click");

    expect(addTabSpy).toHaveBeenCalledOnce();
  });
  test("addTab method adds snippet tab when sideBarTab is 'Snippets", async () => {
    const wrapper = mount(DatabaseTabs, {
      props: {
        tabId: snippetTab.id,
      },
      shallow: true,
    });

    const addTabSpy = vi.spyOn(wrapper.vm, "addTab");
    const createSnippetTabSpy = vi.spyOn(wrapper.vm, "createSnippetTab");

    await wrapper.find('[data-testid="add-tab-button"]').trigger("click");

    expect(addTabSpy).toHaveBeenCalledOnce();
    expect(createSnippetTabSpy).toHaveBeenCalledOnce();
  });
  test("addTab method calls showMenuNewTab method when sideBarTab is not 'Snippets", async () => {
    const wrapper = mount(DatabaseTabs, {
      props: {
        tabId: connTab.id,
      },
      shallow: true,
    });

    const addTabSpy = vi.spyOn(wrapper.vm, "addTab");
    const showMenuNewTabSpy = vi.spyOn(wrapper.vm, "showMenuNewTab");

    await wrapper.find('[data-testid="add-tab-button"]').trigger("click");

    expect(addTabSpy).toHaveBeenCalledOnce();
    expect(showMenuNewTabSpy).toHaveBeenCalledOnce();
  });
  test("call createSnippetTab method on emit event when sideBarTab is 'Snippets'", async () => {
    const wrapper = mount(DatabaseTabs, {
      props: {
        tabId: snippetTab.id,
      },
      shallow: true,
    });

    const createSnippetTabSpy = vi.spyOn(wrapper.vm, "createSnippetTab");

    emitter.emit("create_snippet_tab");

    expect(createSnippetTabSpy).toHaveBeenCalledOnce();
  });
});
