import io
import pandas as pd
from tkinter import END, StringVar, Entry, messagebox, ttk
import numpy as np
#  import os
############ pandastable #############
from pandastable_local.core import Table
from pandastable_local.core_orig import sort_mixed
from pandastable_local import util
from pandastable_local.data import TableModel
from pandastable_local.dialogs import MultipleValDialog, filedialog
############## Own Module ###############
#  from modified_header import MColumnHeader as ColumnHeader
#  from modified_header import RowHeader
from df_combine import df_combine
from utilities import (grouping_by_labels, verifyNewColName, filter_voids,
                       is_void, defaultNewColName)
from dialog import findRepDialog
import tkinter


class FilteredEditBlocked(BaseException):
    """Stops a table change while rows are filtered.

    Raised by MTable.storeCurrent, which every table-changing action calls
    before it changes anything. It derives from BaseException so the
    actions' own `except Exception` blocks do not swallow it."""


def _patch_report_callback_exception():
    """Do not print a traceback for FilteredEditBlocked (the user has
    already been told why nothing happened)."""
    original = tkinter.Tk.report_callback_exception
    if getattr(original, '_filtered_edit_aware', False):
        return

    def report(self, exc, val, tb):
        if isinstance(val, FilteredEditBlocked):
            return
        return original(self, exc, val, tb)

    report._filtered_edit_aware = True
    tkinter.Tk.report_callback_exception = report


_patch_report_callback_exception()


