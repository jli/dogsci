import pandas as pd

with pd.option_context('display.max_rows', 10):
    print(pd.DataFrame(list(range(50))))
