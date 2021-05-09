from enum import Enum


class GSPJoinType(Enum):
    CROSS = 'cross'
    CROSS_APPLY = 'crossapply'
    FULL = 'full'
    FULL_OUTER = 'fullouter'
    INNER = 'inner'
    JOIN = 'join'
    LEFT = 'left'
    LEFT_OUTER = 'leftouter'
    LEFT_SEMI = 'leftsemi'
    NATURAL = 'natural'
    NATURAL_FULL = 'natural_full'
    NATURAL_FULL_OUTER = 'natural_fullouter'
    NATURAL_INNER = 'natural_inner'
    NATURAL_LEFT = 'natural_left'
    NATURAL_LEFT_OUTER = 'natural_leftouter'
    NATURAL_RIGHT = 'natural_right'
    NATURAL_RIGHT_OUTER = 'natural_rightouter'
    NESTED = 'nested'
    OUTER_APPLY = 'outerapply'
    RIGHT = 'right'
    RIGHT_OUTER = 'rightouter'
    STRAIGHT = 'straight'
    UNION = 'union'


GSP_JOIN_ENUM_STR_MAP = {
    GSPJoinType.CROSS: 'cross join',
    GSPJoinType.CROSS_APPLY: 'cross apply',
    GSPJoinType.FULL: 'full join',
    GSPJoinType.FULL_OUTER: 'full outer',
    GSPJoinType.INNER: 'inner join',
    GSPJoinType.JOIN: 'join',
    GSPJoinType.LEFT: 'left join',
    GSPJoinType.LEFT_OUTER: 'left outer join',
    GSPJoinType.LEFT_SEMI: 'left semi join',
    GSPJoinType.NATURAL: 'natural join',
    GSPJoinType.NATURAL_FULL: 'natural full join',
    GSPJoinType.NATURAL_FULL_OUTER: 'natural full outer join',
    GSPJoinType.NATURAL_INNER: 'natural inner join',
    GSPJoinType.NATURAL_LEFT: 'natural left join',
    GSPJoinType.NATURAL_LEFT_OUTER: 'natural left outer join',
    GSPJoinType.NATURAL_RIGHT: 'natural right join',
    GSPJoinType.NATURAL_RIGHT_OUTER: 'natural right outer join',
    GSPJoinType.NESTED: 'nested',
    GSPJoinType.OUTER_APPLY: 'outer apply',
    GSPJoinType.RIGHT: 'right join',
    GSPJoinType.RIGHT_OUTER: 'right outer join',
    GSPJoinType.STRAIGHT: 'straight join',
    GSPJoinType.UNION: 'union'
}
