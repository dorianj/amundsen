// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { mount } from 'enzyme';

import CommonFilters, { CommonFiltersProps } from '.';

describe('CommonFilters', () => {
  const setup = (propOverrides?: Partial<CommonFiltersProps>) => {
    const props = {
      commonFilters: [
        {
          where_clause: 'where field is > 3',
          alias_mapping: [
            {
              alias: 'a',
              table: {
                database: 'database',
                cluster: 'cluster',
                schema: 'schema',
                name: 'table',
                description: 'desc',
                schema_description: 'desc2',
              },
            },
          ],
        },
      ],
      thisTable: 'this_table',
      ...propOverrides,
    };
    const wrapper = mount<typeof CommonFilters>(
      <CommonFilters
        commonFilters={props.commonFilters}
        thisTable={props.thisTable}
      />
    );

    return { props, wrapper };
  };

  describe('render', () => {
    it('returns null if no data provided', () => {
      const { wrapper } = setup({ commonFilters: [] });

      expect(wrapper.instance()).toBeNull();
    });

    it('renders a common join object', () => {
      const { wrapper } = setup();

      expect(wrapper.find('.common-filter-row').props()).toMatchObject({
        children: ['where ', 'field ', 'is ', '> ', '3 '],
      });
    });
  });
});
