import * as React from 'react';
import {
  SlackConversation,
  SlackMessage,
  SlackUser,
} from 'interfaces/Stemma/Slack';
import AvatarLabel from 'components/AvatarLabel';

import './styles.scss';
import { formatDateTimeLong } from '../../../utils/dateUtils';

export interface SlackConversationListProps {
  conversations: SlackConversation[];
}

export interface SlackConversationItemProps {
  message: SlackMessage;
  author: SlackUser;
  permalink: string;
  replies: number;
}

const SlackConversationItem = ({
  message,
  author,
  permalink,
  replies,
}: SlackConversationItemProps) => {
  const key = `key:${message.key}`;
  const messageTime = formatDateTimeLong({
    epochTimestamp: parseFloat(message.thread_ts),
  });

  return (
    <li className="list-group-item slack-conversation-item" id={key}>
      <div className="container">
        <p className="column-name">
          <AvatarLabel label={author.display_name} src={author.image_72} />
          <small className="channel-name">
            {messageTime} - #{message.channel}
          </small>
        </p>
        <div className="">
          <p>{message.text}</p>
        </div>
        {/* at least -1 for the tagged message */}
        <p className="text-secondary">({replies - 1} Replies)</p>
        <p>
          {/* eslint-disable-next-line react/jsx-no-target-blank */}
          <a className="view-slack" target="_blank" href={permalink}>
            View in Slack
          </a>
        </p>
      </div>
    </li>
  );
};

const SlackConversationList: React.FC<SlackConversationListProps> = ({
  conversations,
}: SlackConversationListProps) => {
  if (conversations.length === 0) {
    return null;
  }

  const queryList = conversations.map(
    ({ message, author, permalink, replies }) => (
      <SlackConversationItem
        message={message}
        author={author}
        permalink={permalink}
        replies={replies}
      />
    )
  );

  return (
    <ul className="query-list list-group" role="tablist">
      {queryList}
    </ul>
  );
};

export default SlackConversationList;
