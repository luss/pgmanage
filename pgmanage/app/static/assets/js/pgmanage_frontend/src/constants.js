const queryState = {
  Idle: 0,
  Executing: 1,
  Ready: 2,
};

const tabStatusMap = {
  NOT_CONNECTED: 0,
  IDLE: 1,
  RUNNING: 2,
  IDLE_IN_TRANSACTION: 3,
  IDLE_IN_TRANSACTION_ABORTED: 4,
};

const queryModes = {
  DATA_OPERATION: 0,
  FETCH_MORE: 1,
  FETCH_ALL: 2,
  COMMIT: 3,
  ROLLBACK: 4,
};

export { queryState, tabStatusMap, queryModes };
