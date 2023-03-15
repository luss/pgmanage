<template>
  <h2 class="font-weight-bold text-center mt-2 mb-3">Jobs</h2>
  <div class="card">
    <div class="card-body p-0">
      <ul class="list-group list-group-flush form-group rounded-0">
        <li class="list-group-item d-flex row no-gutters font-weight-bold">
          <div class="col-1">PID</div>
          <div class="col-2">Type</div>
          <div class="col-2">Server</div>
          <div class="col-2">Object</div>
          <div class="col-2">Start Time</div>
          <div class="col-1">Status</div>
          <div class="col-1">Duration</div>
          <div class="col-1">Actions</div>
        </li>

        <li v-for="job in jobList" :key="job.id" class="list-group-item d-flex row no-gutters" role="button">
          <div class="col-1">{{ job.utility_pid }}</div>
          <div class="col-2">{{ job.details.type }}</div>
          <div class="col-2">{{ job.details.server }}</div>
          <div class="col-2">{{ job.details.object }}</div>
          <div class="col-2">{{ job.start_time }}</div>
          <div class="col-1"> 
            <i :class="['fa-solid', {
              'fa-hourglass text-info' : jobStatus(job.process_state) === 'Running',
              'fa-ban text-warning' : jobStatus(job.process_state) === 'Terminated' || jobStatus(job.process_state) === 'Terminating',
              'fa-circle-check text-success' : jobStatus(job.process_state) === 'Finished',
              'fa-circle-exclamation text-danger' : jobStatus(job.process_state) === 'Failed'
            }]"
              data-toggle="tooltip" data-placement="bottom" :title="jobStatus(job.process_state)"
            ></i>
          </div>
          <div class="col-1">{{ job.duration }}</div>
          <div class="col-1 d-flex justify-content-between align-items-start muted-text">
              <a class="btn btn-ghost btn-ghost-secondary" @click="getJobDetails(job.id)" title="View details">
                <i class="fa-solid fa-scroll fa-lg"></i>
              </a>
              <a :class="['btn btn-ghost btn-ghost-secondary', {'disabled': job.canStop }]" @click="stopJob(job.id)" title="Stop job">
                <i class="fa-solid fa-stop fa-lg"></i>
              </a>
              <a class="btn btn-ghost btn-ghost-secondary" @click="deleteJob(job.id)">
                <i class="fas fa-times fa-lg" title="Delete job"></i>
              </a>
          </div>
        </li>
      </ul>
    </div>
  </div>

  <!-- Modal -->
  <div class="modal fade" :id="detailModalId" tabindex="-1" role="dialog" aria-hidden="true">
    <div class="modal-dialog" role="document">
      <div class="modal-content">
        <div class="modal-header align-items-center">
          <h3 class="modal-title">{{ selectedJob?.type_desc }}</h3>
          <button type="button" class="close" data-dismiss="modal" aria-label="Close">
              <span aria-hidden="true"><i class="fa-solid fa-xmark"></i></span>
            </button>
        </div>
        <div class="modal-body">
          <p class="mb">{{ selectedJob?.description }}</p>
          <p class="font-weight-bold mb-2">Command:</p>
          <p class="p-2 border border-radius text-break">{{ selectedJob?.details?.cmd }}</p>
          <div class="d-flex justify-content-between mt-3 mb-2">
            <span>
              <span class="font-weight-bold">Start time:</span> {{ selectedJob?.start_time }}
            </span>
            <span>
              <span class="font-weight-bold">Duration:</span> {{ selectedJob?.duration }}
            </span>
          </div>
          <p class="font-weight-bold mb-2">Output:</p>
          <div :style="{ height: '200px', overflowY: 'auto' }" class="border border-radius p-1">
            <p v-for="log in logs"> {{ log }}</p>
          </div>
        </div>
        <div :class="['modal-footer', { 'd-none': selectedJob.canStop }]">
          <a class="btn btn-danger" @click="stopJob(selectedJob.id)">
            Stop process
          </a>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
const JobState = {
  PROCESS_NOT_STARTED: 0,
  PROCESS_STARTED: 1,
  PROCESS_FINISHED: 2,
  PROCESS_TERMINATED: 3,
  /* Supported by front end only */
  PROCESS_TERMINATING: 10,
  PROCESS_FAILED: 11,
};

