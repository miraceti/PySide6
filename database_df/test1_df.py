# DataFrames à concaténer
import pandas as pd
#base1
df1 = pd.DataFrame({'COMPLEXE': ["wclient1", "wclient2"], 
                    'CLIENT': ["wnom1", "wnom2"]
                    })
#base2
df2 = pd.DataFrame({'COMPLEXE': ["vclient3", "vclient4"], 
                    'CLIENT': ["vnom3", "vnom4"]
                    })


# Concaténation verticale (ajout de lignes)
df_concat = pd.concat([df1, df2], axis=0, ignore_index=True)

print(df_concat)