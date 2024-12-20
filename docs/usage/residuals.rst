Residual Plots
==============

The function will analyze the residuals of a linear regression.

Choose Stats > Residual Plots

.. image:: images/residual1.png
   :align: center

- **X Y Values:** Select two different columns for the predictor (X) and the response variable (Y). Only residual plots will be displayed; the linear regression of the two variables is performed in the background and will not be shown.

.. include:: linear_fit.rst
   :start-line: 207
   :end-line: 225


.. image:: images/residual2.png
   :align: center

- **Residuals versus order:** This plot displays the residuals in the order the data were collected.

  - Use this plot to verify the assumption that residuals are independent. Independent residuals show no trends or patterns over time. Ideally, residuals should fall randomly and not exceed the red dashed lines.
  - Patterns may indicate that residuals near each other are correlated and not independent. 


.. list-table::
   :widths: 33 33 33

   * - .. image:: images/residuals_vs_order_cycles.png
     - .. image:: images/residuals_vs_order_decreasing_pattern.png
     - .. image:: images/residuals_vs_order_abrupt_change_pattern.png

If you see a pattern, investigate the cause. The above types of patterns may indicate that the residuals are dependent.

- **Residuals versus fits:** This graph plots residuals on the y-axis and fitted values on the x-axis. Use it to verify that residuals are randomly distributed with constant variance.

  - Ideally, the points should fall randomly on both sides of 0, with no recognizable patterns in the points. 
  - The patterns in the following table may indicate that the model does not meet the model assumptions.

    - Fanning or uneven spreading of residuals across fitted valuee means Nonconstant variance
    - Curvilinear menas A missing higher-order term
    - A point that is far away from zero means An outlier
    - A point that is far away from the other points in the x-direction means An influential point 

- **Histogram of residuals:** This shows the distribution of residuals for all observations. Use it to determine if data are skewed or include outliers.

  - A long tail in one direction indicates Skewness
  - A bar that is far away from the other bars indicates An outlier

A histogram is most effective when you have approximately 20 or more data points. If the sample is too small, then each bar on the histogram does not contain enough data points to reliably show skewness or outliers. 

- **Normality QQ Plot:** This plot displays residuals versus their expected values if normally distributed. Use it to verify that residuals are normally distributed. The plot should approximately follow a straight line.

  - Check out the help page of `Normality` for more information about QQ plot interpreting. `LINK <https://minijmp.readthedocs.io/en/latest/usage/normality.html>`_
  - If a nonnormal pattern is observed, use other residual plots to check for issues like missing terms or time order effects. Non-normal residuals can lead to inaccurate confidence intervals and p-values.
