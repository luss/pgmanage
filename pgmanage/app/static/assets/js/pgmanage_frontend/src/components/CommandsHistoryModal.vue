<template>
<div class="modal fade" :id="`modal_command_history_${tabId}`" tabindex="-1" role="dialog" aria-hidden="true"> 
  <div class="modal-dialog modal-xl" role="document">
    <div class="modal-content">

      <div class="modal-header align-items-center">
        <h2 class="modal-title font-weight-bold">
          Command history
        </h2>
        <button type="button" class="close" data-dismiss="modal" aria-label="Close">
          <span aria-hidden="true"><i class="fa-solid fa-xmark"></i></span>
        </button>
      </div>
      <div class="modal-body">
        <div :id="`command_history_div_${tabId}`" class="query_command_history">
          <div :id="`command_history_header_${tabId}`" class="query_command_history_header"></div>
          <div :id="`command_history_grid_${tabId}`" class="query_command_history_grid" style="width: 100%;height: calc(100vh - 16.5rem);overflow: hidden;"></div>
        </div>
      </div>
    </div>
  </div>
</div>

</template>

<script>
export default {
  name: 'CommandsHistoryModal',
  props: {
    tabId: String,
  },
}
</script>