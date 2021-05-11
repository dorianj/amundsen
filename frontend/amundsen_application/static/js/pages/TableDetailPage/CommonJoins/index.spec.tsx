// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { shallow } from 'enzyme';

import CommonJoins, { CommonJoinsProps } from '.';

describe('CommonJoins', () => {
  const setup = (propOverrides?: Partial<CommonJoinsProps>) => {
    const props = {
      commonJoins: [
        {
          column: 'date',
          join_sql:
            'ca_covid.open_data.statewide_testing a join ca_covid.open_data.statewide_cases b on a.date = b.date',
          join_type: 'inner join',
          joined_on_table: {
            database: 'database',
            cluster: 'cluster',
            schema: 'schema',
            name: 'table',
            description: 'desc',
            schema_description: 'desc2',
          },
          joined_on_column: 'dt',
        },
        {
          column: 'user_id',
          join_sql:
            'this.table left outer join another.table c on c.user_id = this.table.user_id',
          join_type: 'left outer join',
          joined_on_table: {
            database: 'database',
            cluster: 'cluster',
            schema: 'schema',
            name: 'table',
            description: 'desc',
            schema_description: 'desc2',
          },
          joined_on_column: 'data',
        },
      ],
      ...propOverrides,
    };
    const wrapper = shallow<typeof CommonJoins>(
      <CommonJoins commonJoins={props.commonJoins} />
    );

    return { props, wrapper };
  };

  describe('render', () => {
    it('returns null if no data provided', () => {
      const { wrapper } = setup({ commonJoins: [] });
      expect(wrapper.instance()).toBeNull();
    });
  });
});
