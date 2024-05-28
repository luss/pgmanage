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

import { listUsers } from './users'
import { showConfirm } from './notification_control';
import { settingsStore } from './stores/stores_initializer';
import { Modal } from 'bootstrap';

/*
var v_light_terminal_theme = {
	background: '#f4f4f4',
	brightBlue: '#006de2',
	brightGreen: '#4b9800',
	foreground: '#353535',
	cursor: '#353535',
	cursorAccent: '#353535',
	selection: '#00000030'
}
*/

/// <summary>
/// Startup function.
/// </summary>
$(function() {

	let link_user = document.getElementById('omnidb__utilities-menu__link-user')
	if (link_user) {
		link_user.onclick = function() { listUsers() }
	}

	let link_config = document.getElementById('omnidb__utilities-menu__link-config')
	link_config.onclick = function() { showConfigUser() }

	let link_signout = document.getElementById('omnidb__utilities-menu__link-signout')
	if (link_signout) {
		link_signout.onclick = function() { confirmSignout() }
	}

	let link_toggle = document.getElementById('omnidb__utilities-menu__link-toggle')
	link_toggle.onclick = function() { toggleUtilitiesMenu() }


	// var v_fileref = document.getElementById("ss_theme");
  // v_fileref.setAttribute("href", v_url_folder + '/static/OmniDB_app/new/css/themes/' + v_theme + '.css');


	//var v_configTabControl = createTabControl('config_tabs',0,null);
	//v_configTabControl.selectTabIndex(0);

});


/// <summary>
/// Opens user config window.
/// </summary>
function showConfigUser() {
	Modal.getOrCreateInstance('#modal_settings', {
		backdrop: 'static', keyboard: false
	}).show()
	$('#txt_new_pwd').passtrength({passwordToggle: false});
}

/// <summary>
/// Go to connections.
/// </summary>
function goToConnections() {

	showConfirm('You will lose existing changes. Would you like to continue?',
		function() {

			window.open("../connections","_self");

		});

}

/// <summary>
/// Go to connections.
/// </summary>
function confirmSignout() {

	showConfirm('Are you sure you want to sign out?',
		function() {

			window.open("../logout","_self");

		});

}

function saveEditContent() {
	Modal.getInstance(document.getElementById("div_edit_content")).hide();

	if (v_canEditContent) {
		v_editContentObject.ht.setDataAtCell(v_editContentObject.row, v_editContentObject.col, v_editContentObject.editor.getValue());
	}
	else {
		alert('No permissions.');
	}

	v_editContentObject.editor.setValue('');
}

function cancelEditContent() {
	Modal.getInstance(document.getElementById("div_edit_content")).hide();
	v_editContentObject.editor.setValue('');
}

/// <summary>
/// Hides edit cell window.
/// </summary>
function hideEditContent() {

	Modal.getInstance(document.getElementById("div_edit_content")).hide();

	if (v_canEditContent)
		v_editContentObject.ht.setDataAtCell(v_editContentObject.row, v_editContentObject.col, v_editContentObject.editor.getValue());

	v_editContentObject.editor.setValue('');

}

function toggleUtilitiesMenu() {
	let target_element = $('div.omnidb__utilities-menu.omnidb__theme-bg--menu-utilities.omnidb__rounded--lg')
	target_element.toggleClass('omnidb__utilities-menu--show')
	$(document).mouseup(function (e) {
		let toggle_button = $('#omnidb__utilities-menu__link-toggle')
		if (!toggle_button.is(e.target) && toggle_button.has(e.target).length === 0) {
				if ($('div.omnidb__utilities-menu.omnidb__theme-bg--menu-utilities.omnidb__rounded--lg').hasClass('omnidb__utilities-menu--show')) {
					$ ('div.omnidb__utilities-menu.omnidb__theme-bg--menu-utilities.omnidb__rounded--lg') .removeClass('omnidb__utilities-menu--show');
				}
		}
	});
}

export { showConfigUser };