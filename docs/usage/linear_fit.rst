.. raw:: html

   <style>
      .tight-table td {
             white-space: normal !important;
                       }
                          </style>

Linear Fit
==========

Choose Stats>Linear Fit.

PUT WINDOW DIALOG HERE

The Linear fit share a same dialog with orthogonal fit, and also provide scatter plot and correlation ellipse too. 

- **X Y Values:** Select two different column for the predictor, i.e. X, and the response variable, i.e. Y. Swapping the two values does not simply Swapping the axes, but will affect the result, which will be discussed in the orthogonal fit section. 
- **Scatter Plot:** 

  - **Scatter Dots:** Turn on and off showing individual data points in the plot output.
  - **Correlation Ellipse:** Display a light blue filled ellipse for Bivariate Normal Distribution, which is only available with Pearson's correlation. The ellipse will be always drawn unless Pearson's Correlation is unselected. 
  - **Ellipse Outline:** Display a red outline of the ellipse above. Either of these two settings can work alone, but also together.

- **Linear Fit:** Show the fited line in red in the output plot.
- **Confidence Interval:** Show the confidence Interval of the fitted line in green dash. The range of the interval is decided by the Alpha settting at the end.
- **Prediction Interval:** Show the Prediction Interval of the fitted line in purple dash. The range of the interval is decided by the Alpha setting as well.

- **Orthogonal Fit:** Toggle the orthogonal fitted line, which will be discussed in next section.

- **Axis Settings:**

  - **Label:** If left blank, the axis will be labelled with the data column name.
  - **Min and Max:** The by-default min and max of axis are set by the **Margin** in **Plot Setting** below. 
  - **Legend and Grid:** They won't be shown by default.
  - **Margin:** A margin of 0.1 means using a width of 10% of range of data as the blank margin of the plot.

- **Alpha:** Set the range of Confidence Interval and Prediction Interval as (1-alpha)100%. For example, if alpha is 0.05, the CI range will be 95%, and if it's 0.2, the range will be 80%.

The output tables follows JMP pro 17 format and calibrated the result too. 

Plot Interpretation
-------------------

To understand the plot and the output prints, we will use the data in the CSV file of `ElectricCarData_Clean-kaggle.csv` in the `sample_data` folder. First using the Top Speed as the predictor variable, which is X, and the Range column as the response variable, which is Y, fit the line. Then swap their order and fit them again. 
They are good examples of swapping X and Y in linear fit generates different results. The two red lines are not symmetrical to the diagonal line. 

.. image:: images/linear_fit_plot.png
   :align: center

Fitted Line
~~~~~~~~~~~

Linear fit uses a Least Square Method. The core of calculating a linear fit lies in minimizing the distances between the actual data points and the line itself. This is done by focusing on the vertical distances (residuals) from each point to the proposed line.

It's very import to note that the distances minimized is the vertial distance to the fitted line. Since the distance is not symmetrical to the diagonal, the fitted line won't either.

Confidence Interval
~~~~~~~~~~~~~~~~~~~


