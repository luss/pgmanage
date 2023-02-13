<template>
  <h2 class="text-center">Processes</h2>
  <table class="table table-hover table-dark table-bordered">
    <thead>
      <tr>
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
      <tr v-for="process in processList" :key="process.id" class="text-center">
        <th scope="row"></th>
        <td><a class="btn" @click="deleteProcess(process.id)"><i class="fas fa-times"></i></a></td>
        <td><a class="btn"><i class="fas fa-file-code"></i></a></td>
        <td>{{ process.utility_pid }}</td>
        <td>{{ process.details.type }}</td>
        <td>{{ process.details.server }}</td>
        <td>{{ process.details.object }}</td>
        <td>{{ process.stime }}</td>
        <td class="">{{ processStatus(process.process_state) }}</td>
        <td>{{ process.execution_time }}</td>
      </tr>
    </tbody>
  </table>
</template>

<script>
const WORKER_INTERVAL = 1000;

const BgProcessManagerProcessState = {
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
      processList: [],
      workerId: ''
    }
  },
  mounted() {
    // this.syncProcesses()
    this.startWorker()
  },
  methods: {
    processStatus(process_state) {
      if (process_state === BgProcessManagerProcessState.PROCESS_STARTED) {
        return 'Running'
      } else if (process_state === BgProcessManagerProcessState.PROCESS_FINISHED) {
        return 'Finished'
      } else if (process_state === BgProcessManagerProcessState.PROCESS_TERMINATED) {
        return 'Terminated'
      }
      return ''
    },
    startProcess(jobId, desc) {
      this.pendingJobId.push(jobId)

    },

    syncProcesses() {
      axios.get('/bgprocess')
        .then((resp) => {
          this.processList = resp.data.data.map((p) => {
            let processState = this.evaluateProcessState(p);
            return {
              ...p,
              process_state: processState,
              canDrop: ![BgProcessManagerProcessState.PROCESS_NOT_STARTED, BgProcessManagerProcessState.PROCESS_STARTED].includes(processState),
            }
          })
          this.checkPending();
        })
        .catch((error) => {
          console.log(error)
        })
    },
    checkPending() {
      const completedProcIds = this.processList.filter((p) => {
        if (![
          BgProcessManagerProcessState.PROCESS_NOT_STARTED,
          BgProcessManagerProcessState.PROCESS_STARTED,
          BgProcessManagerProcessState.PROCESS_TERMINATING].includes(p.process_state)) {
          return true;
        }
      }).map((p) => p.id);
      console.log(this.processList, 'CHECK PROCESS LIST')
      console.log(completedProcIds, 'CHECK COMPLETEDPROCIDS')
      console.log(this.pendingJobId, 'PENDING BEFORE')
      this.pendingJobId = this.pendingJobId.filter((id) => {
        if (completedProcIds.includes(id)) {
          // let p = this.processList.find((p) => p.id = id)
          return false
        }
        return true
      })
      console.log(this.pendingJobId, "CHECK PENDING JOB")
    },
    startWorker() {
      this.syncProcesses()
      this.pendingJobId = this.processList.filter((p) => (p.process_state === BgProcessManagerProcessState.PROCESS_STARTED)).map((p) => p.id)
      this.workerId = setInterval(() => {
        if (this.pendingJobId.length > 0) {
          this.syncProcesses();
        }
      }, WORKER_INTERVAL)
    },
    stopProcess(jobId) {
      this.processList.find((p) => p.id == jobId).process_state = BgProcessManagerProcessState.PROCESS_TERMINATING;
      axios.post(`/bgprocess/stop/${jobId}/`)
        .then((resp) => {
          console.log(resp)
          this.processList.find((p) => p.id == jobId).process_state = BgProcessManagerProcessState.PROCESS_TERMINATED;
        })
    },
    evaluateProcessState(p) {
      let retState = p.process_state;
      if ((p.etime || p.exit_code != null) && p.process_state == BgProcessManagerProcessState.PROCESS_STARTED) {
        retState = BgProcessManagerProcessState.PROCESS_FINISHED;
      }
      if (retState == BgProcessManagerProcessState.PROCESS_FINISHED && p.exit_code != 0) {
        retState = BgProcessManagerProcessState.PROCESS_FAILED;
      }
      return retState;
    },
    // acknowledge(jobIds) {
    //   const removeJob = (jobId) => {
    //     this.processList = this.processList.filter((p) => p.id != jobId)
    //   }
    //   jobIds.forEach((jobId) => {
    //     axios.post(`bgprocess/remove/${jobId}`)
    //       .then((resp) => {
    //         console.log(resp)
    //         removeJob(jobId)
    //       })
    //       .catch((error) => {
    //         console.log(error)
    //       })
    //   })
    // }
    deleteProcess(process_id) {
      axios.post(`/bgprocess/delete/${process_id}/`)
        .then((resp) => {
          this.syncProcesses()
        })
        .catch((error) => {
          console.log(error)
        })
    }
  }
}
</script>