.. raw:: html

   <style>
      .tight-table td {
             white-space: normal !important;
                       }
                          </style>

Process Capability with Subgroups
---------------------------------

A process capability study evaluates whether a manufacturing process can consistently produce outputs within specified tolerance limits by analyzing indices like Cp, Cpk, and Cpm. The study with Subgroups focuses on the measurement with different lot, shift, equipment or operators etc. The study will show the repeatability within these Subgroups, for example repeatability of the day shift instead of the overall production line.

To perform the study choose Quality > Process Capability with Subgroups

.. image:: images/cpk_sub1.png
   :align: center


- **Measurement**: The column containing the measurement result. The values must be numerical and continuous. The caculation assumes the data following normal distribution. Nonnormal distribution evaluation is not available yet.
- **Spec Limits**: To perform the analysis, you must specify a lower (LSL) and upper (USL) specification limit to define your process requirements. Target of the process can also be specified. When leaving the Target value zero, the software will use the mean of LSL and USL as the target. 
- **Subgroup**: Set the method to categorize the measurement data into Subgroups.

  - **Option 1: Use Subgroup Size**: Select **Use Subgroup Size** in **Option**, and set the size of each group in **Subgroup Size**. In this case each sub group has to have the same number of sample points. Each sub group will be extracted from the pool sequentially.
  - **Option 2: Use Subgroup ID**: In this case, there shall be a column containing the categorical data for the measurement data points. Select **Use Subgroup ID Col.** in **Option**, and select the column in **ID Col.**. The setting in **Subgroup Size** will be ignored in this case, and vise versa. 

- **Within Subgroup Variation**: Select the **Method** to estimate the within Subgroup sigma.
  
  - **Unbiased Std Dev**: Use the average of the standard deviation of each sub group divided by its C4 value. Same as `Average of Unbiased Std Dev` in JMP and `Sbar` in Minitab.
  - **Ranges**: The approach uses range of each group divided by its d2 value to estimate the underlying data population. The approach is more sensitive to outliers. Same as `Average of Range` in JMP and `Rbar` in Minitab.
  - **Pooled Std Dev**: Pool the variation of all subgroups into one standard deviation, divided by C4. This is the default method of Minitab. JMP does not offer it.

  A subgroup with a single value has no within subgroup variation. It is left out of the within sigma, but its value is still used in N, the mean and the overall sigma. The output notes how many subgroups were left out. At least one subgroup must have 2 or more values.

- **Plot Settings**:
  
  - **X Label**: Customize the label of x axis. By default, the software will use the column name of the measurement input.
  - **Show Spec Limits**: Show vertical lines to mark the USL, LSL and Target in the plot. 
  - **Show Legend**: Legend of the curves of the overall and within distribution fitting.

- **Alpha**: Set confidence interval range. For example CI range will be 95% when alpha is 0.05.


The result aligns with JMP 17. See `Calculation Details and Comparison with JMP and Minitab` at the end of this page for the formulas and where JMP and Minitab differ.


The plot below demenstrates the result from the data set `CPK_sample.pickle` in the sample data folder. Select `Measurement` with column `Y`. Set the LSL, USL and Target to 17, 23 and 20. Select `Subgroup` with `Use Subgroup ID` and column `Lot` as the Subgroup ID. Keep the `Within Subgroup Variation` as `Unbiased SD` unchanged.


.. image:: images/cpk_sub2.png
   :align: center


The plot contains the histogram of the data and the normal distribution fit. The histogram bar charts uses the Y axis on the right hand side, which showing the counts of the data poionts falling into each bin. The normal distribution fit curve uses the Y axis on the left hand side, which is the probability density. In the meanwhile the probability density axis is also used by the histogram, it demonstrates the integrated probability of each bin. The narrower curve is the normal distribution fit of the within sigma. It shows the inner subgroup process capability regardless the inter subgroup difference. 



.. code:: none
  
  ---- Process Capabilities ----
  LSL = 17.000
  USL = 23.000
  Target = 20.000
  mean = 20.397
  Within Sigma = 1.052
  Overall Sigma = 1.475
  N = 32
  N Subgroups = 8
  Stability Index = 1.402
  Within sigma estimated by the average of unbiased SD.
  
  Within
  +-------+----------+--------------+--------------+
  | Index | Estimate | Lower 95.00% | Upper 95.00% |
  +-------+----------+--------------+--------------+
  |  Cpk  |  0.825   |    0.558     |    1.092     |
  |  Cpl  |  1.077   |    0.742     |    1.408     |
  |  Cpu  |  0.825   |    0.557     |    1.089     |
  |   Cp  |  0.951   |    0.675     |    1.227     |
  |  Cpm  |  0.890   |    0.674     |    1.104     |
  +-------+----------+--------------+--------------+
  
  Overall (AKA Ppk in JMP)
  +-------+----------+--------------+--------------+
  | Index | Estimate | Lower 95.00% | Upper 95.00% |
  +-------+----------+--------------+--------------+
  |  Cpk  |  0.588   |    0.402     |    0.775     |
  |  Cpl  |  0.768   |    0.543     |    0.988     |
  |  Cpu  |  0.588   |    0.400     |    0.772     |
  |   Cp  |  0.678   |    0.510     |    0.846     |
  |  Cpm  |  0.655   |    0.503     |    0.826     |
  +-------+----------+--------------+--------------+
  
  Nonconformance (Observation and Expected)
  +-----------+-----------+------------------+-------------------+
  |  Portion  | Observed% | Expected Within% | Expected Overall% |
  +-----------+-----------+------------------+-------------------+
  | Below LSL |    3.12   |       0.06       |        1.06       |
  | Above USL |    3.12   |       0.67       |        3.88       |
  | Total Out |    6.25   |       0.73       |        4.94       |
  +-----------+-----------+------------------+-------------------+
  

