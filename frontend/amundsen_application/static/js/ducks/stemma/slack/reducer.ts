import { SlackConversation } from 'interfaces/Stemma/Slack';
import {
  GetSlackConversations,
  GetSlackConversationsRequest,
  GetSlackConversationsResponse,
  GetSlackConversationsPayload,
} from './types';

/* Actions */

export function getSlackConversations(
  resourceKey: string
): GetSlackConversationsRequest {
  return {
    payload: { resourceKey },
    type: GetSlackConversations.REQUEST,
  };
}

export function getSlackConversationsSuccess(
  payload: GetSlackConversationsPayload
) {
  return {
    payload,
    type: GetSlackConversations.SUCCESS,
  };
}

export function getSlackConversationsFailure(
  payload: GetSlackConversationsPayload
): GetSlackConversationsResponse {
  return {
    payload,
    type: GetSlackConversations.FAILURE,
  };
}

/* Reducer */

export interface SlackConversationsReducerState {
  isLoading: boolean;
  statusCode: number | null;
  conversations: SlackConversation[];
}

export const initialState: SlackConversationsReducerState = {
  isLoading: true,
  statusCode: null,
  conversations: [],
};

export default function reducer(
  state: SlackConversationsReducerState = initialState,
  action
): SlackConversationsReducerState {
  switch (action.type) {
    case GetSlackConversations.REQUEST:
      return {
        ...state,
        statusCode: null,
        isLoading: true,
      };
    case GetSlackConversations.FAILURE:
      return {
        ...state,
        isLoading: false,
        statusCode: action.payload.statusCode,
      };
    case GetSlackConversations.SUCCESS:
      return {
        ...state,
        isLoading: false,
        statusCode: action.payload.statusCode,
        conversations: action.payload.conversations,
      };
    default:
      return state;
  }
}
