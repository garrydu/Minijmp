One Sample Standard Deviation Test
==================================

Choose Stats> One Sample SD

.. image:: images/1sample_dev1.png
   :align: center


- **Sample Values:** This column contains the sampled values, which must be numerical and continuous. 
- **Summarized Data:** If you know the statistical descriptions of the sampled values, fill in `N`, the count of the sampled values, and `Std Dev`, the standard deviation of the sampled values. This information will override the sampled values selected above.
- **Hypothesis Test:** The hypothesized standard deviation value of the population.
- **Alpha:** The significance level used in the calculation. For example, the confidence intervals are calculated as (1-alpha)100%.

Many statistical methods have been developed to evaluate the variance of a population, each with its own strengths and limitations. The classical chi-square method is likely the most commonly used for testing variance, but it is extremely sensitive to the assumption of normality and can produce inaccurate results when the data are skewed or heavy-tailed. It is advisable to test the data for normality before using the chi-square test for variance or standard deviation. The software also provides the Bonett method to test the hypothesis; however, it requires a data set input and will not work with summarized values inputs.

The test is not designed to assess whether the standard deviation of the data set itself is equal to another hypothesized value. Similar to mean tests, the purpose is to determine the significance level of the population standard deviation being equal to the hypothesized value.

The calculation was calibrated with Minitab 20.

A sample output:

.. code-block:: none

  ---- 1 sample standard deviation test ----
  N = 20  SD: s = 0.957
  s0 = 1.000
  +-------------------+----------------+----------------+
  |                   |     Chi Sq     |     Bonett     |
  +-------------------+----------------+----------------+
  |     P-value *     |     0.874      |     0.822      |
  |   SD CI 95.0%     | (0.728, 1.398) | (0.699, 1.453) |
  | 95.0% upper bound |     1.311      |     1.351      |
  | 95.0% lower bound |     0.760      |     0.739      |
  +-------------------+----------------+----------------+
  * H0 s==s0, H1 s!=s0
  The Bonett method is valid for any continuous distribution.
  The chi-square method is valid only for the normal distribution.

The null hypothesis of the test is that the population standard deviation is equal to the specified value from which the dataset was sampled. The chi-square method requires a normal distribution, while the Bonett method requires a continuous distribution but is not limited to normal distribution. If the dataset does not show significance in the normality test, use the p-value from the Bonett test.

The confidence intervals represent the range of the population standard deviation at a certain probability. The range is set by alpha, with the percentage being (1-alpha)100%. For example, the upper boundary indicates the percentage probability that the population standard deviation will be less than the value, similar to the lower boundary.

