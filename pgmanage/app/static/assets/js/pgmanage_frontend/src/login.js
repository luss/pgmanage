import { execAjax } from './ajax_control'

$(document).ready(function () {

  let txt_user = document.getElementById('txt_user')
  let txt_pwd = document.getElementById('txt_pwd')

  txt_user.onkeydown = function(event) {
    if (event.key === 'Enter') signIn();
  }
  txt_pwd.onkeydown = function(event) {
    if (event.key === 'Enter') signIn();
  }

  txt_user.onchange = (event) => { validateField(event.target)}

  txt_pwd.onchange = (event) => { validateField(event.target)}

  //FIXME: remove comment when notification_control.js will be moved to Vite bundle
  // checkSessionMessage();

  var v_user_name = document.getElementById('txt_user');
  var v_pwd = document.getElementById('txt_pwd');

  var validate_fields = [
    {el: v_user_name, val: v_user_name.value},
    {el: v_pwd, val: v_pwd.value}
  ];
  var field_errors = false;

  for (let i = 0; i < validate_fields.length; i++) {
    var v_field = validate_fields[i];
    if (v_field === null || v_field === '') {
      field_errors = true;
      validateField(v_field);
    }
  }

});

function signIn() {

  document.getElementById("txt_user").blur();
  document.getElementById("txt_pwd").blur();

  var v_user_name = document.getElementById('txt_user');
  var v_pwd = document.getElementById('txt_pwd');

  var validate_fields = [
    {el: v_user_name, val: v_user_name.value},
    {el: v_pwd, val: v_pwd.value}
  ];
  var field_errors = false;

  for (let i = 0; i < validate_fields.length; i++) {
    var v_field = validate_fields[i];
    if (v_field === null || v_field === '') {
      field_errors = true;
      validateField(v_field);
    }
  }

  if (!field_errors) {
    execAjax('/sign_in/',
      JSON.stringify({"p_username": v_user_name.value, "p_pwd": v_pwd.value}),
      function(p_return) {

        if (p_return.v_data>=0) {
          window.open(v_url_folder + "/workspace", '_self');
        }
        else if (p_return.v_data==-2) {
          showAlert('Invalid authentication token, use pgmanage-server to support multiple users.');
        }
        else
          showAlert('Invalid username or password.');

      },
      null,
      'box'
    );
  }

}

function validateField(p_field) {
  if (p_field) {
    var v_parent = p_field.parentElement;
    if (p_field.value !== null && p_field.value !== '') {
      v_parent.classList.remove('isEmpty');

    }
    else {
      v_parent.classList.add('isEmpty');
    }
  }
}

