.. raw:: html

   <style>
      .tight-table td {
             white-space: normal !important;
                       }
                          </style>

One Sample Mean Z-test
======================

Choose Stats> One Sample Mean Z-test

.. image:: images/1sample_z1.png
   :align: center

- **Sample Values:** The column contains the sampled values. The values have to be numerical of continuous values. 
- **Summarized Data:** When knowing the statistical descriptions of the sampled values, filling out N, which is the count of the sampled values, and mean. The filled information will override the sampled values selected above. 
- **Hypothesis Test:** The hypothesized mean value of the population. The value has to be inputted.
- **Known Values:** The known population standard deviation. The value has to be inputted. 
- **Alpha:** The significance level used in the calculation. For example the confidence intervals, the range of confidence intervals is (1-alpha)100%.


.. list-table:: Comparison of Z-test and t-test
   :header-rows: 1
   :class: tight-table

   * - Aspect
     - Z-test
     - T-test
   * - Population standard deviation
     - Known
     - Unknown, estimated from sample
   * - Sample size
     - Typically larger (>30)
     - Often smaller (<30)
   * - Distribution
     - Standard normal (z-distribution)
     - t-distribution (varies with degrees of freedom)
   * - Formula
     - :math:`z = \frac{\bar{x} - \mu}{\sigma / \sqrt{n}}`
     - :math:`t = \frac{\bar{x} - \mu}{s / \sqrt{n}}`
   * - Robustness
     - Assumes normal distribution
     - More robust to slight deviations from normality
   * - Degrees of freedom
     - Not used
     - Used, affects t-distribution shape
   * - Practical use
     - Less common (population σ rarely known)
     - More common in real-world applications

A sample output:

.. code-block:: none

  ---- One sample Z ----
  mean = 1.178
  z = -2.880
  df = 19.000
  u0 = 1.500
  Known StDev = 0.500
  Two-tailed test H0: u==u0, H1 u!=u0: p = 0.004
  P-value is the prob of that population mean equals 
  the specified value, which the samples came from.
  95.00% range of population mean which the samples 
  came from: (0.959, 1.397)
  H0 u==u0, H1 u>u0 p value = 0.998
  95.00% Lower bound of population mean: 0.994
  H0 u==u0, H1 u<u0 p value = 0.002
  95.00% Upper bound of population mean: 1.362
  

- Hypotheses: Null hypothesis (H0): The population mean (estimated by the sample mean) is equal to the specified value. Alternative hypothesis (H1): The population mean is different from the specified value.
- When P-value is smaller than the significance level, the null hypothesis should be rejected. Or in another way, the p-value is the probability the population mean equals to the hypothesized population mean.
- The confidence intervals of the population mean, the percentage size of the range is set by alpha.
- In a t-test, the null hypothesis (H0) and alternative hypothesis (H1) can indeed be formulated as you described, with H0: μ = μ0 and H1: μ > μ0. This is known as a one-tailed or directional test. If H0 is rejected, we accept that the true mean is greater than μ0, which is precisely what H1 states.


