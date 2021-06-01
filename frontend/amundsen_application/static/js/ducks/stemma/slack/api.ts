import axios, { AxiosError, AxiosResponse } from 'axios';
import * as qs from 'simple-query-string';

import { SlackConversation } from 'interfaces/Stemma/Slack';

export type GetSlackConversationsAPI = {
  message: string;
  conversations: SlackConversation[];
};

const STEMMA_SLACK_BASE_URI = '/api/stemma/slack/v1';

export function getSlackConversations(key: string) {
  const queryParams = qs.stringify({ key });

  return axios
    .get(`${STEMMA_SLACK_BASE_URI}/messages?${queryParams}`)
    .then((response: AxiosResponse<GetSlackConversationsAPI>) => {
      const { data, status } = response;

      return {
        conversations: data.conversations,
        statusCode: status,
        statusMessage: data.message,
      };
    })
    .catch((e: AxiosError<GetSlackConversationsAPI>) => {
      const { response } = e;
      const statusCode = response ? response.status : null;
      const statusMessage = response ? response.data.message : null;
      // eslint-disable-next-line prefer-promise-reject-errors
      return Promise.reject({ statusCode, statusMessage });
    });
}
