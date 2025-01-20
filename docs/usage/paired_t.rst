Paired t-test
=============


Choose Stats > Paired t-test

.. image:: images/paired_t1.png
   :align: center


- **Sample Values:** The columns that contain the sampled values. The values have to be numerical and continuous. For this test, the order of the data matters. The values of one pair should be in the same row. Any row that does not contain two valid values will be ingored. 
- **Hypothesized mean of the differences:** TSpecify the hypothesized mean of the differences between each pair of values (Sample 1 - Sample 2). For instance, to test for changes before and after a process, set this value to zero, indicating the null hypothesis of no change between the two stages.
- **Alpha:** Define the significance level for the calculation. For example, for confidence intervals, the range is (1-alpha)100%.

The results were aligned with JMP 17 and Minitab 20.

Sample Output:

.. code-block:: none

  ---- Paired t test ----
  Hypothesized mean of the differences u0 = 0.000
  Paired difference (Sample 1 - Sample 2):
  mean (ud) = 0.222
  SD = 1.671
  t = 0.596
  df = 19.000
  n = 20
  H0: ud == u0, H1: ud != u0, p = 0.558
  95.00% range of the difference's mean: (-0.559, 1.004)
  H0: u == u0, H1: ud > u0, p value = 0.279
  95.00% Lower bound of difference's mean: -0.423
  H0: u == u0, H1: ud < u0, p value = 0.721
  95.00% Upper bound of difference's mean: 0.868

In a paired t-test, the differences between each pair are calculated first. These differences are then used as a dataset to perform a one-sample t-test with the hypothesized mean difference. The output mean and standard deviation are statistics of these differences. If uncertain, refer to the first set of null hypotheses, where the alternative hypothesis is that the difference mean is not equal to the hypothesized mean. In the example above, with a p-value of 0.558, the null hypothesis cannot be rejected, indicating no significant difference between the two stages.


