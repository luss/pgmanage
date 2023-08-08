import { deleteRowEditData } from "./tree_context_functions/edit_data";

function editDataActionRenderer(instance, td, row, col, prop, value, cellProperties) {
  const deleteIcon = document.createElement('i');
  deleteIcon.className = 'fas fa-times action-grid action-close text-danger';
  deleteIcon.title = 'Remove';

  deleteIcon.addEventListener('click', () => {
      deleteRowEditData(); 
  });

  const div = document.createElement('div');
  div.className = 'text-center';
  div.appendChild(deleteIcon);

  Handsontable.renderers.HtmlRenderer.apply(this, arguments);

  td.className = 'cellReadOnly';
  td.appendChild(div);

}

export { editDataActionRenderer }