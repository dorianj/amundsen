// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { Link } from 'react-router-dom';

import { TableCommonJoin } from 'interfaces/index';

import { getTableUrl } from 'utils/tableUtils';

import './styles.scss';

export interface CommonJoinsProps {
  commonJoins: TableCommonJoin[];
}

type CommonJoinRowProps = {
  column: string;
  joinedOnTableDatabase: string;
  joinedOnTableCluster: string;
  joinedOnTableSchema: string;
  joinedOnTableName: string;
  joinedOnColumb: string;
  joinType: string;
  joinSql: string;
};

const CommonJoinRow: React.FC<CommonJoinRowProps> = ({
  column,
  joinedOnTableDatabase,
  joinedOnTableCluster,
  joinedOnTableSchema,
  joinedOnTableName,
  joinedOnColumb,
  joinType,
  joinSql,
}: CommonJoinRowProps) => {
  const tableUrl = getTableUrl(
    joinedOnTableCluster,
    joinedOnTableDatabase,
    joinedOnTableSchema,
    joinedOnTableName
  );
  return (
    <div className="common-join-row">
      <table>
        <tr>
          <td className="join-table-key">
            <div className="join-key">Column</div>
          </td>
          <td className="join-table-value">
            <div className="join-value">{column} </div>
          </td>
        </tr>

        <tr>
          <td className="join-table-key">
            <div className="join-key">Joined on</div>
          </td>
          <td className="join-table-value">
            <div className="join-value">
              <Link
                className="resource-list-item table-list-item"
                to={tableUrl}
              >
                {joinedOnTableSchema}.{joinedOnTableName}
              </Link>
              .{joinedOnColumb}
            </div>
          </td>
        </tr>

        <tr>
          <td className="join-table-key">
            <div className="join-key">How</div>
          </td>
          <td className="join-table-value">
            <div className="join-clause join-value">{joinType}</div>
          </td>
        </tr>

        <tr>
          <td className="join-table-key">
            <div className="join-key">SQL</div>
          </td>
          <td className="join-table-value">
            <div className="join-clause join-value">{joinSql}</div>
          </td>
        </tr>
      </table>
    </div>
  );
};

const CommonJoins: React.FC<CommonJoinsProps> = ({ commonJoins }) => {
  if (commonJoins.length === 0) {
    return null;
  }

  return (
    <div className="common-joins-table">
      {commonJoins.map((join, index) => {
        return (
          <CommonJoinRow
            key={join.joined_on_column}
            joinedOnTableDatabase={join.joined_on_table.database}
            joinedOnTableCluster={join.joined_on_table.cluster}
            joinedOnTableSchema={join.joined_on_table.schema}
            joinedOnTableName={join.joined_on_table.name}
            joinedOnColumb={join.joined_on_column}
            column={join.column}
            joinType={join.join_type}
            joinSql={join.join_sql}
          />
        );
      })}
    </div>
  );
};

export default CommonJoins;
