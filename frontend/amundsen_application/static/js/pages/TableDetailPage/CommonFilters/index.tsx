// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { Link } from 'react-router-dom';

import {
  AliasMapping,
  SimpleTableRef,
  TableCommonFilter,
} from 'interfaces/index';

import { getTableUrl } from 'utils/tableUtils';

import './styles.scss';

export interface CommonFiltersProps {
  commonFilters: TableCommonFilter[];
  thisTable: string;
}

type CommonFilterRowProps = {
  thisTable: string;
  whereClause: string;
  aliasMapping: AliasMapping[];
};

function getAliasWithUrl(
  columnComparison: string,
  aliasMapping: SimpleTableRef,
  thisTable: string
) {
  const tableUrl = getTableUrl(
    aliasMapping.cluster,
    aliasMapping.database,
    aliasMapping.schema,
    aliasMapping.name
  );
  const columnCompareTokens = columnComparison.split('.');

  if (thisTable === aliasMapping.name) {
    return aliasMapping.name + '.' + columnCompareTokens[1] + ' ';
  }
  return (
    <div className="where-inline">
      <Link className="resource-list-item table-list-item" to={tableUrl}>
        {aliasMapping.name}
      </Link>
      .{columnCompareTokens[1]}
      <span> </span>
    </div>
  );
}

const CommonFilterRow: React.FC<CommonFilterRowProps> = ({
  whereClause,
  aliasMapping,
  thisTable,
}: CommonFilterRowProps) => {
  const whereTokens = whereClause.split(' ');

  const results = whereTokens.map((whereItem) => {
    for (const alias of aliasMapping) {
      const aliasName = alias.alias + '.';

      if (whereItem.includes(aliasName)) {
        return getAliasWithUrl(whereItem, alias.table, thisTable);
      }
    }
    return whereItem + ' ';
  });

  return <div className="common-filter-row">{results}</div>;
};

const CommonFilters: React.FC<CommonFiltersProps> = ({
  commonFilters,
  thisTable,
}) => {
  if (commonFilters.length === 0) {
    return null;
  }

  return (
    <div className="common-filter-table">
      {commonFilters.map((where) => {
        return (
          <CommonFilterRow
            key={where.where_clause}
            thisTable={thisTable}
            whereClause={where.where_clause}
            aliasMapping={where.alias_mapping}
          />
        );
      })}
    </div>
  );
};

export default CommonFilters;
