I was confused because I saw this code in the wild:

```python
import psycopg2
import psycopg2.extras

psyscopg2.extensions.abc(xyz)
```

I was expecting that, to use psycopg2.extensions, it would need to be imported
in that specific module. But it seems not?!
