# Sublist

A new list slice feature that allows you to create sub-lists.

## Overview

```python
>>> my_list = [0, 1, 2, 3, 4, 5]
>>> my_list[0:2::3]
[[0, 1], [2, 3], [4, 5]]
>>>
```

## Implementation

```python
#coding: sublist
a = [0, 1, 2, 3, 4, 5, 6]
print(a[1:2::3])
```

Let's think of `a[1:2::3]` as `name_of_list[start:stop::step]`. In this case,
`name_of_list` = a `start` = 1 `stop` = 2 `step` = 3

**sublist** implements a codec. (Like `#coding:utf-8`) The tokenizer in the codec,
changes the expression `name_of_list[start:stop::step]` as
`name_of_list['__unpack[start:stop::step]']` With the Ast module, the expression of
`name_of_list['__unpack[start:stop::step]']` turns in to

```python
[ *[ name_of_list[index:index + stop] for index in range(start, len(name_of_list), stop)][:step] ]
```

As a result, the code turns into this;

```python
a = [0, 1, 2, 3, 4, 5, 6]
print([*[a[index:index + 2] for index in range(1, len(a), 2)][:3]])
```

Output:

```python
[[1, 2], [3, 4], [5, 6]]
```

## Installation

sublist can be installed by running `pip install -e .` It requires Python 3.9.0+ to run.