The first part of the numerical prints includes general information of the study. The `Overall Sigma` is the standard deviation of the sample data. `N subgroups` is the number of subgroups. 

`Stability Index` is a measure of stability of the process. A stable process has a stability index near one. Higher values indicate less stability. The stability index is defined as follows: (Overall Sigma / Within Sigma). In the ideal case without any inter subgroup difference, the index shall be 1. In real practics, the index is greater than one, but the less the better.

All the indices in the study are same to the previous session, but including the within subgroup indices. The overall Cpk is also called as Ppk, for example in Minitab, while the overall Cpk or Ppk uses the overall sigma that is the standard deviation of all the sample points. This difference applies to all other capability indices too.

.. image:: images/cpk_ppk_formulas_w640.png
   :align: center

Using subgroup data is always a good approach to understand the process potential, by removing one source of variation, which is the grouping factor. For example, a data set having subgrouping via equipment, if the result of within subgroup is much better than the overall result, demonstrates that the process repeatability can be improved by using less equipment, or reducing the inter equipment difference.

Here is a hyperthetical example of within subgroup capability VS the overall capability.


.. image:: images/similar_cpk_ppk.png
   :align: center

Hyperthetically let's say the data were grouped by lots. As illustrated in the left-side graph, the shift and drift between subgroups are minimal compared to the variation within the subgroups themselves. Consequently, the within-subgroup and overall standard deviations are nearly identical, resulting in closely matched within Cpk and overall Cpk values (1.13 and 1.07, respectively). [ref. `LINK <https://blog.minitab.com/en/process-capability-statistics-cpk-vs-ppk>`_]
   
.. image:: images/different_cpk_ppk.png
   :align: center

But if the same data points were regrouped, for example by operators, the within within subgroup Cpk can go up to 3.7. Using within subgroup indices helped to identify the main variation source of the process is operators. Potentially more training or alignment of their workstation may improve the overall process capability.

In the previous session, when the data do not have any subgrouping, a moving window can still be applied to a sequentially recorded data set for within sigma. The algorithm uses the pairs of neighor data points as the subgroups. It assumes the production condition and environment change less during a short of period time. But if over the entire time span the condition drifts much, the within indices will be much better than the overall indices. In this case, a control chart will come to handy for further process drifting analysis, which will be discussed in the next session.


Calculation Details and Comparison with JMP and Minitab
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

JMP and Minitab use mostly the same formulas, but differ in a few places. MiniJMP follows JMP by default. The table below lists each statistic, how MiniJMP calculates it, and whether the result matches JMP and Minitab. "Same" in the JMP column comes from the original calibration against JMP 17 and later checks against JMP 19. The Minitab column comes from the Minitab help pages below and from comparing results in Minitab; items not covered by either are noted.

References:

- JMP: `Statistical Details for Capability Indices for Normal Distributions <https://www.jmp.com/support/help/en/19.0/index.shtml#page/jmp/statistical-details-for-capability-indices-for-normal-distributions.shtml>`_
- Minitab: `Methods and formulas for overall capability <https://support.minitab.com/en-us/minitab/help-and-how-to/quality-and-process-improvement/capability-analysis/how-to/capability-analysis/normal-capability-analysis/methods-and-formulas/overall-capability/>`_ and `potential (within) capability <https://support.minitab.com/en-us/minitab/help-and-how-to/quality-and-process-improvement/capability-analysis/how-to/capability-analysis/normal-capability-analysis/methods-and-formulas/potential-capability/>`_

Notation: :math:`N` is the number of observations, :math:`\bar{x}` the mean, :math:`s` the sample standard deviation (N-1), :math:`T` the target, :math:`n_i` the size of subgroup i, :math:`s_i` and :math:`R_i` its standard deviation and range, and :math:`k` the number of subgroups.

**Sigma estimates**