class MTable(Table):
    def doExport(self, filename=None):
        """Do a simple export of the cell contents to csv"""

        if filename is None:
            filename = filedialog.asksaveasfilename(parent=self.master,
                                                    defaultextension='.csv',
                                                    initialdir=self.currentdir,
                                                    #  initialdir=os.getcwd(),
                                                    title='Export to CSV',
                                                    filetypes=[("csv", "*.csv"),
                                                               #  ("excel", "*.xls"),
                                                               #  ("html", "*.html"),
                                                               ("All files", "*.*")])
        if filename:
            self.model.save(filename)
            self.rememberFolder(filename)
        return

    def row1ToHeader(self):
        """
        Use the contents of row 1 as the column names and remove row 1.
        Empty cells keep the old name. Names are text: 5.0 becomes "5".
        Repeated names get _1, _2, ...
        """
        df = self.model.df
        if len(df) == 0:
            return
        cols = list(df)
        new_headers = []
        for x in range(len(cols)):
            value = df.iloc[0, x]
            new_name = cols[x] if is_void(value) else self._header_text(value)
            new_headers.append(
                verifyNewColName(str(new_name), new_headers))
        new = df.iloc[1:].copy()
        new.columns = new_headers
        if df.index.equals(pd.RangeIndex(len(df))):
            new.reset_index(drop=True, inplace=True)
        # Columns that held text only because of the header row become
        # numbers again (as if the file had been read with that header).
        for x in range(new.shape[1]):
            if new.iloc[:, x].dtype == object:
                new.isetitem(x, self._as_numbers(new.iloc[:, x]))
        self.storeCurrent()
        self.model.df = new
        self.redraw()
        return

    @staticmethod
    def _header_text(value):
        """Text for a column name: whole numbers without '.0'."""
        if isinstance(value, (float, np.floating)) and float(value).is_integer():
            return str(int(value))
        return str(value).strip()

    @staticmethod
    def _as_numbers(column):
        """The column as numbers if every non-empty cell is a number,
        otherwise the column unchanged."""
        num = pd.to_numeric(column, errors='coerce')
        # Cells that did not become numbers must all be empty ('', spaces).
        # Stop at the first real text, so text columns are cheap to check.
        missed = np.flatnonzero(num.isna().to_numpy() &
                                column.notna().to_numpy())
        for i in missed:
            if not is_void(column.iat[i]):
                return column
        if not num.notna().any():
            return column
        return num

    def findText(self, evt=None):
        """Simple text search in whole table"""

        if hasattr(self, 'searchframe') and self.searchframe is not None:
            return
        self.searchframe = findRepDialog(self)
        self.searchframe.grid(
            row=self.queryrow,
            column=0,
            columnspan=3,
            sticky='news')
        return

    def copy(self, rows=None, cols=None):
        """Copy cell contents from clipboard - overwrites table."""

        data = self.getSelectedDataFrame()
        try:
            #  if len(data) == 1 and len(data.columns) == 1:
            data.to_clipboard(index=False, header=False)
            #  else:
            #  data.to_clipboard()
        except BaseException:
            messagebox.showwarning("Warning",
                                   "No clipboard software.\nInstall xclip",
                                   parent=self.parentframe)
        return

    def fillColumn(self):
        """Fill a column with a data range"""

        dists = ['normal', 'gamma', 'uniform', 'random integer', 'logistic']
        d = MultipleValDialog(
            title='New Column',
            initialvalues=(
                0,
                1,
                False,
                False,
                dists,
                1.0,
                1.0),
            labels=(
                'Linear Low',
                'Linear High',
                'Add Random Noise to Linear',
                'Fill Random Numbers',
                'Distribution',
                'Mean',
                'Std'),
            types=(
                'string',
                'string',
                'checkbutton',
                'checkbutton',
                'combobox',
                'float',
                'float'),
            tooltips=(
                'start value if filling with data',
                'end value if filling with data',
                'add random noise upon the linear filling above',
                'create random noise data in the ranges',
                'sampling distribution for noise',
                'mean/scale of distribution',
                'std dev./shape of distribution'),
            parent=self.parentframe)
        if d.result is None:
            return
        low, high, add_random, random, dist, param1, param2 = d.results
        use_dist = bool(random) or bool(add_random)
        need_range = (not random) or (
            use_dist and dist in ('uniform', 'random integer', 'logistic'))
        need_params = use_dist and dist in ('normal', 'gamma')

        def number(label, text):
            """The field as a number, or None after telling the user."""
            try:
                return float(str(text).strip())
            except ValueError:
                messagebox.showwarning(
                    "Fill With Data", "'%s' must be a number (it is '%s')."
                    "\n\nThe column was not changed." % (label, text),
                    parent=self.parentframe)
                return None

        if need_range:
            low = number('Linear Low', low)
            high = number('Linear High', high) if low is not None else None
            if low is None or high is None:
                return
        if need_params:
            param1 = number('Mean', param1)
            param2 = number('Std', param2) if param1 is not None else None
            if param1 is None or param2 is None:
                return

        df = self.model.df
        n = len(df)
        if n == 0 or len(df.columns) == 0:
            return
        try:
            if use_dist:
                if dist == 'normal':
                    data = np.random.normal(param1, param2, n)
                elif dist == 'gamma':
                    data = np.random.gamma(param1, param2, n)
                elif dist == 'uniform':
                    data = np.random.uniform(low, high, n)
                elif dist == 'random integer':
                    # Low to High inclusive, as in JMP and Minitab
                    data = np.random.randint(int(low), int(high) + 1, n)
                else:  # logistic
                    data = np.random.logistic(low, high, n)
        except ValueError as e:
            messagebox.showwarning(
                "Fill With Data", "Cannot draw %s numbers with these "
                "settings: %s\n\nThe column was not changed." % (dist, e),
                parent=self.parentframe)
            return
        if not random:
            # n evenly spaced values from Low to High (just Low for 1 row)
            linear = np.linspace(low, high, n) if n > 1 else np.array([low])
            data = data + linear if add_random else linear
        self.storeCurrent()
        # By position: the table's row labels may have gaps (rows removed)
        df.isetitem(self.currentcol, np.asarray(data))
        self.redraw()
        self.tableChanged()
        return

    def sortColumnIndex(self):
        """Sort the column header by the current rows values"""

        cols = self.model.df.columns
        # get only sortable cols
        # temp = self.model.df._convert(convert_numeric=True) **** depreciated
        # ****
        temp = self.model.df.apply(pd.to_numeric, errors='ignore')
        temp = temp.select_dtypes(include=['int', 'float'])
        rowindex = temp.index[self.currentrow]
        #  row = temp.ix[rowindex] **** depreciated ****
        row = temp.iloc[rowindex]
        # add unsortable cols to end of new ordered ones
        newcols = list(temp.columns[row.argsort()])
        a = list(set(cols) - set(newcols))
        newcols.extend(a)
        self.model.df = self.model.df.reindex(columns=newcols)
        self.redraw()
        return

    def update_rowcolors(self):
        """Update row colors if present so that it syncs with current dataframe."""
        #
        #  df = self.model.df
        #  rc = self.rowcolors
        #  if len(df) == len(self.rowcolors):
        #      rc.set_index(df.index, inplace=True)
        #  elif len(df) > len(rc):
        #      idx = df.index.difference(rc.index)
        #      # self.rowcolors = rc.append(pd.DataFrame(index=idx))
        #      self.rowcolors = pd.concat([rc, pd.DataFrame(index=idx)])
        #  else:
        #      idx = rc.index.difference(df.index)
        #      rc.drop(idx, inplace=True)
        #  # check columns
        #  cols = list(rc.columns.difference(df.columns))
        #  print(cols)
        #  if len(cols) > 0:
        #      try:
        #          rc.drop(cols, inplace=True)
        #      except BaseException:
        #          pass
        #  cols = list(df.columns.difference(rc.columns))
        #  if len(cols) > 0:
        #      for col in cols:
        #          rc[col] = np.nan
        return

    def setAlignment(self, colnames=None):
        """Set column alignments, overrides global value"""

        cols = self.multiplecollist
        df = self.model.df
        cf = self.columnformats
        cfa = cf['alignment']
        vals = ['Left', 'Right', 'Center']
        conv = {"Left": 'w', "Right": 'e', "Center": 'center'}
        d = MultipleValDialog(title='set alignment',
                              initialvalues=[vals],
                              labels=['Align:'],
                              types=['combobox'],
                              parent=self.parentframe)
        if d.result is None:
            return
        aln = conv[d.results[0]]
        #  print(aln)
        for col in cols:
            colname = df.columns[col]
            cfa[colname] = aln
        self.redraw()
        return

    def handle_right_click(self, event):
        return

    def drawCellEntry(self, row, col, text=None):
        """When the user single/double clicks on a text/number cell,
          bring up entry window and allow edits."""

        def select_all(event):
            event.widget.select_range(0, END)
            return 'break'

        if not self.editable:
            return
        h = self.rowheight
        #  model = self.model
        text = self.model.getValueAt(row, col)
        if pd.isnull(text):
            text = ''
        x1, y1, x2, y2 = self.getCellCoords(row, col)
        w = x2 - x1
        self.cellentryvar = txtvar = StringVar()
        txtvar.set(text)

        column = self.model.df.iloc[:, col]
        if str(column.dtype) == 'category':
            # Category cells: an editable drop-down box. Pick a category
            # from the list, or type a new value (it becomes a category).
            self.cellentry = ttk.Combobox(
                self.parentframe, width=20, textvariable=txtvar,
                values=[str(c) for c in column.cat.categories],
                takefocus=1, font=self.thefont)
            self.cellentry.bind(
                '<<ComboboxSelected>>',
                lambda x: self.handleCellEntry(row, col))
        else:
            self.cellentry = Entry(self.parentframe, width=20,
                                   textvariable=txtvar,
                                   takefocus=1,
                                   font=self.thefont)
        self.cellentry.icursor(END)
        self.cellentry.bind(
            '<Return>',
            lambda x: self.handleCellEntry(
                row,
                col))
        self.cellentry.bind("<FocusIn>", select_all)
        # After Return the editor moves on and keeps the focus, so Ctrl-Z
        # (Cmd-Z on macOS, bound on the table) would not reach undo
        # without this.
        util.bind_modifier(self.cellentry, "z", self._undo_key)
        self.cellentry.bind("<Tab>",
                            lambda x: self.handleCellEntry(
                                row,
                                col, nxt_col=True))
        self.cellentry.focus_set()
        self.entrywin = self.create_window(x1, y1,
                                           width=w, height=h,
                                           window=self.cellentry, anchor='nw',
                                           tag='entry')
        #  if col == 0:
        #  self.xview_moveto(0)
        #  print(col, row)
        return

    def _undo_key(self, event=None):
        self.undo()
        return 'break'

    def handleCellEntry(self, row, col, nxt_col=False):
        """Callback for cell entry"""

        value = self.cellentryvar.get()
        if self._edit_cell(row, col, lambda df, r: self.model.setValueAt(
                self._category_value(df, col, value), r, col, df=df)):
            self.drawText(row, col, value, align=self.align)
        self.delete('entry')
        self.gotonextCell(nxt_col=nxt_col)
        return

    def gotonextCell(self, nxt_col=False):
        """Move highlighted cell to next cell in row after enter cell entry"""

        if hasattr(self, 'cellentry'):
            self.cellentry.destroy()
        nrows, ncols = self.model.df.shape
        if nxt_col:
            if self.currentcol + 1 >= ncols:
                return  # last column: stay on the edited cell
            self.currentcol += 1
        else:
            if self.currentrow + 1 >= nrows:
                return  # last row: stay on the edited cell
            self.currentrow = self.currentrow + 1
        #  self.drawSelectedRect(self.currentrow, self.currentcol)
        #  self.xview_moveto(0)
        self.drawCellEntry(self.currentrow, self.currentcol)
        #  if self.currentcol == 0:
        #  self.xview_moveto(0.5)
        #  self.xview_scroll(-1, "unit")
        return

    def doBindings(self):
        """pandastable binds Shift-click to the right-click menu on macOS,
        and MiniJMP has no right-click menu, so Shift-click did nothing.
        Make it select from the current cell to the clicked cell, as on
        other systems."""
        super().doBindings()
        self.bind('<Shift-Button-1>', self.handle_left_shift_click)
        return

    def handle_left_release(self, event):
        """Mouse button released. The original also put a pick-only
        drop-down over category cells here, on every click; it covered the
        cell editor of a double click, so category cells could not be
        typed into. Category cells now use the editable drop-down box of
        drawCellEntry (double click), like other cells."""
        self.endrow = self.get_row_clicked(event)
        return

    def handle_double_click(self, event):
        """Do double click stuff. Selected row/cols will already have
           been set with single click binding"""

        row = self.get_row_clicked(event)
        col = self.get_col_clicked(event)
        self.drawCellEntry(self.currentrow, self.currentcol)
        #  self.xview_scroll(-1, "unit")
        return

    @staticmethod
    def _read_clipboard(header=None):
        """The clipboard text as a table, or None if it cannot be read.
        Copied cells (from MiniJMP or Excel) are tab-separated; other text
        is read as comma-separated. pandas only switches to tabs by itself
        when at least 2 rows were copied, so one copied row ended up in a
        single cell."""
        try:
            from pandas.io.clipboard import clipboard_get
            text = clipboard_get()
            if not text or not text.strip():
                return None
            sep = '\t' if '\t' in text else ','
            return pd.read_csv(io.StringIO(text), sep=sep, header=header,
                               on_bad_lines='skip')
        except Exception:
            print("Can't paste.")
            return None

    def paste(self, event=None):
        """Paste a new table from the clipboard"""

        df = self._read_clipboard(header=None)
        if df is None or len(df) == 0:
            return
        self.storeCurrent()

        try:
            ins_y = min(self.multiplerowlist)
            ins_x = min(self.multiplecollist)
        except BaseException:
            ins_y = ins_x = 0
        model = TableModel(df_combine(
            self.model.df, df,
            ins_y=ins_y, ins_x=ins_x))
        self.updateModel(model)
        self.redraw()
        self.updateIndex()
        return

    def paste_header(self, event=None):
        """Paste a new table from the clipboard"""

        df = self._read_clipboard(header=0)
        if df is None or len(df) == 0:
            return
        self.storeCurrent()

        try:
            ins_x = min(self.multiplecollist)
        except BaseException:
            ins_x = 0
        new_df = df_combine(
            self.model.df, df,
            ins_y=0,  # min(self.multiplerowlist),
            ins_x=ins_x)
        col_names = new_df.columns.tolist()
        df2_cols = df.columns.tolist()
        for x in range(len(df2_cols)):
            xx = ins_x + x
            col_names[xx] = verifyNewColName(df2_cols[x], col_names)
        new_df.columns = col_names
        model = TableModel(new_df)
        self.updateModel(model)
        self.redraw()
        self.updateIndex(ask=False)
        return

    def splitColumn(self, evt=None):
        """
        Split data column with a categorical column into several
        individual columns.
        """

        df = self.model.df
        cols = list(df)

        d = MultipleValDialog(
            title='Split Column',
            initialvalues=(
                cols,
                cols),
            labels=(
                'Data Column',
                'Grouping ID Column'),
            types=(
                'combobox',
                'combobox'),
            tooltips=(
                'The data to be splitted into seperated columns',
                'Categorical data to group the data'),
            parent=self.parentframe)
        if d.result is None:
            return
        self.storeCurrent()
        data = df[d.results[0]]
        grpList = df[d.results[1]]
        [data, grpList] = filter_voids([data, grpList])
        keys = list(set(grpList))

        resList = grouping_by_labels(data, grpList, keys=keys)

        def insertCol(col1, col2):
            """
            Move col1 next to col2, useful for placing a new column
            made from the first one next to it so user can see it easily
            """
            ind1 = self.model.df.columns.get_loc(col1)
            ind2 = self.model.df.columns.get_loc(col2)
            self.model.moveColumn(ind1, ind2 + 1)

        for i in range(len(resList)):
            key = verifyNewColName(str(keys[i]), cols)
            df[key] = resList[i] + [np.nan] * \
                (df.shape[0] - len(resList[i]))
        self.redraw()
        return

    def stackColumn(self, evt=None):
        """
        Stack selected columns into two colums with data and grouping keys
        keys are the column ids
        """

        self.storeCurrent()
        df = self.model.df
        selected_cols = list(df.columns[self.multiplecollist])
        cols = list(df)

        # model.addColumn, not self.addColumn: that would record two more
        # undo steps on top of the one stored above.
        self.model.addColumn(verifyNewColName('Stk Keys', cols), 'object')
        self.model.addColumn(verifyNewColName('Stk Data', cols), 'object')

        resKeys, resData = [], []
        for col in selected_cols:
            data = list(df[col])
            resKeys = resKeys + [col] * len(data)
            resData = resData + data
        [resKeys, resData] = filter_voids([resKeys, resData])
        ins_y = 0
        ins_x = df.shape[1] - 2
        model = TableModel(df_combine(
            self.model.df,
            pd.DataFrame({'1': resKeys, '2': resData}),
            ins_y=ins_y, ins_x=ins_x))
        self.updateModel(model)

        self.redraw()
        self.updateIndex(ask=False)
        return

    def addColumn(self, newname=None):
        """Add a new column"""

        if newname is None:
            coltypes = ['object', 'float64']
            default_name = defaultNewColName(self.model.df.columns)
            d = MultipleValDialog(title='New Column',
                                  initialvalues=(coltypes, default_name),
                                  labels=('Column Type', 'Name'),
                                  types=('combobox', 'string'),
                                  parent=self.parentframe)
            if d.result is None:
                return
            else:
                dtype = d.results[0]
                newname = d.results[1].strip() or default_name
        else:
            dtype = 'object'

        #  df = self.model.df
        if newname is not None:
            if newname in self.model.df.columns:
                messagebox.showwarning("Name exists",
                                       "Name already exists!",
                                       parent=self.parentframe)
            else:
                self.storeCurrent()
                self.model.addColumn(newname, dtype)
                self.parentframe.configure(width=self.width)
                self.update_rowcolors()
                self.redraw()
                self.tableChanged()
        return

    def updateIndex(self, ask=True, drop=True):
        """Reset index and redraw row header"""

        #  self.storeCurrent()
        #  df = self.model.df
        #  if (df.index.name is None or df.index.names[0] is None) and ask == True:
        #      drop = messagebox.askyesno("Reset Index", "Drop the index?",
        #                                parent=self.parentframe)
        # Renumber only plain row numbers. Row labels that carry data (the
        # groups of a Value Counts or Group-Aggregate sub-table: named, text
        # or several levels) stay with their rows.
        idx = self.model.df.index
        if not (isinstance(idx, pd.MultiIndex) or
                any(n is not None for n in idx.names) or
                not pd.api.types.is_integer_dtype(idx.dtype)):
            self.model.df.reset_index(drop=drop, inplace=True)
        self.update_rowcolors()
        # self.set_rowcolors_index()
        self.redraw()
        # self.drawSelectedCol()
        #  if hasattr(self, 'pf'):
        #      self.pf.updateData()
        self.update_rowcolors()
        self.tableChanged()
        return

    def deleteRow(self, ask=False):
        """Delete a selected row"""

        n = True
        if ask:
            n = messagebox.askyesno("Delete",
                                    "Delete selected rows?",
                                    parent=self.parentframe)
        if not n:
            return

        if len(self.multiplerowlist) > 1:
            if n:
                self.storeCurrent()
                rows = self.multiplerowlist
                self.model.deleteRows(rows)
                self.setSelectedRow(0)
                self.clearSelected()
                self.update_rowcolors()
                self.redraw()
        else:
            if n:
                self.storeCurrent()
                row = self.getSelectedRow()
                self.model.deleteRows([row])
                self.setSelectedRow(row - 1)
                self.clearSelected()
                self.update_rowcolors()
                self.redraw()
        self.updateIndex()
        return

    def colorRows(self):
        return

    def colorColumns(self):
        return

    def sortAll(self, evt=None):
        """
        Sort the entire table by 1-3 cols.
        """

        df = self.model.df
        cols = [""] + list(df)

        d = MultipleValDialog(
            title='Sort All Columns',
            initialvalues=(
                cols,
                True,
                cols, True,
                cols,
                True),
            labels=(
                'Sort By',
                'Ascending',
                'Then By',
                'Ascending',
                'Then By',
                'Ascending'),
            types=(
                'combobox',
                'checkbutton',
                'combobox',
                'checkbutton',
                'combobox',
                'checkbutton'),
            tooltips=(
                '',
                '',
                '', '', '',
                ''),
            parent=self.parentframe)
        if d.result is None:
            return
        self.storeCurrent()
        col_list, a_list = [], []
        for i in [0, 2, 4]:
            if d.results[i] != "":
                col_list.append(d.results[i])
                a_list.append(1 if d.results[i + 1] else 0)
            else:
                break
        if len(col_list) == 0:
            return

        try:
            #  print(col_list, d.results[3])
            self.model.df = df = sort_mixed(df, col_list, a_list)
        except BaseException:
            print('could not sort')

        self.updateIndex(ask=False)
        self.redraw()
        return

    def sortSelected(self, evt=None):
        """
        Sort the entire table by 1-3 cols.
        """

        df = self.model.df
        columnIndex = self.multiplecollist
        if isinstance(columnIndex, int):
            columnIndex = [columnIndex]

        colnames = list(df.columns[columnIndex])
        cols = [""] + colnames

        d = MultipleValDialog(
            title='Sort Selected Columns',
            initialvalues=(
                cols,
                True,
                cols, True,
                cols,
                True),
            labels=(
                'Sort By',
                'Ascending',
                'Then By',
                'Ascending',
                'Then By',
                'Ascending'),
            types=(
                'combobox',
                'checkbutton',
                'combobox',
                'checkbutton',
                'combobox',
                'checkbutton'),
            tooltips=(
                '',
                '',
                '', '', '',
                ''),
            parent=self.parentframe)
        if d.result is None:
            return
        self.storeCurrent()
        col_list, a_list = [], []
        for i in [0, 2, 4]:
            if d.results[i] != "":
                col_list.append(d.results[i])
                a_list.append(1 if d.results[i + 1] else 0)
            else:
                break
        if len(col_list) == 0:
            return

        dfSub = df[colnames].copy()
        dfSub = sort_mixed(dfSub, col_list, a_list)
        # Put the sorted rows back by position, under the table's own row
        # labels. Matching by label would undo the sort, and after rows were
        # removed (labels 0, 2, 3...) it filled rows with empty cells.
        dfSub.index = df.index
        df[colnames] = dfSub
        self.redraw()
        return

    # Undo history. Each entry is one of
    #   ("df", table copy): the whole table, stored by storeCurrent() before
    #       a major change (insert/delete/sort rows, add/rename columns...);
    #   ("cell", row, col, name, old value, new value, check): one cell typed
    #       in or picked from a category drop-down;
    #   ("col", row, col, name, old column, check): a typed cell whose edit
    #       changed the type of its whole column (text typed into a number
    #       column), so the old column is kept.
    # "check" records how the edited column looked right after the edit; the
    # entry is only applied while the table still matches it, so an untracked
    # change can never make undo write into wrong rows. Redo entries have the
    # same form.
    MAX_UNDO = 50
    MAX_UNDO_SNAPSHOTS = 5
    N_CHECK_CELLS = 16

    def _history(self):
        if not hasattr(self, "undo_stack"):
            self.undo_stack, self.redo_stack = [], []
        return self.undo_stack, self.redo_stack

    def clearUndoHistory(self):
        undo_stack, redo_stack = self._history()
        undo_stack.clear()
        redo_stack.clear()
        self.prevdf = None
        return

    @staticmethod
    def _same(a, b):
        """a == b for cell values and column names, with NaN equal to NaN"""
        try:
            if a is b or bool(a == b):
                return True
        except (TypeError, ValueError):
            return False
        try:
            return bool(pd.isna(a)) and bool(pd.isna(b))
        except (TypeError, ValueError):
            return False

    def _check(self, df, row, col):
        """Row labels, dtype and a few values (the edited cell plus cells
        spread over the column) of column col, to recognise this state later
        without comparing or hashing the whole column"""
        n = len(df)
        step = max(1, n // self.N_CHECK_CELLS)
        pos = sorted(set(range(0, n, step)) | {row})
        values = list(df.iloc[pos, col])
        return (df.index, str(df.iloc[:, col].dtype), pos, values)

    def _matches(self, df, col, name, check):
        index, dtype, pos, values = check
        if col >= df.shape[1] or not self._same(df.columns[col], name):
            return False
        if not (df.index is index or df.index.equals(index)):
            return False
        if str(df.iloc[:, col].dtype) != dtype:
            return False
        now = list(df.iloc[pos, col])
        return all(self._same(x, y) for x, y in zip(now, values))

    def _push_undo(self, entry):
        undo_stack, redo_stack = self._history()
        undo_stack.append(entry)
        redo_stack.clear()  # a new change drops what could be redone
        while (len(undo_stack) > self.MAX_UNDO or
               sum(e[0] == "df" for e in undo_stack) > self.MAX_UNDO_SNAPSHOTS):
            del undo_stack[0]
        # core_orig hides "Undo" in the popup menu while prevdf is None
        self.prevdf = undo_stack
        return

    def storeCurrent(self):
        """Store current version of the table before a major change is made.

        While rows are filtered the grid shows a filtered copy, and changes
        to it would be lost when the filter is closed: the change is
        stopped (FilteredEditBlocked) with a message instead. Typing into a
        cell does not come here and still works while filtered."""
        if self.filtered:
            messagebox.showinfo(
                "Filter Rows",
                "The table cannot be changed while rows are filtered "
                "(only typing into cells works). Close the filter first.",
                parent=self.parentframe)
            raise FilteredEditBlocked()
        # The table is about to change (rows sorted, inserted, deleted...):
        # an open cell editor would keep its old text and row position and
        # could write that text into another row on Enter.
        self._close_editor()
        self._push_undo(("df", self.model.df.copy()))
        return

    def _filtered_row(self, row, col):
        """Position in the full table of the shown row `row` while rows are
        filtered, or None if it cannot be found for sure."""
        view, full = self.model.df, getattr(self, 'dataframe', None)
        if full is None or col >= full.shape[1] or \
                not self._same(full.columns[col], view.columns[col]):
            return None
        label = view.index[row]
        if not full.index.is_unique:
            return None
        try:
            pos = full.index.get_loc(label)
        except (KeyError, TypeError, ValueError):
            return None
        return pos if isinstance(pos, (int, np.integer)) else None

    def _edit_cell(self, row, col, set_value):
        """Set a cell the user typed or picked. set_value(df, r) sets the
        cell at position (r, col) of df.

        While rows are filtered the shown table is a filtered copy: the
        value goes into that copy at the shown row and into the full table
        at the row with the same row label, and the undo step is kept for
        the full table (Undo works again after the filter is closed).
        Returns False if nothing was changed."""
        plain_set = set_value

        def set_value(df, r):
            plain_set(df, r)
            self._auto_numeric(self.model.df if df is None else df, col, r)

        if not self.filtered:
            self._record_cell_edit(
                self.model.df, row, col, lambda: set_value(None, row))
            return True
        full_row = self._filtered_row(row, col)
        if full_row is None:
            messagebox.showinfo(
                "Edit", "This cell cannot be matched to a row of the full "
                "table (repeated row labels, or the columns were changed "
                "while filtered). Close the filter and edit it there.",
                parent=self.parentframe)
            self.redraw()
            return False

        def change():
            set_value(self.dataframe, full_row)
            set_value(self.model.df, row)

        self._record_cell_edit(self.dataframe, full_row, col, change)
        return True

    def _category_value(self, df, col, value):
        """For a category column: the typed text as a value of the column's
        kind (a number if the categories are numbers), added as a new
        category if it is not one yet. Other columns: the text unchanged."""
        if df is None:
            df = self.model.df
        column = df.iloc[:, col]
        if str(column.dtype) != 'category' or is_void(value):
            return value
        cats = column.cat.categories
        v = value
        if pd.api.types.is_numeric_dtype(cats.dtype):
            try:
                v = float(value)
                if pd.api.types.is_integer_dtype(cats.dtype) and v.is_integer():
                    v = int(v)
            except ValueError:
                v = value
        if v not in cats:
            df.isetitem(col, column.cat.add_categories([v]))
        return v

    def _auto_numeric(self, df, col, row=None):
        """After a cell of a text (object) column was typed in: if every
        non-empty cell of that column is now a number, make it a number
        column, as reading a CSV file would. Typed numbers in a new table
        would otherwise stay text ("12" sorts before "2")."""
        column = df.iloc[:, col]
        if column.dtype != object:
            return
        if row is not None:
            value = column.iat[row]
            if not is_void(value) and pd.isna(pd.to_numeric(
                    pd.Series([value]), errors='coerce')[0]):
                return  # the typed cell is text: the column stays text
        # Quick look at a few cells spread over the column first, so a big
        # text column is not converted cell by cell on every Enter.
        step = max(1, len(column) // 64)
        sample = column.iloc[::step]
        if self._as_numbers(sample) is sample and sample.notna().any() and \
                not sample.map(is_void).all():
            return
        numbers = self._as_numbers(column)
        if numbers is not column:
            df.isetitem(col, numbers)
        return

    def _record_cell_edit(self, df, row, col, change):
        """Run change(), which sets the cell at positions (row, col) of df,
        and keep an undo entry for it (also if change() raises midway)."""
        if not df.columns.is_unique:
            # setValueAt finds the column by name, so with repeated names an
            # edit can reach other columns too: keep the whole table instead.
            before_df = df.copy()
            try:
                change()
            finally:
                if not before_df.equals(df):
                    self._push_undo(("df", before_df))
            return
        name = df.columns[col]
        # No copy: if the edit converts the column to another dtype, pandas
        # builds a new column and this one keeps the old values.
        column = df.iloc[:, col]
        dtype = column.dtype
        old = df.iat[row, col]
        try:
            change()
        finally:
            if df.iloc[:, col].dtype != dtype:
                # The cell may have been written into this column before
                # the column was converted: put its old value back.
                saved = column.copy()
                saved.iat[row] = old
                self._push_undo(("col", row, col, name, saved,
                                 self._check(df, row, col)))
            else:
                new = df.iat[row, col]
                if not self._same(old, new):
                    self._push_undo(("cell", row, col, name, old, new,
                                     self._check(df, row, col)))
        return

    def _fits(self, entry):
        """Whether an entry can be applied to the table as it is now"""
        if entry[0] == "df":
            return True
        col, name, check = entry[2], entry[3], entry[-1]
        return self._matches(self.model.df, col, name, check)

    def _swap(self, entry):
        """Apply an entry and return the entry that reverses it"""
        if entry[0] == "df":
            current = ("df", self.model.df.copy())
            # Work on a copy so later edits do not change the stored snapshot.
            self.model.df = entry[1].copy()
            return current
        df = self.model.df
        if entry[0] == "cell":
            _, row, col, name, old, new, _ = entry
            df.iat[row, col] = old
            return ("cell", row, col, name, new, old,
                    self._check(df, row, col))
        _, row, col, name, column, _ = entry
        current = df.iloc[:, col].copy()
        df.isetitem(col, column.copy())
        return ("col", row, col, name, current, self._check(df, row, col))

    def _close_editor(self):
        """Close an open cell editor or category drop-down, so it cannot
        write its old text back after the table changed"""
        if getattr(self, "cellentry", None) is not None:
            self.cellentry.destroy()
        self.delete('entry')
        return

    def _step(self, source, target, action):
        if self.filtered:
            messagebox.showinfo(
                action, "%s is not available while rows are filtered. "
                "Close the filter first." % action, parent=self.parentframe)
            return
        stale = 0
        while source and not self._fits(source[-1]):
            source.pop()
            stale += 1
        if stale:
            # Leave the table alone; the next press continues with the
            # entries that still fit.
            messagebox.showinfo(
                action, "%d earlier step(s) could not be %s because the "
                "table was changed by an action that undo does not track. "
                "They were removed from the history and the table was not "
                "changed." % (stale, "undone" if action == "Undo" else
                              "redone"), parent=self.parentframe)
        elif source:
            self._close_editor()
            target.append(self._swap(source.pop()))
            self.redraw()
            self.updateModel(self.model)
        self.prevdf = self.undo_stack if self.undo_stack else None
        return

    def undo(self, event=None):
        """Undo the last table change"""
        undo_stack, redo_stack = self._history()
        self._step(undo_stack, redo_stack, "Undo")
        return

    def redo(self, event=None):
        """Redo the last undone table change"""
        undo_stack, redo_stack = self._history()
        self._step(redo_stack, undo_stack, "Redo")
        return

    def handleEntryMenu(self, *args):
        """Pick a value from the drop-down of a category column"""
        value = self.dropvar.get()
        self.delete('entry')
        row = self.currentrow
        col = self.currentcol

        def set_value(df, r):
            try:
                self.model.setValueAt(value, r, col, df=df)
            except BaseException:
                self.model.setValueAt(float(value), r, col, df=df)

        if self._edit_cell(row, col, set_value):
            self.drawText(row, col, value, align=self.align)
        return

    def _fresh_history(self, load, *args, **kwargs):
        """Run a File action that may put a different table in place.
        A new table starts with an empty undo history."""
        old = self.model
        result = load(*args, **kwargs)
        if self.model is not old:
            self.clearUndoHistory()
        return result

    def new(self):
        return self._fresh_history(super().new)

    def load(self, filename=None):
        return self._fresh_history(super().load, filename)

    def importCSV(self, filename=None, dialog=False, **kwargs):
        return self._fresh_history(super().importCSV, filename, dialog,
                                   **kwargs)

    def loadExcel(self, filename=None):
        return self._fresh_history(super().loadExcel, filename)

    def tableChanged(self):
        """Callback to be used when dataframe changes so that other
            widgets and data can be updated"""

        self.updateFunctions()
        self.updateWidgets()
        try:
            if hasattr(self, 'pf'):
                self.pf.updateData()
        except BaseException:
            pass
        return

    def adjustColumnWidths(self, limit=30):
        return

    def clearDataUp(self, evt=None):
        """Delete cells and move cells below up"""

        if self.allrows:
            self.deleteColumn()
            return
        if not self.editable:
            return
        answer = messagebox.askyesno(
            "Clear Confirm",
            "Clear this data and move the cells below up?",
            parent=self.parentframe)
        if not answer:
            return

        rows = self.multiplerowlist
        cols = self.multiplecollist
        df = self.model.df
        self.storeCurrent()
        vSet = set(df.iloc[rows, cols].values.ravel())
        fills = 65535
        while fills in vSet:
            fills += 1
        self.model.deleteCells(rows, cols, fills=fills)
        names = df.columns[cols]
        for col in names:
            res = [i for i in df[col] if i != fills]
            res = res + [np.nan] * (df.shape[0] - len(res))
            df[col] = res

        self.redraw()
        return
