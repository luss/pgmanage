<template>
  <h2 class="text-center">Jobs</h2>
  <div class="utility-jobs">
  <table class="table table-hover table-dark table-bordered">
    <thead class="text-center">
      <tr>
        <th scope="col"></th>
        <th scope="col"></th>
        <th scope="col"></th>
        <th scope="col"></th>
        <th scope="col">PID</th>
        <th scope="col">Type</th>
        <th scope="col">Server</th>
        <th scope="col">Object</th>
        <th scope="col">Start Time</th>
        <th scope="col">Status</th>
        <th scope="col">Time Taken (sec)</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="job in jobList" :key="job.id" class="text-center">
        <th scope="row"></th>
        <td><a class="btn" @click="deleteJob(job.id)"><i class="fas fa-times" title="delete job"></i></a></td>
        <td><a :class="['btn', { 'disabled': job.canStop }]" @click="stopJob(job.id)" title="Stop job"><i
              class="fa-regular fa-circle-stop"></i></a></td>
        <td><a class="btn" @click="getJobDetails(job.id)" title="View Details"><i class="fas fa-file-code"></i></a></td>
        <td>{{ job.utility_pid }}</td>
        <td>{{ job.details.type }}</td>
        <td>{{ job.details.server }}</td>
        <td>{{ job.details.object }}</td>
        <td>{{ job.start_time }}</td>
        <td :class="{
          'bg-info': jobStatus(job.process_state) === 'Running',
          'bg-danger': jobStatus(job.process_state) === 'Terminated' || jobStatus(job.process_state) === 'Terminating',
          'bg-success': jobStatus(job.process_state) === 'Finished',
          'bg-dirtied': jobStatus(job.process_state) === 'Failed'
        }">{{ jobStatus(job.process_state) }}
        </td>
        <td>{{ job.execution_time }}</td>
      </tr>
    </tbody>
  </table>
</div>

  <!-- Modal -->
  <div class="modal fade" :id="detailModalId" tabindex="-1" role="dialog" aria-hidden="true">
    <div class="modal-dialog" role="document">
      <div class="modal-content">
        <div class="modal-header p-3">
          <h3 class="modal-title">{{ selectedJob?.type_desc }}</h3>
          <button type="button" class="close" data-dismiss="modal" aria-label="Close">
            <span aria-hidden="true">&times;</span>
          </button>
        </div>
        <div class="modal-body">
          <p>{{ selectedJob?.description }}</p>
          <p>Command:</p>
          <p class="bg-ligth p-2 border border-dark">{{ selectedJob?.details?.cmd }}</p>
          <div class="d-flex justify-content-between">
            <a>Start time - {{ selectedJob?.start_time }}</a>
            <a>Execution time {{ selectedJob?.execution_time }}</a>
          </div>
          <div :style="{ height: '200px', overflowY: 'scroll' }" class="border border-dark p-1">
            <p v-for="log in logs"> {{ log }}</p>
          </div>
        </div>
        <div class="modal-footer">
          <a :class="['btn', 'btn-danger', { 'd-none': selectedJob.canStop }]" @click="stopJob(selectedJob.id)">Stop process</a>
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
          this.selectedJob.execution_time = resp.data.data.execution_time
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

<style scoped>
  .utility-jobs {
    height: 50vh;
    overflow-y: scroll;
  }
</style>