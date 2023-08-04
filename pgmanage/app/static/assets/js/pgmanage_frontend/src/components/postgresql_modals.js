import { createApp } from "vue";
import UtilityJobsJobDetail from './UtilityJobsJobDetail.vue'

const jobDetailModal = createApp({
  components: {
    "job-detail": UtilityJobsJobDetail
  },
});

jobDetailModal.mount("#utility-job-detail-wrap");