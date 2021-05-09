// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { Link } from 'react-router-dom';

import { TableCommonJoin } from 'interfaces/index';

import {getTableUrl} from 'utils/tableUtils';

import './styles.scss';

export interface CommonJoinsProps {
  common_joins: TableCommonJoin[];
}

type CommonJoinRowProps = {
  column: string;
  joined_on_table_database: string;
  joined_on_table_cluster: string;
  joined_on_table_schema: string;
  joined_on_table_name: string;
  joined_on_column: string;
  join_type: string;
  join_sql: string;
};



const CommonJoinRow: React.FC<CommonJoinRowProps> = ({
  column,
  joined_on_table_database,
  joined_on_table_cluster,
  joined_on_table_schema,
  joined_on_table_name,
  joined_on_column,
  join_type,
  join_sql
}: CommonJoinRowProps) => {

  const tableUrl = getTableUrl(
    joined_on_table_cluster,
    joined_on_table_database,
    joined_on_table_schema,
    joined_on_table_name
  )
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
              <Link className="resource-list-item table-list-item" to={tableUrl}>
                {joined_on_table_schema}.{joined_on_table_name}
              </Link>.{joined_on_column}
            </div>
          </td>
        </tr>

        <tr>
          <td className="join-table-key">
            <div className="join-key">How</div>
          </td>
          <td className="join-table-value">
            <div className="join-clause join-value">{join_type}</div>
          </td>
        </tr>

        <tr>
          <td className="join-table-key">
            <div className="join-key">SQL</div>
          </td>
          <td className="join-table-value">
            <div className="join-clause join-value">{join_sql}</div>
          </td>
        </tr>

      </table>
    </div>
  );
}


const CommonJoins: React.FC<CommonJoinsProps> = ({ common_joins }) => {
  if (common_joins.length === 0) {
      return null;
  }

  return (
      <div className="common-joins-table">
        {common_joins.map((join, index) => {
          return (
            <CommonJoinRow
              key={join.joined_on_column}
              joined_on_table_database={join.joined_on_table.database}
              joined_on_table_cluster={join.joined_on_table.cluster}
              joined_on_table_schema={join.joined_on_table.schema}
              joined_on_table_name={join.joined_on_table.name}
              joined_on_column={join.joined_on_column}
              column={join.column}
              join_type={join.join_type}
              join_sql={join.join_sql}
            />
          );
        })}
      </div>
  );
};

export default CommonJoins;
