.. raw:: html

   <style>
      .tight-table td {
             white-space: normal !important;
                       }
                          </style>

Correlation
===========

Choose Stats > Correlation.

.. image:: images/cor1.png
   :align: center

Correlation is a statistical measure that describes the strength and direction of the relationship between two variables.

- **X Y Values:** Select the two sets of data. The order of the dataset, either which is X, won't change the correlation result, but only the plotting orientation. 
- **Correlation Select:**  There are two main types of correlation analyses: parametric (like Pearson's correlation) and nonparametric (such as Spearman's and Kendall's correlations). Their differences will be discussed, but select Pearson's Correlation by default if you are unsure.
- **Scatter Plot Setting:** A scatter plot of data will be displayed, all the settings below are about this plot. 

  - **Correlation Ellipse:** Display a light blue filled ellipse for Bivariate Normal Distribution, which is only available with Pearson's correlation.  
  - **Ellipse Outline:** Display a red outline of the ellipse above. Either of these two settings can work alone or together.
  - **Alpha:** Determines the contour level of the ellipse. If alpha is 0.05, the ellipse of 95% Probability Contour will be displayed; while 0.3 for 70% of Probability Contour. Leave it by default if you are unsure. This alpha also determines the confidence intervals range of the Pearson's correlation coefficient.
  - **Axis Settings:**

    - **Label:** If left blank, the axis will be labelled with the data column name.
    - **Min and Max:** The default min and max of the axis are set by the **Margin** in **Plot Setting** below.
    - **Legend and Grid:** They won't be shown by default.
    - **Margin:** A margin of 0.1 means using a width of 10% of the range of data as the blank margin of the plot.

The results of correlation have been calibrated with Minitab 20, JMP pro 17 and R (lib Hmisc 5.1).

- The Pearson's correlation shows the same result as Minitab, while I didn't find CI of the correlation coefficient in JMP.
- The Spearman's rho and Kendall's tau are the same as the JMP results, with the p-value of Kendall's in a few cases showing <0.1 difference from JMP, though not affecting judgment.
- The Hoeffding's D value works the same with JMP, and the p-value is the same as R.
- Minitab doesn't have Hoeffding and Kendall's to compare with.


Pearson's Correlation
---------------------

.. highlight :: none
   
::

    ---- Pearson correlation alpha = 0.050 ----
    Correlation coefficient: -0.027
    Confidence Interval (-0.063, 0.009)
    Covariance: -6.206
    p-value = 0.136 N = 3000


The above is a sample output of Pearson's Correlation. 

Correlation Coefficient
~~~~~~~~~~~~~~~~~~~~~~~

The Pearson correlation coefficient (r) ranges from -1 to +1.

- r = 0 indicates no linear relationship
- r = +1 indicates a perfect positive linear relationship
- r = -1 indicates a perfect negative linear relationship

Degrees of Correlation:

- Perfect: Values near ±1 indicate a perfect correlation, where one variable’s increase (or decrease) is mirrored by the other.
- High Degree: Values between ±0.50 and ±1 suggest a strong correlation.
- Moderate Degree: Values between ±0.30 and ±0.49 indicate a moderate correlation.
- Low Degree: Values below +0.29 are considered a weak correlation.
- No Correlation: A value of zero implies no relationship.

However, the criteria depend on the type of data, and the purpose of the evaluation. For some situation, a abs(r) > 0.7 or higher is considered a good correlation.

**The confidence intervals** are of the correlation coefficient, whose range is set by the alpha in the dialog. 

Covariance
~~~~~~~~~~

Covariance and Pearson correlation coefficient are related, but they serve different purposes. Covariance is more fundamental but harder to interpret, while Pearson correlation provides a standardized measure of linear relationship strength that's easier to understand and compare across different variable pairs. If you are unsure, ignore the covariance value.

.. list-table:: Comparison of Covariance and Pearson Correlation
   :header-rows: 1
   :widths: 20 40 40
   :class: tight-table

   * - Aspect
     - Covariance
     - Pearson Correlation
   * - Range
     - Can be any real number (-∞ to +∞)
     - Always between -1 and +1
   * - Interpretation
     - Difficult to interpret magnitude directly
     - Easily interpretable (e.g., 0.8 indicates strong positive correlation)
   * - Units
     - Depends on the units of the variables
     - Unitless (normalized)
   * - Use cases
     - Often used in variance calculations and as a building block for other statistics
     - Used to measure the strength and direction of linear relationships

p-Value
~~~~~~~

The H0 is that there is no linear correlation in the population. The alternative hypothesis (H1) states that there is a correlation. When interpreting Pearson correlation results, if the p-value is less than the chosen significance level (e.g., 0.05), you would reject the null hypothesis and conclude that there is evidence of a linear relationship between the variables in the population. 

For example the quoted result above show the p-value of the correlation between Height and Col Cholesterol Level is 0.136 which is higher than 0.05, we can't reject the null hypothesis of no linear relationship between the two populations. 


Correlation Ellipse
-------------------

The correlation ellipse is a strong tool to visualize the direction and strength of the correlation. The long axis indicates the direction of the correlation, either positive or negative. The width of the ellipse, i.e., the ratio between the short and long axes, shows the correlation strength; the narrower the ellipse, the stronger the correlation.

.. list-table::
   :widths: 33 33 33

   * - .. image:: images/cor_p1.png
     - .. image:: images/cor_p2.png
     - .. image:: images/cor_p3.png

The screenshots show different levels of correlations. The data is available at `data_sample` folder in the CSV file of `human_age_prediction-Kaggle`. 

To discuss the mechanism behind the ellipse, we first look at the univariate Normal Distribution, i.e., distribution changing via one variable. The area under the PDF curve corresponds to probability: 68% area between ± σ and 95% between ± 1.96σ.

.. image:: images/cor_e_1d_norm.png
   :align: center

A Bivariate Normal Distribution has two independent variables. For example, when shooting bullets towards the target center, the bullet's position in X and Y both follows a univariate Normal Distribution. Combining together, the probability density on the 2-dimensional plane of target paper forms a bell shape; when viewed from the top, it has a contour of an ellipse.


.. |img1| image:: images/cor_e_2d_norm1.png
   :width: 40%

.. |img2| image:: images/cor_e_2d_norm2.png
   :width: 40%

.. raw:: html

    <div style="text-align: center;">

|img1| |img2|

.. raw:: html

    </div>

The ellipse is the contour line of the Bivariate Normal Distribution of the two datasets in the correlation. The commonly used 95% ellipse boundary is the two-dimensional form of the red line in the univariate distribution, which contains 95% integrated probability under the bell curve. The integrated volume under the bell dorm within the boundary is 95%.

.. image:: images/contour_cor_5_25_50.png
   :align: center

The above is a stacked image, not generated by the software directly, of 95%, 75% and 50% ellipse of the Bivariate Normal Distribution. They are the contour line of the bell shape of the distribution.

Since the ellipse is drawn based on Normal Distribution. When both varialbes are normally distributed, the Pearson correlation coefficient fully describes their linear relationship. In this case, the probability contours of the distribution form perfect ellipses.

**If one or both of the variables are not normally distributed, the ellipse can still be drawn as a visualization tool, but its interpretation may be less straightforward.** Pearson correlation does not strictly require normally distributed inputs.

Non-parametric Correlation
--------------------------

The term "non-parametric" refers to the fact that these tests do not rely on assumptions about the specific parameters (like mean and standard deviation) of the population distribution. Instead, they are based on the ranks or order of the data. The term refers to the methods, while the evaluation methods are still good for data under common distributions, like gamma, lognormal etc.. But the methods are not sensitive to whether the input variables follow a certain distribution or not, unlike Pearson's correlation. 

Spearman's rho and Kendall's tau
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Spearman's rank correlation coefficient and Kendall's tau are two prominent measures among various statistics designed to assess monotonic associations between variables. These measures possess the property of invariance under strictly monotonic-increasing, or decreasing, transformations of the variables.

Both Spearman's and Kendall's coefficients were originally developed for continuous variables. In terms of sample calculations:

- Spearman's coefficient is computed as the Pearson correlation coefficient of the ranked data.
- Kendall's tau evaluates pairs of observations, calculating the difference between the proportion of concordant pairs (where both variables increase or decrease together) and discordant pairs (where the variables move in opposite directions).

.. list-table:: Comparison of Spearman and Kendall Correlations
   :header-rows: 1
   :widths: 20 40 40
   :class: tight-table
   :align: left

   * - Aspect
     - Spearman
     - Kendall
   * - Calculation method
     - Based on the differences between ranks
     - Based on concordant and discordant pairs
   * - Interpretation
     - Measures the strength of the monotonic relationship
     - Measures the strength of dependence between variables
   * - Magnitude
     - Generally produces larger values
     - Usually produces smaller values than Spearman
   * - Sensitivity
     - More sensitive to errors and discrepancies in data
     - Less sensitive to errors and outliers
   * - Sample size considerations
     - Preferred for larger sample sizes
     - More accurate with smaller sample sizes, especially for strong correlations
   * - Ties in data
     - May not handle ties in data as well
     - Better at handling ties in data

Though Spearman's rho is claimed to handle non-linear relationship, it still tests only monotonic relationship. In data distribution has some non-linear portion for example a cubical or logarithm relationship, Pearson' correlation still gives decent distinguish to the error amount containing in the data, especially p-value, if we don't argue its null hypothesis of linear relationship. In most of my tests, Spearman's rho has similar p-value with Pearson's correlation, except for some carefully tuned corner case like the one below.

.. list-table::
   :widths: 33 67
   :class: tight-table

   * - .. image:: images/cor_corner_spearman.png
     - .. code-block:: none

			---- Pearson correlation alpha = 0.050 ----
			Correlation coefficient: 0.655
			Confidence Interval (-0.194, 0.943)
			Covariance: 0.547
			p-value = 0.111	N = 7

			---- Spearman's rho Correlation ----
			Spearman correlation: 1.000
			Spearman p-value: 0.000 

Even though it's not strictly correct in null hypothesis, Spearman's rho doesn't work better than Pearson in distinguishing if two variables have a non-linear monotonic relationship.

However, Pearson's correlation and Spearman's rho both handle outliers poorly. Kendall's tau stands out in this perspective. Tested with non-linear related data I have and those with outliers, Kendall's tau did a better job in telling the potential correlation between the variables. For example, in the `sample_data` folder `correlation.pickle`, the column `X` and column `Outlier` have a non-linear relationship with outliers. Only Kendall's tau gives a small p-value, while all three methods' coefficients are similar.p


.. list-table::
   :widths: 33 67
   :class: tight-table

   * - .. image:: images/cor_outlier.png
     - .. code-block:: none

            ---- Pearson correlation alpha = 0.050 ----
            Correlation coefficient: -0.255
            Confidence Interval (-0.550, 0.097)
            Covariance: -360.564
            p-value = 0.152 N = 33

            ---- Spearman's rho Correlation ----
            Spearman correlation: -0.229
            Spearman p-value: 0.200

            ---- Kendall's tau Correlation ----
            Kendall's tau: -0.282
            Kendall's p-value: 0.021

Hoeffding's D
~~~~~~~~~~~~~

Unlike Spearman's rho, Kendall's tau, and Pearsons's Correlation, Hoeffding's D can be used to detect a wide variety of dependence structures beyond monotonic association. For example the distributions below, except for the first one which is a random distribution, Hoeffding's D will reject the H0 for all datasets, wihch is that the two varialbes are independent.

.. image:: images/cor_heoffd1.png
   :align: center

Like the other two non-parametric methods, Hoeffding's D can handle both continuous and ordinal data. This algorithm can handle problems much broader than this software offering. Here is a good article discussing this algorithm. `LINK <https://github.com/Dicklesworthstone/hoeffdings_d_explainer/blob/main/README.md>`_

If we testing the data set above with Hoeffding's D, it will give a definite rejection to the null hypothesis. 


.. list-table::
   :widths: 33 67
   :class: tight-table

   * - .. image:: images/cor_outlier.png
     - .. code-block:: none

            ---- Hoeffding's D Correlation ----
            Hoeffding's D: 0.196
            Hoeffding's p-value: 0.000
            H0: The two variables are independent.

In another dataset from the `correlation.pickle` sample sets, the first and second columns show two linear relationships moving in different directions with random errors. Testing with the four correlations, only Hoeffding's D provided a p-value less than 0.05, rejecting the null hypothesis.


.. list-table::
   :widths: 33 67
   :class: tight-table

   * - .. image:: images/cor_heoffd2.png
     - .. code-block:: none

            ---- Spearman's rho Correlation ----
            Spearman's rho correlation: 0.103
            Spearman's rho p-value: 0.570

            ---- Kendall's tau Correlation ----
            Kendall's tau: 0.102
            Kendall's tau p-value: 0.415

            ---- Hoeffding's D Correlation ----
            Hoeffding's D: 0.043
            Hoeffding's D p-value: 0.019

            ---- Pearson correlation alpha = 0.050 ----
            Correlation coefficient: 0.204
            Confidence Interval (-0.150, 0.512)
            Covariance: 571.448
            p-value = 0.254 N = 33

In a dataset without any random errors, Hoeffding's D gives a higher D value and a much smaller p-value.

In general, Pearson's correlation is sufficient for most cases. Hoeffding's D is a great choice when complex relationships are involved and to determine the amount of random error within the datasets. Hoeffding's D value generally increases monotonically with stronger relationships between variables, which can be used as a measure of randomness.

- Hoeffding's D ranges from -0.5 to 1.
- A value of 0 indicates no association between the variables.
- As the strength of the association between two variables increases, the D value tends to increase as well.
- Positive values indicate a positive association.
- Negative values are rare and may indicate some form of negative association.
- Values closer to 1 suggest stronger associations.
