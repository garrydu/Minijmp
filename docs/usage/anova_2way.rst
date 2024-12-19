Two-Way ANOVA
=============

Choose Stats> Two-Way ANOVA

.. image:: images/anova_2way1.png
   :align: center

- **Factors:** These are the independent categorical variables in columns. The data must be stacked and can be either text or numerical.
- **Response:** This is the dependent numerical variable in its column. It must be a quantitative variable representing amounts or counts, which can be divided to find a group mean. 

The Two-Way ANOVA results are consistent with both JMP 17 and Minitab 22. Note that the Two-Way ANOVA does not have a standalone menu entry in these two software packages but can be performed using general linear models with least squares methods.

.. code-block:: none

  ---- Two Way ANOVA With
  +----------+--------+
  |  Factor  | Levels |
  +----------+--------+
  | Operator |   3    |
  |   Part   |   5    |
  +----------+--------+
  
  Analysis of Variance
  +---------------+----+-----------+----------+---------+---------+
  |     Source    | DF |   Adj SS  |  Adj MS  | F-value | p-value |
  +---------------+----+-----------+----------+---------+---------+
  |    Operator   | 2  |  415.400  | 207.700  |  17.025 |  0.000  |
  |      Part     | 4  | 12791.133 | 3197.783 | 262.113 |  0.000  |
  | Operator*Part | 8  |  103.267  |  12.908  |  1.058  |  0.439  |
  |     Error     | 15 |  183.000  |  12.200  |         |         |
  |     Total     | 29 | 13492.800 |          |         |         |
  +---------------+----+-----------+----------+---------+---------+


This example analyzes the sample data from `gasket.pickle`, selecting the Y column as the response data column, and the `Part` and `Operator` columns as the factors. A two-way ANOVA with interaction tests three null hypotheses simultaneously:

- There is no difference in group means at any level of the first independent variable.
- There is no difference in group means at any level of the second independent variable.
- The effect of one independent variable does not depend on the effect of the other independent variable (a.k.a. No interaction effect).
 

The first two null hypotheses are straightforward, similar to one-way ANOVA. The third null hypothesis tests the interaction between the two factors. For example, in the dataset above, where operators measure different parts, one or two operators may handle large parts poorly, resulting in significant offsets in the results.

In the sample above, both independent factors significantly impact the group mean, while the interaction of the two factors does not. However, if we compare the one-way ANOVA result here `LINK <https://minijmp.readthedocs.io/en/latest/usage/anova_1way.html>`_, the one-Way ANOVA result did not reject the null hypothesis that the operator impacts mean values, with a p-value of 0.6. In contrast, in the Two-Way ANOVA example, its p-value is much smaller.

This should be explained by the algorithm of ANOVA. The p-value is determined by an F distribution with the F-value and the degrees of freedom of the factor and error. In one-Way ANOVA the error is the row of `Within`. The F-value is ratio between adjusted mean square of the factor and error. The total square sum of the system is identical in one-Way ANOVA and Two-Way ANOVA, while the square sum of the `Operator` factor is same too. In one-Way ANOVA, all the rest of square sum of the variation except for the `Operator` was counted into error. In Two-Way ANOVA, after the factor of `Part` and interaction were considered, the square sum of the error became much smaller. 

In simple terms, the variation between parts was counted as the operators' measurement error, making the variation of one operator's results larger than the variation between the operators. Therefore, it is important in the design of the experiment to include more controllable factors rather than counting their impacts as errors.

