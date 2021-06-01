export interface SlackUser {
  display_name: string;
  id: string;
  first_name: string;
  last_name: string;
  real_name: string;
  image_72: string;
  image_original: string;
  title?: string;
}

export interface SlackMessage {
  author: string;
  channel_id: string;
  channel: string;
  key: string;
  team: string;
  text: string;
  // Timestamp of the parent message.
  thread_ts: string;

  // Timestamp of the current message.
  // In our case this will be the same as the thread_ts as we are only capturing parent messages
  ts: string;
  type: string;
}

export interface SlackConversation {
  message: SlackMessage;
  author: SlackUser;
  permalink: string;
  replies: number;
}
