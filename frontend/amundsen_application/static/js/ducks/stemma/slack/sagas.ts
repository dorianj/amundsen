import { SagaIterator } from 'redux-saga';
import { call, put, takeEvery } from 'redux-saga/effects';

import * as API from './api';
import {
  getSlackConversationsSuccess,
  getSlackConversationsFailure,
} from './reducer';
import { GetSlackConversations } from './types';

export function* getSlackConversationsWorker(action): SagaIterator {
  try {
    const { resourceKey } = action.payload;
    const response = yield call(API.getSlackConversations, resourceKey);

    yield put(getSlackConversationsSuccess(response));
  } catch (error) {
    yield put(getSlackConversationsFailure(error));
  }
}

export function* getSlackConversationsWatcher(): SagaIterator {
  yield takeEvery(GetSlackConversations.REQUEST, getSlackConversationsWorker);
}
