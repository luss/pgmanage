/*
This file is part of OmniDB.
OmniDB is open-source software, distributed "AS IS" under the MIT license in the hope that it will be useful.

The MIT License (MIT)

Portions Copyright (c) 2015-2020, The OmniDB Team
Portions Copyright (c) 2017-2020, 2ndQuadrant Limited

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
*/

import { createApp } from "vue";
import TreeSqlite from "../components/TreeSqlite.vue";
import { tabSQLTemplate } from "./tree_postgresql";
import { toggleConnectionAutocomplete } from "../workspace";
import { querySQL } from "../query";

/// <summary>
/// Retrieving tree.
/// </summary>
function getTreeSqlite(div) {
    const div_tree = document.getElementById(div);
    div_tree.innerHTML ='<tree-sqlite :database-index="databaseIndex" :tab-id="tabId"></tree-sqlite>'
    const app = createApp({
      components: {
        "tree-sqlite": TreeSqlite
      },
        data() {
            return {
              databaseIndex: window.v_connTabControl.selectedTab.tag.selectedDatabaseIndex,
              tabId: window.v_connTabControl.selectedTab.id,
            };
          },
    })
    app.mount(`#${div}`)

    // save tree referece in the tab, it will be later used to destroy tree instance on tab close
    v_connTabControl.selectedTab.tree = app

    let autocomplete_switch_status = (v_connTabControl.selectedTab.tag.enable_autocomplete !== false) ? ' checked ' : '';
    let autocomplete_btn_id = `autocomplete_toggler_${v_connTabControl.selectedTab.tag.tab_id}`
    v_connTabControl.selectedTab.tag.divDetails.innerHTML =
        `<i class="fas fa-server mr-1"></i>selected DB: 
        <b>${truncateText(v_connTabControl.selectedTab.tag.selectedDatabase, 10)}</b>
        <div class="omnidb__switch omnidb__switch--sm float-right" data-toggle="tooltip" data-placement="bottom" data-html="true" title="" data-original-title="<h5>Toggle autocomplete.</h5><div>Switch OFF <b>disables the autocomplete</b> on the inner tabs for this connection.</div>">
    	    <input type="checkbox" ${autocomplete_switch_status} id="${autocomplete_btn_id}" class="omnidb__switch--input">
    	    <label for="${autocomplete_btn_id}" class="omnidb__switch--label">
                <span>
                    <i class="fas fa-spell-check"></i>
                </span>
            </label>
		</div>`;

    let autocomplete_btn = document.getElementById(`${autocomplete_btn_id}`)
    autocomplete_btn.onchange = function() { toggleConnectionAutocomplete(autocomplete_btn_id) }
    
    // tree.beforeContextMenuEvent = function(node, callback) {
    //     var v_elements = [];

    //     //Hooks
    //     if (v_connTabControl.tag.hooks.sqliteTreeContextMenu.length > 0) {
    //         for (var i = 0; i < v_connTabControl.tag.hooks.sqliteTreeContextMenu.length; i++) {
    //             v_elements = v_elements.concat(v_connTabControl.tag.hooks.sqliteTreeContextMenu[i](node));
    //         }
    //     }

    //     callback(v_elements);
    // }
}

function afterNodeOpenedCallbackSqlite(node) {
    //Hooks
    if (v_connTabControl.tag.hooks.sqliteTreeNodeOpen.length > 0) {
        for (var i = 0; i < v_connTabControl.tag.hooks.sqliteTreeNodeOpen.length; i++) {
            v_connTabControl.tag.hooks.sqliteTreeNodeOpen[i](node);
        }
    }
}

/// <summary>
/// Retrieving SELECT SQL template.
/// </summary>
function TemplateSelectSqlite(p_table, p_kind) {
    execAjax(
        '/template_select_sqlite/',
        JSON.stringify({
            'p_database_index': v_connTabControl.selectedTab.tag.selectedDatabaseIndex,
            'p_tab_id': v_connTabControl.selectedTab.id,
            'p_table': p_table,
            'p_kind': p_kind
        }),
        function(p_return) {
            let v_tab_name = p_table;
            v_connTabControl.tag.createQueryTab(v_tab_name);

            var v_tab_tag = v_connTabControl.selectedTab.tag.tabControl.selectedTab.tag;
            v_tab_tag.editor.setValue(p_return.v_data.v_template);
            v_tab_tag.editor.clearSelection();

            querySQL(0);
        },
        function(p_return) {
            showError(p_return.v_data);
            return '';
        },
        'box',
        true
    );
}

/// <summary>
/// Retrieving INSERT SQL template.
/// </summary>
function TemplateInsertSqlite(p_table) {
    execAjax(
        '/template_insert_sqlite/',
        JSON.stringify({
            'p_database_index': v_connTabControl.selectedTab.tag.selectedDatabaseIndex,
            'p_tab_id': v_connTabControl.selectedTab.id,
            'p_table': p_table
        }),
        function(p_return) {
          tabSQLTemplate(
              'Insert ' + p_table,
              p_return.v_data.v_template
          );
        },
        function(p_return) {
            showError(p_return.v_data);
            return '';
        },
        'box',
        true
    );
}

/// <summary>
/// Retrieving UPDATE SQL template.
/// </summary>
function TemplateUpdateSqlite(p_table) {
    execAjax(
        '/template_update_sqlite/',
        JSON.stringify({
            'p_database_index': v_connTabControl.selectedTab.tag.selectedDatabaseIndex,
            'p_tab_id': v_connTabControl.selectedTab.id,
            'p_table': p_table
        }),
        function(p_return) {
          tabSQLTemplate(
              'Update ' + p_table,
              p_return.v_data.v_template
          );
        },
        function(p_return) {
            showError(p_return.v_data);
            return '';
        },
        'box',
        true
    );
}

function truncateText(text, maxLength) {
    if (text.length <= maxLength) {
      return text;
    } else if (text.indexOf('/') !== -1) {
      const ellipsis = '...';
      const parts = text.split('/');
      const firstPart = parts[0];
      const lastPart = parts[parts.length - 1];
      const middleParts = parts.slice(1, parts.length - 1);
      let truncatedText = firstPart + '/';
      for (let i = 0; i < middleParts.length; i++) {
        if (truncatedText.length + middleParts[i].length + ellipsis.length > maxLength) {
          truncatedText += ellipsis;
          break;
        }
        truncatedText += middleParts[i] + '/';
      }
      truncatedText += '/' + lastPart;
      return truncatedText;
    } else {
      const ellipsis = '...';
      const truncatedText = text.slice(0, maxLength - ellipsis.length) + ellipsis;
      return truncatedText;
    }
  }

export {
  getTreeSqlite,
  TemplateSelectSqlite,
  TemplateInsertSqlite,
  TemplateUpdateSqlite,
};