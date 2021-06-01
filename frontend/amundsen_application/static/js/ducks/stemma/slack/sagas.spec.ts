import { testSaga } from 'redux-saga-test-plan';
import * as API from './api';
import * as Sagas from './sagas';

import {
  getSlackConversations,
  getSlackConversationsFailure,
  getSlackConversationsSuccess,
} from './reducer';
import { GetSlackConversations } from './types';

describe('slack conversations sagas', () => {
  describe('getSlackConversationsWatcher', () => {
    it('takes every GetSlackConversations.REQUEST with getSlackConversationsWorker', () => {
      testSaga(Sagas.getSlackConversationsWatcher)
        .next()
        .takeEvery(
          GetSlackConversations.REQUEST,
          Sagas.getSlackConversationsWorker
        )
        .next()
        .isDone();
    });
  });

  describe('getSlackConversationsWorker', () => {
    it('executes flow for successfully getting slack conversations', () => {
      const mockResponse = {
        conversations: [],
        statusCode: 200,
      };
      testSaga(
        Sagas.getSlackConversationsWorker,
        getSlackConversations('testUri')
      )
        .next()
        .call(API.getSlackConversations, 'testUri')
        .next(mockResponse)
        .put(getSlackConversationsSuccess(mockResponse))
        .next()
        .isDone();
    });

    it('executes flow for a failed request slack conversations', () => {
      const mockResponse = {
        conversations: [],
        statusCode: 500,
        statusMessage: 'oops',
      };
      testSaga(
        Sagas.getSlackConversationsWorker,
        getSlackConversations('testUri')
      )
        .next()
        .call(API.getSlackConversations, 'testUri')
        // @ts-ignore
        .throw(mockResponse)
        .put(getSlackConversationsFailure(mockResponse))
        .next()
        .isDone();
    });
  });
});
