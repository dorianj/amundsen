// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { Link } from 'react-router-dom';

import { AliasMapping, SimpleTableRef, TableCommonFilter } from 'interfaces/index';

import {getTableUrl} from 'utils/tableUtils';

import './styles.scss';

export interface CommonFiltersProps {
  common_filters: TableCommonFilter[];
  this_table: string;
}

type CommonFilterRowProps = {
  this_table: string;
  where_clause: string;
  alias_mapping: AliasMapping[]
};


function getAliasWithUrl(col_comparison: string, alias_mapping: SimpleTableRef, this_table: string){
  const tableUrl = getTableUrl(
    alias_mapping.cluster,
    alias_mapping.database,
    alias_mapping.schema,
    alias_mapping.name
  )
  const col_compare = col_comparison.split('.');

  if (this_table == alias_mapping.name){
    return alias_mapping.name + '.' + col_compare[1] + ' ';
  }
  else {
    return (
      <div className="where-inline">
          <Link className="resource-list-item table-list-item" to={tableUrl}>
            {alias_mapping.name}
          </Link>.{col_compare[1]}<span> </span>
      </div>
    )
  }

}


const CommonFilterRow: React.FC<CommonFilterRowProps> = ({
  where_clause,
  alias_mapping,
  this_table
}: CommonFilterRowProps) => {
  const split_where = where_clause.split(' ');

  const results = split_where.map((where_item) => {
    for (const alias of alias_mapping){
      const alias_str = alias.alias + '.';

      if (where_item.includes(alias_str)){
        return getAliasWithUrl(where_item, alias.table, this_table);
      }
    }
    return where_item + ' ';
  })

  return (
    <div className="common-filter-row">
      {results}
    </div>
  );
}


const CommonFilters: React.FC<CommonFiltersProps> = ({ common_filters, this_table }) => {
  if (common_filters.length === 0) {
      return null;
  }

  return (
      <div className="common-filter-table">
        {common_filters.map((where, index) => {
          return (
            <CommonFilterRow
              key={where.where_clause}
              this_table={this_table}
              where_clause={where.where_clause}
              alias_mapping={where.alias_mapping}
            />
          );
        })}
      </div>
  );
};

export default CommonFilters;
