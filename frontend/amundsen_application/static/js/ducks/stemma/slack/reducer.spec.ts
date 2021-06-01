import reducer, {
  getSlackConversations,
  getSlackConversationsFailure,
  getSlackConversationsSuccess,
  SlackConversationsReducerState,
} from './reducer';

describe('slack conversation reducer', () => {
  let testState: SlackConversationsReducerState;
  beforeAll(() => {
    testState = {
      isLoading: false,
      statusCode: 200,
      conversations: [],
    };
  });

  it('should return the existing state if action is not handled', () => {
    expect(reducer(testState, { type: 'INVALID.ACTION' })).toEqual(testState);
  });

  it('should handle GetSlackConversations.REQUEST', () => {
    expect(reducer(testState, getSlackConversations('testUri'))).toEqual({
      ...testState,
      isLoading: true,
      statusCode: null,
    });
  });

  it('should handle GetSlackConversations.SUCCESS', () => {
    expect(
      reducer(
        testState,
        getSlackConversationsSuccess({
          conversations: [],
          statusCode: 202,
        })
      )
    ).toEqual({
      isLoading: false,
      statusCode: 202,
      conversations: [],
    });
  });

  it('should handle GetSlackConversations.FAILURE', () => {
    expect(
      reducer(
        testState,
        getSlackConversationsFailure({
          statusCode: 500,
          conversations: [],
        })
      )
    ).toEqual({
      isLoading: false,
      statusCode: 500,
      conversations: [],
    });
  });
});
