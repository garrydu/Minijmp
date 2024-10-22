import numpy as np
##################
from pandastable_local.data_orig import TableModel as TM


class TableModel(TM):
    def deleteColumns(self, cols=None):
        """Remove all cols or list provided"""

        df = self.df
        colnames = df.columns[cols]
        df.drop(colnames, axis=1, inplace=True)
        return

    def deleteCells(self, rows, cols, fills=np.nan):
        self.df.iloc[rows, cols] = fills
        return
