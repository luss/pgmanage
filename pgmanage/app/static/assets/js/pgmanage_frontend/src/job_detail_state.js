import { reactive } from "vue";
const jobDetailState = reactive({
  visible: false,
  selectedJob: {},
  clearSelectedAndHide() {
    this.selectedJob = {};
    this.visible = false;
  },
  setJobAndShow(job) {
    this.selectedJob = job;
    this.visible = true;
  },
  setDuration(duration) {
    this.selectedJob.duration = duration;
  },
});

export { jobDetailState }