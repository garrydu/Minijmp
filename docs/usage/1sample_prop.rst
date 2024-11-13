.. raw:: html

   <style>
      .tight-table td {
             white-space: normal !important;
                       }
                          </style>

One Proportion Test
===================


Choose Stats> One Proportion Test

.. image:: images/1sample_prop1.png
   :align: center

- **Sample Values:** The column contains the sampled values. The values have to be categorical. The **Name of Event** should be the value of the state which is to be studied. The values do not have to be binary. But the event name should be consistent with the inputted value.
- **Summarized Data:** The input will override the **Sample Values** selected above. The **Number of Events** is the occurance of the state. The **Number of Trials** is the total number of the data. For example 250 products were made, while 9 out the 250 were defective. The **Number of Trials** should be 250, while the **Number of Events** should be 9. 
- **Hypothesized Proportion:** The hypothesized proportion, i.e. a number between 0 and 1, of the population to be tested.
- **Alpha:** Set the range of confidence intervals to be calculated, (1-alpha)100%. When alpha is set to 0.05, 95% confidence interval will be displayed.

The results contain two parts. The first is the replicate from Minitab 22, not version 20 as the most of the software did. The second part is the chi-square method that is available in JMP 17, while I didn't find the similar binomial proportion test in JMP.

The results have been calibrated to Minitab 22 and JMP 17 for the two parts separately.

.. code-block:: none
  ---- One sample propotion test ----
  
  p-value for H0: p==p0, H1: p!=p0
  Normal Approx.   0.025
  Strerne's Method 0.020
  Blaker's Method  0.020
  Adj. Blaker's Exact   0.021
  
  H0: p==p0, H1: p<p0.
  Normal Approx. p-value = 0.012
  Clopper-Pearson Exact p-value = 0.011
  
  H0: p==p0, H1: p>p0.
  Normal Approx. p-value = 0.988
  Clopper-Pearson Exact p-value = 0.995
  
  +-----+-------+----------------+
  |  N  | Event | Sample P Ratio |
  +-----+-------+----------------+
  | 250 |   9   |     0.036      |
  +-----+-------+----------------+
  P ratio CI of 95.00%
  +-----------------+----------------+-------------+-------------+
  |       Algo      |       CI       | Upper Bound | Lower Bound |
  +-----------------+----------------+-------------+-------------+
  |  Normal Approx. | (0.013, 0.059) |    0.055    |    0.017    |
  | Clopper-Pearson | (0.017, 0.067) |    0.062    |    0.019    |
  |   Blaker Adj.   | (0.018, 0.066) |      -      |      -      |
  +-----------------+----------------+-------------+-------------+
  Note: the results have been calibrated with Minitab 22, which 
  uses adjusted Blaker's exact method for H1 p!=p0, and Clopper-
  Pearson exact for H1 p>p0 and p<p0.

The first part that is aligned with Minitab 22 focuses in the binomial distribution and its approximation. You will be surprised that the methods to calculate confidence intervals of binomial distribution is still evolving in the 2020s. The methods to calculate p-value and confidence intervals with the alternative hypothesis population proportion is not equal to the hypothesized proportion are different in Minitab 22 and Minitab 20. Here we aligned with the version 22. Normal approximation is not available in the version 22, which has been aligned with the previous version.

The sample output above is about a discussion in a book of Kenji Kurogane. The question he raised is that one process step has defect rate of 7.3%. After a process change, there are 9 defected products in total 250. Has the new process reduced the defect rate? The book is a fairly old one. The book demonstrated using normal approximation to calculate the significance level. When a binomial sample set either has p <= 0.5 and np >= 5, or p >= 0.5 and (1-p)n >= 5, the distribution can be appropriated to a normal distribution. The normal approximation is easier for manual calculation.

Another category of methods is binomial exact methods. They use the discrete binomial distribution to calculate the results. The methods included except for normal approximation are all exact methods, such as Strerne's method, Blaker's method, Adjusted Blaker's exact and Clopper-Pearson Exact.

Sterne's and Blaker's methods were found to have coverage probabilities significantly closer to the nominal level (e.g., 0.95 for a 95% confidence interval) compared to other exact methods. Clopper-Pearson is known to be very conservative, often producing wider intervals than necessary. The adjusted Blaker exact method produces two-sided confidence intervals for the proportion of events and produces p-values for the alternative hypothesis of p ≠ p0. Blaker provides an exact, two-sided confidence interval by inverting the p-value function of an exact test. The Clopper-Pearson intervals are wider and always contain the Blaker confidence intervals. Intervals from the Blaker exact method are nested. This property means that confidence intervals with higher confidence levels contain confidence intervals with lower confidence levels. For example, an exact, two-sided Blaker 95% confidence interval contains the corresponding 90% confidence interval.

It's recommended to use the adjusted Blaker exact method's p-value and confidence intervals in the case of the alternative hypothesis is p != p0. For the alternative hypothesis (H1) being either p > p0 or p < p0, use the Clopper-Pearson Exact p-value and its upper / lower bounds.

.. code-block:: none

  ---- Chi square test ----
  df = 1
  +------------------+--------+-----------+
  |       Test       | Chi sq | P > ChiSq |
  +------------------+--------+-----------+
  | Likelihood Ratio | 6.139  |   0.013   |
  |     Pearson      | 5.057  |   0.025   |
  +------------------+--------+-----------+

In JMP 17, after plotting distribution of a categorical sample, `test proportion` can be selected in the red triangle. JMP uses chi-square method, which is an approximation method. The method works better with large size of sample and is compatible to more than two types of states in the sample. Minitab's binomial exact methods are more accurate for small samples, but are limited with binary states.

The p-value here is the `P > ChiSq` value. The null hypothesis is p == p0, while the alternative hypothesis is p != p0.