export default {
  data() {
    return {
      pendingJobId: [],
      jobList: [],
      workerId: '',
      detailedJobWorker: '',
      logs: [],
      selectedJob: {},
      detailModalId: `${window.v_connTabControl.selectedTab.tag.tabControl.selectedTab.id}_modal_job_detail`
    }
  },
  mounted() {
    this.startWorker()
    $(`#${this.detailModalId}`).on('hidden.bs.modal', () => {
      this.logs.splice(0)
      clearInterval(this.detailedJobWorker)
    })
  },
  methods: {
    getJobList() {
      axios.get('/bgprocess')
        .then((resp) => {
          console.log(resp)
          this.jobList = resp.data.data.map((j) => {
            let processState = this.evaluateProcessState(j);
            return {
              ...j,
              start_time: moment(j.start_time).format("DD/MM/YY hh:mm A"),
              process_state: processState,
              canStop: ![JobState.PROCESS_NOT_STARTED, JobState.PROCESS_STARTED].includes(processState),
            }
          })
          this.checkPending();
        })
        .catch((error) => {
          console.log(error)
        })
    },
    startWorker() {
      this.getJobList()
      this.pendingJobId = this.jobList.filter((p) => (p.process_state === JobState.PROCESS_STARTED)).map((p) => p.id)
      this.workerId = setInterval(() => {
        if (this.pendingJobId.length > 0) {
          this.getJobList();
        }
      }, 1000)
    },
    startJob(job_id) {
      this.pendingJobId.push(job_id)
    },
    stopJob(job_id) {
      this.jobList.find((p) => p.id == job_id).process_state = JobState.PROCESS_TERMINATING;
      axios.post(`/bgprocess/stop/${job_id}/`)
        .then((resp) => {
          this.jobList.find((p) => p.id == job_id).process_state = JobState.PROCESS_TERMINATED;
        })
        .catch((error) => {
          console.log(error)
        })
    },
    deleteJob(job_id) {
      axios.post(`/bgprocess/delete/${job_id}/`)
        .then((resp) => {
          this.getJobList()
        })
        .catch((error) => {
          console.log(error)
        })
    },
    getJobDetails(job_id, out = 0, err = 0) {
      axios.get(`/bgprocess/${job_id}/${out}/${err}`)
        .then((resp) => {
          console.log(resp)
          this.selectedJob = Object.assign({}, this.jobList.find((j) => j.id == job_id))
          let out_pos = resp.data.data.out.pos
          let err_pos = resp.data.data.err.pos
          this.selectedJob.duration = resp.data.data.duration
          this.logs.push(
            ...resp.data.data.err.lines.map((l) => l[1]),
            ...resp.data.data.out.lines.map((l) => l[1]))
          $(`#${this.detailModalId}`).modal('show')
          if (!this.detailedJobWorker) {
            this.detailedJobWorker = setInterval(() => {
              this.getJobDetails(job_id, out_pos, err_pos)
            }, 1000)

          }
          if (resp.data.data.out.done && resp.data.data.err.done && resp.data.data.exit_code != null && this.detailedJobWorker) {
            clearInterval(this.detailedJobWorker)
          }
        })
        .catch((error) => {
          console.log(error)
        })
    },
    jobStatus(process_state) {
      if (process_state === JobState.PROCESS_STARTED) {
        return 'Running'
      } else if (process_state === JobState.PROCESS_FINISHED) {
        return 'Finished'
      } else if (process_state === JobState.PROCESS_TERMINATED) {
        return 'Terminated'
      } else if (process_state === JobState.PROCESS_TERMINATING) {
        return 'Terminating'
      } else if (process_state === JobState.PROCESS_FAILED) {
        return 'Failed'
      }
      return ''
    },
    evaluateProcessState(p) {
      let retState = p.process_state;
      if ((p.end_time || p.exit_code != null) && p.process_state == JobState.PROCESS_STARTED) {
        retState = JobState.PROCESS_FINISHED;
      }
      if (retState == JobState.PROCESS_FINISHED && p.exit_code != 0) {
        retState = JobState.PROCESS_FAILED;
      }
      return retState;
    },
    checkPending() {
      const completedJobIds = this.jobList.filter((j) => {
        if (![
          JobState.PROCESS_NOT_STARTED,
          JobState.PROCESS_STARTED,
          JobState.PROCESS_TERMINATING].includes(j.process_state)) {
          return true;
        }
      }).map((j) => j.id);
      this.pendingJobId = this.pendingJobId.filter((id) => {
        if (completedJobIds.includes(id)) {
          return false
        }
        return true
      })
    },
  }
}
</script>