// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

export function getTableUrl(
  cluster: string,
  database: string,
  schema: string,
  tableName: string
): string {
  return `/table_detail/${cluster}/${database}/${schema}/${tableName}`;
}