.. list-table::
   :header-rows: 1
   :widths: 22 38 20 20
   :class: tight-table

   * - Statistic
     - MiniJMP
     - JMP
     - Minitab
   * - Overall sigma
     - :math:`s`
     - Same
     - Same (default, without the unbiasing constant)
   * - Within sigma, no subgroups
     - Average moving range of length 2 / d2(2), d2(2) = 1.128379
     - Same
     - Uses d2(2) = 1.128, so slightly larger (16.2844 vs 16.2899 in one example). Minitab also offers other moving range lengths.
   * - Within sigma, Unbiased Std Dev
     - :math:`\frac{1}{k}\sum s_i / c_4(n_i)`
     - Same (Average of Unbiased Std Dev)
     - Same as the Sbar option when subgroups have equal size
   * - Within sigma, Ranges
     - :math:`\frac{1}{k}\sum R_i / d_2(n_i)`
     - Same (Average of Range)
     - Same as the Rbar option when subgroups have equal size
   * - Within sigma, Pooled Std Dev
     - :math:`s_p / c_4(d+1)`, :math:`s_p = \sqrt{\sum\sum (x_{ij}-\bar{x}_i)^2 / d}`, :math:`d = \sum (n_i - 1)`
     - Not available
     - Same (Minitab default)

**Capability indices**

Cp, Cpk, Cpl and Cpu use the standard formulas (shown above) in all three programs. The within indices use the within sigma, and the overall indices (Pp, Ppk, Ppl, Ppu in Minitab) use the overall sigma.

Cpm differs:

- MiniJMP and JMP:

  .. math::

     Cpm = \frac{\min(T - LSL, USL - T)}{3\sqrt{\sigma^2 + (\bar{x} - T)^2}}

  with :math:`\sigma` = overall or within sigma.

- Minitab (overall only, no within Cpm):

  .. math::

     Cpm = \frac{\min(T - LSL, USL - T)}{3\sqrt{\sum (x_i - T)^2 / N}}

  This divides by N instead of N-1, so for small samples Minitab shows a larger Cpm (for example 0.48 vs 0.462 with N = 9).

**Confidence intervals**

.. list-table::
   :header-rows: 1
   :widths: 22 38 20 20
   :class: tight-table

   * - Statistic
     - MiniJMP
     - JMP
     - Minitab
   * - Cp
     - Chi-square: :math:`Cp\sqrt{\chi^2_{\alpha/2,\nu}/\nu}` to :math:`Cp\sqrt{\chi^2_{1-\alpha/2,\nu}/\nu}`
     - Same
     - Same formula, see the degrees of freedom below
   * - Cpk
     - Normal approximation: :math:`Cpk \pm z_{1-\alpha/2}\sqrt{\frac{1}{9N} + \frac{Cpk^2}{2\nu}}`
     - Same
     - Overall interval matched in our test. Within interval differs (0.02 to 0.54 in Minitab vs 0.001 to 0.559 in JMP and MiniJMP for one example).
   * - Cpl, Cpu
     - Based on the noncentral t distribution
     - Same
     - Not reported
   * - Cpm
     - Chi-square with :math:`\gamma = N\frac{(1+a^2)^2}{1+2a^2}`, :math:`a = (\bar{x}-T)/\sigma`. Overall interval is centered on :math:`Cpm_2 = \frac{USL-LSL}{6\sqrt{\frac{N-1}{N}s^2 + (T-\bar{x})^2}}`; within interval is centered on Cpm. Only shown when the target is the middle of LSL and USL.
     - Same
     - Overall interval is the same. No within interval.

Degrees of freedom :math:`\nu` used by the Cp and Cpk intervals:

.. list-table::
   :header-rows: 1
   :widths: 30 30 20 20
   :class: tight-table

   * - Sigma
     - MiniJMP
     - JMP
     - Minitab
   * - Overall
     - :math:`N - 1`
     - Same
     - Same
   * - Within, no subgroups
     - :math:`0.62(N - 1)`
     - Same
     - :math:`N - 1`, so Minitab gives a narrower within interval
   * - Within, Unbiased Std Dev
     - :math:`f_n \sum (n_i - 1)` for equal sizes, :math:`\sum (n_i - 1)` otherwise
     - Same
     - Same for equal sizes (Sbar)
   * - Within, Ranges
     - Approximation from d2 and d3 for equal sizes, :math:`\sum (n_i - 1)` otherwise
     - Same
     - Minitab uses :math:`0.9k(n-1)`
   * - Within, Pooled Std Dev
     - :math:`\sum (n_i - 1)`
     - Not available
     - Same

**Nonconformance**

The expected percentages outside the spec limits come from the normal distribution with the mean and the within or overall sigma. JMP and Minitab calculate them the same way (Minitab reports them as PPM).

**Summary of differences from Minitab**

When you compare MiniJMP results with Minitab, expect differences in these places only:

- Minitab's default within sigma is Pooled Std Dev. Choose `Pooled Std Dev` in MiniJMP to get the same within sigma.
- Minitab's Cpm uses N instead of N-1, so its Cpm point estimate is larger for small samples. The overall Cpm interval is the same.
- The within Cpk interval, and the within Cp interval without subgroups, use different formulas or degrees of freedom.
- Without subgroups, Minitab uses d2(2) = 1.128 instead of 1.128379.
