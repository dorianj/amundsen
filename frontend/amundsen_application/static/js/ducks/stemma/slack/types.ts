import { SlackConversation } from 'interfaces/Stemma/Slack';

export enum GetSlackConversations {
  REQUEST = 'amundsen/stemma/slack/GET_SLACK_CONVERSATIONS_REQUEST',
  SUCCESS = 'amundsen/stemma/slack/GET_SLACK_CONVERSATIONS_SUCCESS',
  FAILURE = 'amundsen/stemma/slack/GET_SLACK_CONVERSATIONS_FAILURE',
}

export interface GetSlackConversationsRequest {
  type: GetSlackConversations.REQUEST;
  payload: {
    resourceKey: string;
  };
}

export interface GetSlackConversationsResponse {
  type: GetSlackConversations.SUCCESS | GetSlackConversations.FAILURE;
  payload: GetSlackConversationsPayload;
}

export interface GetSlackConversationsPayload {
  conversations: SlackConversation[];
  statusCode?: number;
  statusMessage?: string;
}
